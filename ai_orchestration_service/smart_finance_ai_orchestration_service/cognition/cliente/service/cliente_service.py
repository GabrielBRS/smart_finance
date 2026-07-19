# service/cliente_service.py
from cognition.cliente.domain.cliente import Cliente
from cognition.cliente.repository.cliente_repository import ClienteRepository

class ClienteService:
    def __init__(self, *, llm, embedder, vectors, repo: ClienteRepository) -> None:
        self._llm = llm
        self._embedder = embedder
        self._vectors = vectors
        self._repo = repo

    async def profile(self, cliente_id: int) -> Cliente | None:
        return await self._repo.get_cliente(cliente_id)

    async def chat(self, cliente_id: int, mensagem: str):
        ...   # embed -> retrieval -> LLM entra aqui depois