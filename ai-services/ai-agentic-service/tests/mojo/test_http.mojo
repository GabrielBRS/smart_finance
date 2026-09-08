from application.application import make_application
from application.config import Settings
from std.testing import assert_equal, assert_true, TestSuite
from transport.http.json import json_field_bool, json_field_string
from transport.http.request import HTTPRequest
from transport.http.router import Router
from transport.http.routes.agent import register_agent_routes
from transport.http.routes.health import register_health_routes
from transport.http.routes.workflow import register_workflow_routes
from transport.http.server import HTTPServer


def test_parse_get() raises:
    var req = HTTPRequest.parse("GET /health/live HTTP/1.1\r\nHost: x\r\n\r\n")
    assert_equal(req.method, "GET")
    assert_equal(req.path, "/health/live")
    assert_equal(req.body, "")


def test_parse_post_json() raises:
    var raw = (
        "POST /agents/execute HTTP/1.1\r\n"
        + "Content-Length: 27\r\n\r\n"
        + "{\"prompt\":\"hello mojo\"}"
    )
    var req = HTTPRequest.parse(raw)
    assert_equal(req.method, "POST")
    assert_equal(req.path, "/agents/execute")
    assert_equal(json_field_string(req.body, "prompt"), "hello mojo")


def test_json_fields() raises:
    var body = "{\"agent_id\":\"default\",\"prompt\":\"hi\",\"retrieve\":true}"
    assert_equal(json_field_string(body, "agent_id"), "default")
    assert_equal(json_field_string(body, "prompt"), "hi")
    assert_true(json_field_bool(body, "retrieve", False))
    assert_true(not json_field_bool(body, "missing", False))


def test_router_registers_http_names() raises:
    var router = Router()
    register_health_routes(router)
    register_agent_routes(router)
    register_workflow_routes(router)
    assert_equal(router.match("GET", "/health"), "health.live")
    assert_equal(router.match("POST", "/agents/execute"), "agent.execute")
    assert_equal(router.match("POST", "/workflows/execute"), "workflow.execute")
    assert_equal(router.match("GET", "/missing"), "")


def test_handle_health_and_agent() raises:
    var router = Router()
    register_health_routes(router)
    register_agent_routes(router)
    var server = HTTPServer(router^, "127.0.0.1", 8080)
    var app = make_application(Settings.default())
    app.lifecycle.start()
    var live = server.handle(app, "GET /health HTTP/1.1\r\n\r\n")
    assert_equal(live.status, 200)
    assert_true(live.body.find("\"ready\":true") >= 0)
    var missing = server.handle(app, "GET /nope HTTP/1.1\r\n\r\n")
    assert_equal(missing.status, 404)
    var exec_raw = (
        "POST /agents/execute HTTP/1.1\r\n\r\n"
        + "{\"prompt\":\"hello\"}"
    )
    var executed = server.handle(app, exec_raw)
    assert_equal(executed.status, 200)
    assert_true(executed.body.find("[local] hello") >= 0)


def test_handle_unknown_agent_is_404() raises:
    var router = Router()
    register_agent_routes(router)
    var server = HTTPServer(router^, "127.0.0.1", 8080)
    var app = make_application(Settings.default())
    var raw = (
        "POST /agents/execute HTTP/1.1\r\n\r\n"
        + "{\"agent_id\":\"missing\",\"prompt\":\"x\"}"
    )
    var response = server.handle(app, raw)
    assert_equal(response.status, 404)


def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
