"""LoRA helpers used by PeftRuntime / trainer. Not called from Mojo directly."""

from __future__ import annotations

from python._lazy import load


def lora_kwargs(config_json: str) -> dict:
    config = load(config_json)
    return {
        "r": int(config.get("r") or 8),
        "lora_alpha": int(config.get("lora_alpha") or 16),
        "lora_dropout": float(config.get("lora_dropout") or 0.05),
    }
