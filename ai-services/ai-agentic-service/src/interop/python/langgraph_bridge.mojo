from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct LangGraphRuntime:
    """Mojo-facing LangGraph runner. Application never sees PythonObject.

    Layer: interop/python
    Why Python: LangGraph has no Mojo equivalent.
    Future: replace with native Mojo graph; keep run_batch().
    """

    var _impl: PythonObject

    def __init__(out self) raises:
        var module = PythonBridge.import_local("python.agentic.langgraph_runtime")
        try:
            self._impl = module.LangGraphRuntime()
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "falha ao criar LangGraphRuntime"
            )

    def ping(self) raises -> String:
        return String(self._impl.ping())

    def run_batch(self, spec_json: String, inputs_json: String) raises -> String:
        """One crossing: compile spec once, invoke the whole input batch."""
        try:
            return String(self._impl.run_batch(spec_json, inputs_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "langgraph.run_batch falhou"
            )
