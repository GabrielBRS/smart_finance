from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct Tokenizer:
    """Mojo-facing tokenizer. Callers never see PythonObject.

    Layer: interop/python
    Why Python: tokenization libraries (and later Hugging Face) live there.
    Future: swap this body for a native Mojo implementation; keep this API.
    """

    var _impl: PythonObject

    def __init__(out self) raises:
        var module = PythonBridge.import_local("python.models.tokenizer")
        try:
            self._impl = module.Tokenizer()
        except e:
            raise OrchestratorError(
                StatusCode.unavailable,
                "falha ao criar python.models.tokenizer.Tokenizer",
            )

    def encode(self, text: String) raises -> List[String]:
        """One Mojo→Python crossing for the whole string, not per character."""
        try:
            return PythonBridge.to_string_list(self._impl.encode(text))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "tokenizer.encode falhou"
            )

    def encode_batch(self, texts: List[String]) raises -> List[List[String]]:
        """Prefer this over N encode() calls — one crossing, one Python loop."""
        try:
            var batches = self._impl.encode_batch(
                PythonBridge.from_string_list(texts)
            )
            var out = List[List[String]]()
            var count = Int(batches.__len__())
            var i = 0
            while i < count:
                out.append(PythonBridge.to_string_list(batches[i]))
                i += 1
            return out^
        except e:
            raise OrchestratorError(
                StatusCode.internal, "tokenizer.encode_batch falhou"
            )
