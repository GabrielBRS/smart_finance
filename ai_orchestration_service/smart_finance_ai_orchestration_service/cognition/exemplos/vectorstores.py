from pymilvus import AsyncMilvusClient

from .ports import RetrievedChunk


class MilvusVectorStore:
    def __init__(self, client: AsyncMilvusClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    async def search(self, embedding: list[float], *, top_k: int = 5) -> list[RetrievedChunk]:
        results = await self._client.search(
            collection_name=self._collection,
            data=[embedding],
            anns_field="embedding",
            limit=top_k,
            output_fields=["text", "source"],
        )
        hits = results[0]
        return [
            RetrievedChunk(
                id=str(h["id"]),
                text=h["entity"].get("text", ""),
                score=h["distance"],
                source=h["entity"].get("source", ""),
            )
            for h in hits
        ]