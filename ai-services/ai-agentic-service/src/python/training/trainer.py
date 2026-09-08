"""TRL / Accelerate training entry. One train() call, not a step loop from Mojo.

LiteLLM and vLLM are not imported. Optional MLflow logging stays local.
"""

from __future__ import annotations

from python.integrations.mlflow_adapter import MLflowAdapter
from python.training.lora import lora_kwargs
from python._lazy import dump, installed, load, require


class Trainer:
    def ping(self) -> str:
        return dump(
            {
                "backend": "trl",
                "trl": installed("trl"),
                "accelerate": installed("accelerate"),
                "peft": installed("peft"),
                "datasets": installed("datasets"),
                "bitsandbytes": installed("bitsandbytes"),
                "mlflow": installed("mlflow"),
            }
        )

    def train(self, config_json: str) -> str:
        config = load(config_json)
        require("trl")
        require("accelerate")
        require("transformers")
        require("torch")
        _ = lora_kwargs(dump(config.get("lora") or {}))
        if config.get("mlflow"):
            MLflowAdapter().log_metrics({"started": 1.0}, config.get("run_name") or "train")
        return dump(
            {
                "status": "configured",
                "model": config.get("model"),
                "note": "train() e o unico cruzamento; o loop TRL fica neste processo",
            }
        )
