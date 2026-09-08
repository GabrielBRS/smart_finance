from interop.python.bridge import PythonBridge


struct EnvBridge(Copyable):
    """Reads process environment through CPython `os`.

    Layer: interop/python — stdlib Python, not business rules.
    Why Python: Mojo 1.0 in this project still uses the CPython runtime
    for env lookup. Replace this bridge later if a native Mojo API lands.
    """

    @staticmethod
    def get(name: String, default: String) raises -> String:
        return PythonBridge.env(name, default)
