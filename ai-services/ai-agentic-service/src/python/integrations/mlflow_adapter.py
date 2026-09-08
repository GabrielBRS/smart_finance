"""MLflow logging used by the training adapter. Coarse log_metrics() only."""

from __future__ import annotations

from python._lazy import dump, installed, require


class MLflowAdapter:
    def ping(self) -> str:
        return dump({"backend": "mlflow", "installed": installed("mlflow")})

    def log_metrics(self, metrics: dict[str, float], run_name: str = "mojo-train") -> str:
        mlflow = require("mlflow")
        with mlflow.start_run(run_name=run_name):
            mlflow.log_metrics(metrics)
        return dump({"run_name": run_name, "metrics": metrics})
