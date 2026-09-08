"""Coarse PyTorch probe. Do not expose per-tensor ops across the Mojo boundary."""

from __future__ import annotations

from python._lazy import dump, installed, require


class TorchRuntime:
    def ping(self) -> str:
        info = {
            "backend": "torch",
            "installed": installed("torch"),
            "cuda": False,
        }
        if not info["installed"]:
            return dump(info)
        torch = require("torch")
        info["cuda"] = bool(torch.cuda.is_available())
        info["device_count"] = int(torch.cuda.device_count()) if info["cuda"] else 0
        return dump(info)
