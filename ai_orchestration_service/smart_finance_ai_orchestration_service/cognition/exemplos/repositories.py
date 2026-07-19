# cognition/repositories.py
#
# CORRECAO (contrato de id Milvus -> Postgres):
# O agent recupera ids no Milvus e hidrata o conteudo autoritativo no Postgres
# via `WHERE id = ANY($1::uuid[])`. Isso SO funciona se a primary key da colecao
# Milvus for o UUID do documento. Se a colecao usar o int64 auto-gerado default
# do Milvus, os ids chegam como "45783501..." e o cast ::uuid[] estoura com um
# erro opaco de asyncpg. Aqui validamos ANTES e damos um erro claro, e
# preservamos a ORDEM do ranking do Milvus (auditabilidade no dominio fiscal).
import uuid

import asyncpg


class PostgresRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def fetch_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []

        # Contrato explicito: ids do vector store DEVEM ser UUIDs de documento.
        try:
            uuids = [uuid.UUID(i) for i in ids]
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValueError(
                "IDs vindos do vector store nao sao UUIDs validos. Verifique se "
                "a primary key da colecao Milvus e o uuid do documento (e nao o "
                f"int64 auto-gerado). Recebido, ex.: {ids[:3]}"
            ) from exc

        rows = await self._pool.fetch(
            "SELECT id, content, source, created_at "
            "FROM documents WHERE id = ANY($1::uuid[])",
            uuids,
        )

        # Reordena para respeitar o ranking de similaridade do Milvus. Ids sem
        # correspondencia no Postgres sao silenciosamente omitidos (o documento
        # existe no indice vetorial mas nao na fonte autoritativa).
        by_id = {str(r["id"]): dict(r) for r in rows}
        return [by_id[i] for i in ids if i in by_id]