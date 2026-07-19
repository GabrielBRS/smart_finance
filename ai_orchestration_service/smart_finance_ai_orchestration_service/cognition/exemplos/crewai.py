import asyncio

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

from cognition.exemplos.config import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY

llm = LLM(model=f"openai/{LLM_MODEL}", base_url=LLM_BASE_URL, api_key=LLM_API_KEY)

# CrewAI é síncrono. As dependências (embedder/vectors/repo) precisam estar
# acessíveis aqui — o padrão limpo é injetá-las via um setter chamado no lifespan.
_deps: dict = {}


def configure(embedder, vectors, repo) -> None:
    _deps.update(embedder=embedder, vectors=vectors, repo=repo)


@tool("recuperar_contexto")
def recuperar(question: str) -> str:
    """Busca contexto financeiro no acervo Smart-Finance."""
    from cognition.exemplos.retrieval import retrieve
    return asyncio.run(retrieve(question, _deps["embedder"], _deps["vectors"], _deps["repo"]))


pesquisador = Agent(
    role="Pesquisador Financeiro",
    goal="Recuperar o contexto mais relevante para a pergunta",
    backstory="Especialista em achar a fonte certa no acervo.",
    tools=[recuperar], llm=llm,
)
analista = Agent(
    role="Analista Financeiro",
    goal="Sintetizar uma resposta objetiva e ancorada nas fontes",
    backstory="Especialista em conciliação e regras fiscais.",
    llm=llm,
)


def run_crew(question: str) -> str:
    t1 = Task(description=f"Recupere contexto para: {question}", agent=pesquisador,
              expected_output="Trechos relevantes com a fonte.")
    t2 = Task(description="Responda com base no contexto recuperado.", agent=analista,
              expected_output="Resposta final ancorada.", context=[t1])
    return Crew(agents=[pesquisador, analista], tasks=[t1, t2]).kickoff().raw