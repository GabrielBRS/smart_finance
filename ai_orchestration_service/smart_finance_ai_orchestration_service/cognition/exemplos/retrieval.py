from functools import partial
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from cognition.exemplos.agent import SYSTEM_PROMPT
from cognition.exemplos.config import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY
from cognition.exemplos.ports import EmbeddingPort, VectorStore, DocumentRepository

llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL, api_key=LLM_API_KEY, temperature=0.2)


async def retrieve(question: str, embedder: EmbeddingPort,
                   vectors: VectorStore, repo: DocumentRepository) -> str:
    vec = await embedder.embed(question)
    chunks = await vectors.search(vec, top_k=5)
    records = await repo.fetch_by_ids([c.id for c in chunks])
    return "\n\n".join(f"[{r['source']}] {r['content']}" for r in records)


class State(TypedDict):
    question: str
    context: str
    answer: str


async def node_retrieve(state: State, *, embedder, vectors, repo) -> dict:
    ctx = await retrieve(state["question"], embedder, vectors, repo)
    return {"context": ctx}


async def node_generate(state: State) -> dict:
    msgs = [
        ("system", SYSTEM_PROMPT),
        ("system", f"Contexto recuperado:\n{state['context']}"),
        ("user", state["question"]),
    ]
    resp = await llm.ainvoke(msgs)
    return {"answer": resp.content}


def build_graph(embedder, vectors, repo):
    return (
        StateGraph(State)
        .add_node("retrieve", partial(node_retrieve, embedder=embedder, vectors=vectors, repo=repo))
        .add_node("generate", node_generate)
        .add_edge(START, "retrieve")
        .add_edge("retrieve", "generate")
        .add_edge("generate", END)
        .compile()
    )


async def run_langchain(question: str, embedder, vectors, repo) -> str:
    from cognition.exemplos.lang_chain import chain
    context = await retrieve(question, embedder, vectors, repo)
    return await chain.ainvoke({"context": context, "question": question})