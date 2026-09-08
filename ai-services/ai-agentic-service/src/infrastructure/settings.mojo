from application.config import Settings
from domain.model import Provider
from interop.python.env_bridge import EnvBridge


def load_settings() raises -> Settings:
    """Fill Settings from the process environment.

    Layer: infrastructure
    Why here: application owns the Settings shape; it must not import Python.
    The env read itself is delegated to EnvBridge (interop).
    """
    var settings = Settings.default()
    settings.app_name = EnvBridge.get("AOR_APP_NAME", settings.app_name)
    settings.app_env = EnvBridge.get("AOR_APP_ENV", settings.app_env)
    settings.log_level = EnvBridge.get("AOR_LOG_LEVEL", settings.log_level)
    settings.http_host = EnvBridge.get("AOR_HTTP_HOST", settings.http_host)
    settings.grpc_host = EnvBridge.get("AOR_GRPC_HOST", settings.grpc_host)
    settings.ipc_path = EnvBridge.get("AOR_IPC_PATH", settings.ipc_path)
    settings.compute_ipc_path = EnvBridge.get(
        "AOR_COMPUTE_IPC_PATH", settings.compute_ipc_path
    )
    settings.data_ipc_path = EnvBridge.get(
        "AOR_DATA_IPC_PATH", settings.data_ipc_path
    )
    settings.llm_provider = Provider.parse(
        EnvBridge.get("AOR_LLM_PROVIDER", settings.llm_provider.name())
    )
    settings.storage_engine = EnvBridge.get(
        "AOR_STORAGE_ENGINE", settings.storage_engine
    )
    return settings^
