import base64
import importlib.util
import json
import sys
import types
from pathlib import Path


class _FakeAgent:
    last_goal = None

    def run(self, goal=None):
        self.__class__.last_goal = goal
        return {
            "memory_backend": "cockroachdb",
            "goal": goal,
            "task_id": "task-test",
            "results": [],
            "invariant": "Memory != authority.",
        }


def _load_handler():
    package = types.ModuleType("hiop_crdb_adapter")
    package.__path__ = []
    orchestrator = types.ModuleType("hiop_crdb_adapter.orchestrator")
    orchestrator.GovernedMemoryAgent = _FakeAgent
    sys.modules["hiop_crdb_adapter"] = package
    sys.modules["hiop_crdb_adapter.orchestrator"] = orchestrator

    path = Path(__file__).resolve().parents[1] / "deploy" / "aws" / "handler.py"
    spec = importlib.util.spec_from_file_location("aws_handler_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_api_gateway_json_body_passes_goal_to_agent(monkeypatch):
    monkeypatch.delenv("S3_RECEIPT_BUCKET", raising=False)
    handler = _load_handler()
    response = handler.lambda_handler({"body": json.dumps({"goal": "safe lab"})}, None)

    assert response["statusCode"] == 200
    assert _FakeAgent.last_goal == "safe lab"
    assert json.loads(response["body"])["goal"] == "safe lab"


def test_function_url_base64_body_passes_goal_to_agent(monkeypatch):
    monkeypatch.delenv("S3_RECEIPT_BUCKET", raising=False)
    handler = _load_handler()
    encoded = base64.b64encode(json.dumps({"goal": "safe orbit"}).encode()).decode()
    handler.lambda_handler({"body": encoded, "isBase64Encoded": True}, None)

    assert _FakeAgent.last_goal == "safe orbit"


def test_direct_lambda_goal_still_works(monkeypatch):
    monkeypatch.delenv("S3_RECEIPT_BUCKET", raising=False)
    handler = _load_handler()
    handler.lambda_handler({"goal": "direct invoke"}, None)

    assert _FakeAgent.last_goal == "direct invoke"
