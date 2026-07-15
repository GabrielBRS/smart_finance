#agent
from dataclasses import dataclass

from .ports import LLMMessage, LLMPort, LLMResult, EmbeddingPort, VectorStore, DocumentRepository

SYSTEM_PROMPT = (
    "Você é o agente de cognição financeira do Smart-Finance. "
    "Responda de forma objetiva, tecnicamente correta e em português. "
    "Se não houver dados suficientes, diga isso explicitamente em vez de inventar."
)


@dataclass(slots=True)
class CognitionAgent:
    llm: LLMPort
    embedder: EmbeddingPort
    vectors: VectorStore
    repo: DocumentRepository

    async def run(self, user_message: str) -> LLMResult:
        # 1. transforma a pergunta em vetor
        query_vec = await self.embedder.embed(user_message)

        # 2. Milvus: quais chunks são semanticamente mais próximos?
        chunks = await self.vectors.search(query_vec, top_k=5)

        # 3. Postgres: hidrata o conteúdo AUTORITATIVO por id
        ids = [c.id for c in chunks]
        records = await self.repo.fetch_by_ids(ids)

        # 4. monta o contexto ancorado (com a fonte, pra auditabilidade)
        context = "\n\n".join(f"[{r['source']}] {r['content']}" for r in records)

        # 5. LLM responde ANCORADA no contexto recuperado
        messages = [
            LLMMessage("system", SYSTEM_PROMPT),
            LLMMessage("system", f"Contexto recuperado:\n{context}"),
            LLMMessage("user", user_message),
        ]
        return await self.llm.complete(messages)