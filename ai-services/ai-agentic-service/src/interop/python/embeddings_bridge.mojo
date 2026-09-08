from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct EmbeddingModel:
    """Mojo-facing sentence-transformers encoder.

    Layer: interop/python
    Why Python: sentence-transformers / torch. Local hash embed stays in Mojo.
    """

    var _impl: PythonObject

    def __init__(out self) raises:
        var module = PythonBridge.import_local("python.models.embeddings")
        try:
            self._impl = module.EmbeddingModel()
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "falha ao criar EmbeddingModel"
            )

    def ping(self) raises -> String:
        return String(self._impl.ping())

    def embed_batch(self, texts_json: String, config_json: String) raises -> String:
        """One crossing: encode the entire batch, return JSON vectors."""
        try:
            return String(self._impl.embed_batch(texts_json, config_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "embeddings.embed_batch falhou"
            )
