"""PEFT adapter factory. One config in, one adapter description out."""

from __future__ import annotations

from python._lazy import dump, installed, load, require


class PeftRuntime:
    def ping(self) -> str:
        return dump({"backend": "peft", "installed": installed("peft")})

    def prepare(self, config_json: str) -> str:
        config = load(config_json)
        peft = require("peft")
        method = config.get("method") or "lora"
        if method == "lora":
            peft_config = peft.LoraConfig(
                r=int(config.get("r") or 8),
                lora_alpha=int(config.get("lora_alpha") or 16),
                lora_dropout=float(config.get("lora_dropout") or 0.05),
                task_type=config.get("task_type") or "CAUSAL_LM",
            )
        else:
            raise ValueError("method PEFT nao suportado: " + method)
        return dump(
            {
                "method": method,
                "r": peft_config.r,
                "lora_alpha": peft_config.lora_alpha,
            }
        )
