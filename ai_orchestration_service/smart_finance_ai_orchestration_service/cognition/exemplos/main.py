# main.py

import os
from contextlib import asynccontextmanager

import httpx
import asyncpg
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pymilvus import AsyncMilvusClient

from cognition.exemplos.adapters import TritonLLM, TritonEmbedder
from cognition.exemplos.agent import CognitionAgent
from cognition.exemplos.config import LLM_BASE_URL, LLM_MODEL, EMBED_MODEL
from cognition.exemplos.multi_agent import build_multi_agent
from cognition.exemplos.repositories import PostgresRepository
from cognition.exemplos.retrieval import run_langchain, build_graph
from cognition.exemplos.schemas import ChatRequest, ChatResponse
from cognition.exemplos.vectorstores import MilvusVectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient(base_url=LLM_BASE_URL, timeout=httpx.Timeout(60.0, connect=5.0))
    pg_pool = await asyncpg.create_pool(
        dsn=os.getenv("PG_DSN", "postgresql://smartfinance:senha@192.168.15.201:5432/smartfinance"),
        min_size=2, max_size=10,
    )
    milvus = AsyncMilvusClient(uri=os.getenv("MILVUS_URI", "http://192.168.15.201:19530"))

    # --- Singletons APP-scope: criados UMA vez, reusados por todas as requisicoes ---
    app.state.llm = TritonLLM(http_client, LLM_MODEL)
    app.state.embedder = TritonEmbedder(http_client, EMBED_MODEL)
    app.state.repo = PostgresRepository(pg_pool)
    app.state.vectors = MilvusVectorStore(milvus, os.getenv("MILVUS_COLLECTION", "smartfinance_docs"))

    # Grafos LangGraph COMPILADOS UMA VEZ aqui (APP-scope). Compilar e um custo
    # de montagem do StateGraph; nunca faca isso por requisicao.
    app.state.graph = build_graph(app.state.embedder, app.state.vectors, app.state.repo)
    app.state.multi_graph = build_multi_agent(app.state.embedder, app.state.vectors, app.state.repo)

    # CrewAI e OPCIONAL e SINCRONO. So configura se a lib estiver instalada; se
    # nao estiver, a rota /chat-crew responde 503 em vez de derrubar o startup.
    try:
        from cognition.exemplos.crewai import configure
        configure(app.state.embedder, app.state.vectors, app.state.repo)
        app.state.crew_ready = True
    except Exception:
        app.state.crew_ready = False

    try:
        yield
    finally:
        await http_client.aclose()
        await pg_pool.close()
        await milvus.close()


app = FastAPI(title="Smart-Finance Cognition", lifespan=lifespan)


def get_agent(request: Request) -> CognitionAgent:
    # REQUEST-scope: um agent novo por requisicao. Barato — so embrulha os
    # singletons ja existentes em app.state, nao reabre conexao nenhuma.
    s = request.app.state
    return CognitionAgent(llm=s.llm, embedder=s.embedder, vectors=s.vectors, repo=s.repo)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, agent: CognitionAgent = Depends(get_agent)) -> ChatResponse:
    result = await agent.run(req.message)
    return ChatResponse(reply=result.content, model=result.model,
                        prompt_tokens=result.prompt_tokens, completion_tokens=result.completion_tokens)


@app.post("/chat-langchain")
async def chat_lc(req: ChatRequest, request: Request):
    s = request.app.state
    answer = await run_langchain(req.message, s.embedder, s.vectors, s.repo)
    return {"reply": answer}


@app.post("/chat-langgraph")
async def chat_lg(req: ChatRequest, request: Request):
    result = await request.app.state.graph.ainvoke({"question": req.message})
    return {"reply": result["answer"]}


@app.post("/chat-multiagent")
async def chat_ma(req: ChatRequest, request: Request):
    # Reusa o grafo multi-agente ja compilado no lifespan (pesquisador ->
    # analista -> revisor, com gate de revisao). Inicializa os campos que o
    # gate le para evitar KeyError no primeiro passe.
    result = await request.app.state.multi_graph.ainvoke(
        {"question": req.message, "revisions": 0, "critique": ""}
    )
    return {"reply": result["answer"]}


@app.post("/chat-crew")
async def chat_crew(req: ChatRequest, request: Request):
    if not getattr(request.app.state, "crew_ready", False):
        return JSONResponse(status_code=503, content={"detail": "CrewAI nao disponivel."})
    # CrewAI e sincrono e o tool usa asyncio.run() internamente. Rodar isso
    # dentro do event loop do FastAPI levanta "cannot be called from a running
    # event loop". A solucao e empurrar para um threadpool: la nao ha loop
    # rodando, entao o asyncio.run() interno funciona. Import tardio para nao
    # acoplar o startup a presenca do CrewAI.
    from cognition.exemplos.crewai import run_crew
    reply = await run_in_threadpool(run_crew, req.message)
    return {"reply": reply}


@app.exception_handler(httpx.HTTPError)
async def llm_error_handler(request: Request, exc: httpx.HTTPError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": f"Falha ao consultar a LLM: {exc.__class__.__name__}"})


@app.get("/")
async def root():
    return {"message": "Hello World"}