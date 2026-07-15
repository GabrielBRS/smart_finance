import httpx

from .ports import LLMMessage, LLMResult


class TritonLLM:
    """Adaptador para o Nemotron servido no Triton (192.168.15.201)."""

    def __init__(self, client: httpx.AsyncClient, model: str) -> None:
        self._client = client
        self._model = model

    async def complete(self, messages: list[LLMMessage], *,
                       temperature: float = 0.2, max_tokens: int = 1024) -> LLMResult:
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage", {})
        return LLMResult(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", self._model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )


class TritonEmbedder:
    """Implementa EmbeddingPort via endpoint /v1/embeddings do Triton."""

    def __init__(self, client: httpx.AsyncClient, model: str) -> None:
        self._client = client
        self._model = model

    async def embed(self, text: str) -> list[float]:
        resp = await self._client.post("/embeddings", json={"model": self._model, "input": text})
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]