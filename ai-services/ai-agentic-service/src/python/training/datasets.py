"""Hugging Face Datasets loader. One load() for the whole split."""

from __future__ import annotations

from python._lazy import dump, installed, load, require


class DatasetRuntime:
    def ping(self) -> str:
        return dump({"backend": "datasets", "installed": installed("datasets")})

    def load(self, config_json: str) -> str:
        config = load(config_json)
        datasets = require("datasets")
        name = config.get("name")
        split = config.get("split") or "train"
        if not name:
            raise ValueError("dataset name obrigatorio")
        ds = datasets.load_dataset(name, split=split)
        limit = int(config.get("limit") or 0)
        size = len(ds) if limit <= 0 else min(len(ds), limit)
        return dump({"name": name, "split": split, "rows": size})
