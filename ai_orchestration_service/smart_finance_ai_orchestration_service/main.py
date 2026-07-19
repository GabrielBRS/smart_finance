# main.py
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from pymilvus import AsyncMilvusClient

from cognition.config.postgres_config import create_pg_pool

from cognition.exemplos.adapters import TritonLLM, TritonEmbedder
from cognition.exemplos.config import LLM_BASE_URL, LLM_MODEL, EMBED_MODEL
from cognition.exemplos.vectorstores import MilvusVectorStore

from cognition.cliente.repository.cliente_repository import ClienteRepository
from cognition.cliente.routers import cliente_router
from cognition.cliente.service import ClienteService

# transacao: reative quando o domínio existir de verdade
# from cognition.transacao.routers import transacao_router
# from cognition.transacao.service import TransacaoService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- infra: abre UMA vez, reusa em todos os domínios ---
    http_client = httpx.AsyncClient(base_url=LLM_BASE_URL, timeout=httpx.Timeout(60.0, connect=5.0))
    pg_pool = await create_pg_pool()          # credenciais vêm do ambiente, não do main
    milvus = AsyncMilvusClient(uri=os.getenv("MILVUS_URI", "http://192.168.15.201:19530"))

    # --- adapters de infra ---
    app.state.llm = TritonLLM(http_client, LLM_MODEL)
    app.state.embedder = TritonEmbedder(http_client, EMBED_MODEL)
    app.state.vectors = MilvusVectorStore(milvus, os.getenv("MILVUS_COLLECTION", "smartfinance_docs"))

    # --- repositório do domínio cliente (a porta do próprio domínio) ---
    cliente_repo = ClienteRepository(pg_pool)

    # --- service de domínio: singleton app-scope ---
    app.state.cliente_service = ClienteService(
        llm=app.state.llm, embedder=app.state.embedder,
        vectors=app.state.vectors, repo=cliente_repo,
    )

    try:
        yield
    finally:
        await http_client.aclose()
        await pg_pool.close()
        await milvus.close()


app = FastAPI(
    title="Smart-Finance Cognition",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app.include_router(cliente_router)
# app.include_router(transacao_router)


@app.exception_handler(httpx.HTTPError)
async def llm_error_handler(request: Request, exc: httpx.HTTPError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": f"Falha ao consultar a LLM: {exc.__class__.__name__}"})


@app.get("/")
async def root():
    return {"message": "Smart-Finance Cognition up"}