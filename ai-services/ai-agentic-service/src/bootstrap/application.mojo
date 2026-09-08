from application.application import Application as Orchestrator
from application.application import make_application
from application.config import Settings
from infrastructure.settings import load_settings
from transport.http.router import Router
from transport.http.routes.agent import register_agent_routes
from transport.http.routes.health import register_health_routes
from transport.http.routes.workflow import register_workflow_routes
from transport.http.server import HTTPServer


struct Application:
    """Process composition root. Wires use cases to input adapters."""

    var orchestrator: Orchestrator
    var http: HTTPServer
    var settings: Settings

    def __init__(
        out self,
        var orchestrator: Orchestrator,
        var http: HTTPServer,
        var settings: Settings,
    ):
        self.orchestrator = orchestrator^
        self.http = http^
        self.settings = settings^

    @staticmethod
    def build() raises -> Application:
        var settings = load_settings()
        var orchestrator = make_application(settings.copy())
        var router = Router()
        register_health_routes(router)
        register_agent_routes(router)
        register_workflow_routes(router)
        var http = HTTPServer(
            router^, settings.http_host.copy(), settings.http_port
        )
        return Application(orchestrator^, http^, settings^)

    def run(mut self) raises:
        self.orchestrator.lifecycle.start()
        print(
            "ai-orchestrator",
            self.orchestrator.health().version,
            "http://",
            self.settings.http_host,
            ":",
            Int(self.settings.http_port),
        )
        self.http.serve(self.orchestrator)
