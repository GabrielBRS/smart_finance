"""Hugging Face Transformers generate, one batch per crossing.

Caches the pipeline on the instance so Mojo does not reload weights
per prompt. vLLM is not imported here — call it as an HTTP service.
"""

from __future__ import annotations

from python._lazy import dump, installed, load, require


class TransformersRuntime:
    def __init__(self) -> None:
        self._pipelines: dict[str, object] = {}

    def ping(self) -> str:
        return dump(
            {
                "backend": "transformers",
                "transformers": installed("transformers"),
                "torch": installed("torch"),
                "accelerate": installed("accelerate"),
            }
        )

    def generate_batch(self, prompts_json: str, config_json: str) -> str:
        prompts = load(prompts_json)
        config = load(config_json)
        if not isinstance(prompts, list):
            raise ValueError("prompts deve ser uma lista; uma travessia por lote")
        model_id = config.get("model") or "sshleifer/tiny-gpt2"
        max_new_tokens = int(config.get("max_new_tokens") or 32)
        pipe = self._pipeline(model_id)
        outputs = pipe(prompts, max_new_tokens=max_new_tokens)
        texts = []
        for item in outputs:
            if isinstance(item, list) and item:
                texts.append(str(item[0].get("generated_text", "")))
            elif isinstance(item, dict):
                texts.append(str(item.get("generated_text", "")))
            else:
                texts.append(str(item))
        return dump({"texts": texts, "model": model_id})

    def _pipeline(self, model_id: str) -> object:
        cached = self._pipelines.get(model_id)
        if cached is not None:
            return cached
        require("torch")
        transformers = require("transformers")
        pipe = transformers.pipeline("text-generation", model=model_id)
        self._pipelines[model_id] = pipe
        return pipe
