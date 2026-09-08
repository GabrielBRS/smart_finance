from std.python import Python, PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode


struct PythonBridge(Copyable):
    """Single place that talks to embedded CPython.

    Domain, application and infrastructure never import Python.
    Only files under interop/python/ should use this type.
    """

    @staticmethod
    def ensure_local_path() raises:
        """Runtime: put `src` on sys.path so `python.*` modules resolve.

        Compile time does not see src/python/*.py — CPython loads them here.
        """
        var sys = Python.import_module("sys")
        var os = Python.import_module("os")
        var candidates = List[String]()
        candidates.append("src")
        var env_path = os.environ.get("AOR_PYTHON_PATH")
        if env_path:
            candidates.append(String(env_path))
        for candidate in candidates:
            var abs_path = os.path.abspath(candidate)
            var python_dir = os.path.join(abs_path, "python")
            if os.path.isdir(python_dir):
                sys.path.insert(0, abs_path)
                return

    @staticmethod
    def import_module(name: String) raises -> PythonObject:
        try:
            return Python.import_module(name)
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "python module indisponivel: " + name
            )

    @staticmethod
    def import_local(name: String) raises -> PythonObject:
        try:
            Self.ensure_local_path()
        except e:
            pass
        return Self.import_module(name)

    @staticmethod
    def env(name: String, default: String) raises -> String:
        try:
            var os = Self.import_module("os")
            var value = os.environ.get(name)
            if value:
                return String(value)
        except e:
            pass
        return default

    @staticmethod
    def from_string_list(items: List[String]) raises -> PythonObject:
        var builtins = Python.import_module("builtins")
        var out = builtins.list()
        for item in items:
            _ = out.append(item)
        return out

    @staticmethod
    def to_string_list(value: PythonObject) raises -> List[String]:
        var out = List[String]()
        var count = Int(value.__len__())
        var i = 0
        while i < count:
            out.append(String(value[i]))
            i += 1
        return out^
