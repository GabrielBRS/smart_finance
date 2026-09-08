from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct TransformersRuntime:
    """Mojo-facing HF Transformers / PyTorch generate.

    Layer: interop/python
    Why Python: transformers + torch + accelerate.
    vLLM is not here — call it as an HTTP/gRPC service from infrastructure.
    """

    var _impl: PythonObject

    def __init__(out self) raises:
        var module = PythonBridge.import_local("python.models.transformers_runtime")
        try:
            self._impl = module.TransformersRuntime()
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "falha ao criar TransformersRuntime"
            )

    def ping(self) raises -> String:
        return String(self._impl.ping())

    def generate_batch(self, prompts_json: String, config_json: String) raises -> String:
        """One crossing for the whole prompt list. Pipeline stays cached in Python."""
        try:
            return String(self._impl.generate_batch(prompts_json, config_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "transformers.generate_batch falhou"
            )
