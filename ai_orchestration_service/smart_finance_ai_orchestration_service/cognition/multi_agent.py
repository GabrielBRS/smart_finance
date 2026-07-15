# cognition/multi_agent.py
#
# Multi-agente EM LangGraph (o framework de multi-agente do ecossistema LangChain),
# nao em CrewAI. Tres papeis especializados compartilhando um State, com um
# gate condicional que fecha o loop de revisao:
#
#   pesquisador  -> planeja a consulta e RECUPERA via tuas portas (embedder/vectors/repo)
#   analista     -> redige a resposta ANCORADA no contexto recuperado
#   revisor      -> checa se a resposta esta grounded; se nao, devolve pro analista
#
# Nada de gpt-4o: a LLM e a local (Nemotron no Triton, 192.168.15.201) via base_url.
#
# CORRECAO: o grafo e COMPILADO UMA VEZ (build_multi_agent) e reusado. O antigo
# run_multi_agent recompilava a cada chamada; agora ele recebe o grafo ja pronto.
# Em producao o grafo vive em app.state.multi_graph (compilado no lifespan).
from functools import partial
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from cognition.agent import SYSTEM_PROMPT
from cognition.config import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY
from cognition.retrieval import retrieve
from cognition.ports import EmbeddingPort, VectorStore, DocumentRepository

# LLM local (on-prem). Mesma convencao do teu lang_graph.py / retrieval.py.
llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL,
                 api_key=LLM_API_KEY, temperature=0.2)

MAX_REVISOES = 2  # teto de passes do analista; evita loop infinito com o gate


class State(TypedDict, total=False):
    question: str
    search_query: str
    context: str
    answer: str
    critique: str
    grounded: bool
    revisions: int


# --- Agente 1: Pesquisador --------------------------------------------------
# Diferente do node_retrieve linear: aqui ele PLANEJA a consulta antes de
# buscar (comportamento de agente, melhora recall no acervo fiscal), depois
# recupera reusando teu retrieve() -- que ja passa por Milvus + Postgres.
PROMPT_PESQUISADOR = (
    "Voce e o Pesquisador Financeiro do Smart-Finance. "
    "Reescreva a pergunta do usuario como UMA consulta de busca objetiva, "
    "usando os termos tecnicos/fiscais mais relevantes para recuperar documentos. "
    "Responda apenas com a consulta, sem explicacoes."
)


async def node_pesquisador(state: State, *, embedder, vectors, repo) -> dict:
    plan = await llm.ainvoke([
        ("system", PROMPT_PESQUISADOR),
        ("user", state["question"]),
    ])
    query = (plan.content or "").strip() or state["question"]
    context = await retrieve(query, embedder, vectors, repo)
    return {"search_query": query, "context": context}


# --- Agente 2: Analista -----------------------------------------------------
# Redige a resposta ancorada. Se o revisor devolveu uma critica, refaz
# corrigindo -- e aqui que o loop de qualidade acontece.
async def node_analista(state: State) -> dict:
    msgs = [
        ("system", SYSTEM_PROMPT),
        ("system", f"Contexto recuperado:\n{state['context']}"),
    ]
    if state.get("critique"):
        msgs.append(("system",
                     f"Revise sua resposta anterior corrigindo estes pontos: {state['critique']}"))
    msgs.append(("user", state["question"]))

    resp = await llm.ainvoke(msgs)
    return {"answer": resp.content, "revisions": state.get("revisions", 0) + 1}


# --- Agente 3: Revisor de Conformidade --------------------------------------
# O papel que o teu dominio fiscal exige: auditar se a resposta esta inteiramente
# suportada pelas fontes. Sem ele, "multi-agente" vira so mais chamadas de LLM.
PROMPT_REVISOR = (
    "Voce e o Revisor de Conformidade do Smart-Finance. "
    "Verifique se a RESPOSTA esta inteiramente ancorada no CONTEXTO fornecido, "
    "sem afirmacoes inventadas ou nao suportadas pelas fontes. "
    "Responda SOMENTE com JSON, sem markdown: "
    '{"grounded": true|false, "critique": "o que corrigir, ou string vazia"}'
)


async def node_revisor(state: State) -> dict:
    import json

    resp = await llm.ainvoke([
        ("system", PROMPT_REVISOR),
        ("user", f"CONTEXTO:\n{state['context']}\n\nRESPOSTA:\n{state['answer']}"),
    ])
    raw = (resp.content or "").strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        verdict = json.loads(raw)
        grounded = bool(verdict.get("grounded", True))
        critique = (verdict.get("critique") or "").strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        # Modelo local nem sempre devolve JSON limpo: no fail-open nao travamos
        # o fluxo, mas voce pode trocar para fail-closed se auditoria for critica.
        grounded, critique = True, ""
    return {"grounded": grounded, "critique": critique}


def gate(state: State) -> str:
    """Revisor aprovou OU esgotou os passes -> encerra; senao, volta ao analista."""
    if state.get("grounded", True) or state.get("revisions", 0) >= MAX_REVISOES:
        return END
    return "analista"


# --- Montagem do grafo (mesma convencao do teu build_graph em lang_graph.py) -
def build_multi_agent(embedder: EmbeddingPort,
                      vectors: VectorStore,
                      repo: DocumentRepository):
    """Compila o grafo UMA vez. Chame no lifespan e guarde em app.state."""
    return (
        StateGraph(State)
        .add_node("pesquisador",
                  partial(node_pesquisador, embedder=embedder, vectors=vectors, repo=repo))
        .add_node("analista", node_analista)
        .add_node("revisor", node_revisor)
        .add_edge(START, "pesquisador")
        .add_edge("pesquisador", "analista")
        .add_edge("analista", "revisor")
        .add_conditional_edges("revisor", gate, {"analista": "analista", END: END})
        .compile()
    )


async def run_multi_agent(question: str, graph) -> str:
    """Invoca um grafo JA COMPILADO (recebido de fora). Nao recompila.

    Em producao, prefira chamar graph.ainvoke direto na rota (ver /chat-multiagent
    em main.py). Este helper existe para uso em scripts/testes.
    """
    result = await graph.ainvoke({"question": question, "revisions": 0, "critique": ""})
    return result["answer"]