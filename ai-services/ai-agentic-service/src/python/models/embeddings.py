"""sentence-transformers embeddings. One encode() for the whole batch."""

from __future__ import annotations

from python._lazy import dump, installed, load, require


class EmbeddingModel:
    def __init__(self) -> None:
        self._models: dict[str, object] = {}

    def ping(self) -> str:
        return dump(
            {
                "backend": "sentence-transformers",
                "installed": installed("sentence_transformers"),
                "torch": installed("torch"),
            }
        )

    def embed_batch(self, texts_json: str, config_json: str = "{}") -> str:
        texts = load(texts_json)
        config = load(config_json)
        if not isinstance(texts, list):
            raise ValueError("texts deve ser uma lista; uma travessia por lote")
        model_id = config.get("model") or "sentence-transformers/all-MiniLM-L6-v2"
        model = self._model(model_id)
        vectors = model.encode(texts, convert_to_numpy=True)
        return dump(
            {
                "model": model_id,
                "vectors": [row.tolist() for row in vectors],
            }
        )

    def _model(self, model_id: str) -> object:
        cached = self._models.get(model_id)
        if cached is not None:
            return cached
        st = require("sentence_transformers")
        model = st.SentenceTransformer(model_id)
        self._models[model_id] = model
        return model
