"""Tokenizer wrapper.

Default is whitespace so the bridge can be studied without Hugging Face.
`from_pretrained` loads `transformers` in one coarse call.
"""

from __future__ import annotations

from python._lazy import dump, installed, require


class Tokenizer:
    def __init__(self, name: str | None = None) -> None:
        self._name = name or "whitespace"
        self._hf = None
        if name and name != "whitespace":
            transformers = require("transformers")
            self._hf = transformers.AutoTokenizer.from_pretrained(name)

    def ping(self) -> str:
        return dump(
            {
                "backend": self._name,
                "transformers": installed("transformers"),
            }
        )

    def encode(self, text: str) -> list[str]:
        if not text:
            return []
        if self._hf is None:
            return text.split()
        return [str(token) for token in self._hf.tokenize(text)]

    def encode_batch(self, texts: list[str]) -> list[list[str]]:
        return [self.encode(text) for text in texts]
