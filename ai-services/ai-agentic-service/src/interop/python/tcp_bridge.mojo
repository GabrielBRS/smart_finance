from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct TcpListener:
    """Mojo-facing TCP listen socket. Python implements bind/accept.

    Layer: interop/python
    Why Python: Mojo 1.0 has no std.net. HTTP stays in transport/http.
    """

    var _impl: PythonObject

    def __init__(out self, host: String, port: Int) raises:
        var module = PythonBridge.import_local("python.runtime.tcp")
        try:
            self._impl = module.Listener(host, port)
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "falha ao bind TCP " + host
            )

    def accept(self) raises -> TcpConnection:
        try:
            return TcpConnection(self._impl.accept())
        except e:
            raise OrchestratorError(
                StatusCode.internal, "accept TCP falhou"
            )

    def close(self) raises:
        try:
            _ = self._impl.close()
        except e:
            pass


struct TcpConnection:
    var _impl: PythonObject

    def __init__(out self, impl: PythonObject):
        self._impl = impl

    def recv_http(self) raises -> String:
        """One crossing: whole HTTP request bytes in, String out."""
        try:
            return String(self._impl.recv_http())
        except e:
            raise OrchestratorError(
                StatusCode.internal, "recv HTTP falhou"
            )

    def send_all(self, data: String) raises:
        try:
            _ = self._impl.sendall(data)
        except e:
            raise OrchestratorError(
                StatusCode.internal, "send HTTP falhou"
            )

    def close(self) raises:
        try:
            _ = self._impl.close()
        except e:
            pass
