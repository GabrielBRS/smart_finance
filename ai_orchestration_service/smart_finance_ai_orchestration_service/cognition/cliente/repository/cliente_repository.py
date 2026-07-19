# repository/cliente_repository.py
import asyncpg
from cognition.cliente.domain.cliente import Cliente

class ClienteRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_cliente(self, cliente_id: int) -> Cliente | None:
        row = await self._pool.fetchrow(
            "SELECT id, nome, documento, criado_em FROM cliente WHERE id = $1",
            cliente_id,
        )
        return Cliente(**row) if row else None