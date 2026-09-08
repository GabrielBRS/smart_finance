from application.application import Application
from transport.http.errors import error_json
from transport.http.request import HTTPRequest
from transport.http.response import HTTPResponse
from transport.http.routes.agent import handle_agent_execute
from transport.http.routes.health import handle_health_live, handle_health_ready
from transport.http.routes.workflow import handle_workflow_execute


def dispatch(
    mut app: Application, name: String, request: HTTPRequest
) raises -> HTTPResponse:
    if name == "health.live":
        return handle_health_live(app, request)
    if name == "health.ready":
        return handle_health_ready(app, request)
    if name == "agent.execute":
        return handle_agent_execute(app, request)
    if name == "workflow.execute":
        return handle_workflow_execute(app, request)
    return HTTPResponse.json(
        404, error_json("not_found", "rota nao registrada: " + name)
    )
