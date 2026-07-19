from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True, frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass(slots=True, frozen=True)
class LLMResult:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int


@dataclass(slots=True, frozen=True)
class RetrievedChunk:
    id: str
    text: str
    score: float
    source: str


class LLMPort(Protocol):
    async def complete(self, messages: list[LLMMessage], *,
                       temperature: float = 0.2, max_tokens: int = 1024) -> LLMResult: ...


class EmbeddingPort(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class VectorStore(Protocol):
    async def search(self, embedding: list[float], *, top_k: int = 5) -> list[RetrievedChunk]: ...


class DocumentRepository(Protocol):
    async def fetch_by_ids(self, ids: list[str]) -> list[dict]: ...