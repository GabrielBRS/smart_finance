# cognition/lang_graph.py
#
# Grafo LINEAR de RAG (retrieve -> generate). O multi-agente vive em multi_agent.py.
# embedder/vectors/repo NAO sao pacotes PyPI: sao as TUAS portas (cognition.ports),
# injetadas na montagem — mesma convencao do build_multi_agent.
from functools import partial
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from cognition.exemplos.agent import SYSTEM_PROMPT
from cognition.exemplos.config import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY
from cognition.exemplos.ports import EmbeddingPort, VectorStore, DocumentRepository

llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL,
                 api_key=LLM_API_KEY, temperature=0.2)


class State(TypedDict, total=False):
    question: str
    context: str
    answer: str


async def node_retrieve(state: State, *, embedder, vectors, repo) -> dict:
    vec = await embedder.embed(state["question"])
    chunks = await vectors.search(vec, top_k=5)
    records = await repo.fetch_by_ids([c.id for c in chunks])
    context = "\n\n".join(f"[{r['source']}] {r['content']}" for r in records)
    return {"context": context}


async def node_generate(state: State) -> dict:
    msgs = [
        ("system", SYSTEM_PROMPT),
        ("system", f"Contexto recuperado:\n{state['context']}"),
        ("user", state["question"]),
    ]
    resp = await llm.ainvoke(msgs)
    return {"answer": resp.content}


def build_graph(embedder: EmbeddingPort,
                vectors: VectorStore,
                repo: DocumentRepository):
    """Compila UMA vez. Chame no lifespan e guarde em app.state.rag_graph."""
    return (
        StateGraph(State)
        .add_node("retrieve",
                  partial(node_retrieve, embedder=embedder, vectors=vectors, repo=repo))
        .add_node("generate", node_generate)
        .add_edge(START, "retrieve")
        .add_edge("retrieve", "generate")
        .add_edge("generate", END)
        .compile()
    )


async def run_langgraph(question: str, graph) -> str:
    result = await graph.ainvoke({"question": question})
    return result["answer"]