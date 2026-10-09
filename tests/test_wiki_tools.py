from __future__ import annotations

import json
import urllib.request
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import runtime_tools
from agent_config import AgentConfig
from runtime_contract import project_contract, wiki_enabled
from sessions.attempt import render_system_prompt as attempt_system_prompt
from sessions.lineage_bootstrap import render_system_prompt as baseline_system_prompt
from tool_contracts import tool_request_schema

ROOT = Path(__file__).resolve().parents[1]


def contract(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    enabled: object = True,
    modules: tuple[str, ...] = (),
    binding: bool = True,
) -> Path:
    path = root / "input/runtime-contract"
    path.mkdir(parents=True)
    names = {"runtime-contract", "gateway-execute", "attempt-report"}
    if "directions" in modules:
        names |= {"update-direction", "list-directions", "load-direction", "find-kernel-directions"}
    if "experiments" in modules:
        names |= {
            "record-experiment",
            "list-experiments",
            "load-experiment",
            "find-kernel-experiments",
        }
    bindings: dict[str, Any] = {name: {} for name in names}
    if binding:
        bindings["wiki-query"] = {"kind": "runtime-query", "operation": "wiki_query"}
    values: dict[str, dict[str, Any]] = {
        "tools": {"bindings": bindings, "gateway": {"operations": {}}},
        "environment": {"tool_modules": list(modules), "services": {"wiki": enabled}},
        "limits": {},
    }
    for name, value in values.items():
        (path / f"{name}.json").write_text(json.dumps({"schema_version": 1, **value}))
    monkeypatch.setenv("ATREX_RUNTIME_CONTRACT_PATH", str(path))
    return path


def context(root: Path) -> Any:
    return SimpleNamespace(
        workspace=root,
        attempt_id="attempt_0123456789abcdef0123456789abcdef",
        manifest={"dsl": "cuda"},
        wiki_url="http://runtime.invalid",
        wiki_capability="test-private-capability",
    )


@pytest.mark.parametrize(
    "modules", [(), ("directions",), ("experiments",), ("directions", "experiments")]
)
@pytest.mark.parametrize("enabled", [False, True])
def test_wiki_switch_controls_discovery_and_both_phase_prompts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    modules: tuple[str, ...],
    enabled: bool,
) -> None:
    contract(tmp_path, monkeypatch, enabled=enabled, modules=modules, binding=enabled)
    assert wiki_enabled() is enabled
    _, projected = project_contract(allow_baseline=False)
    assert ("wiki-query" in projected["tools"]) is enabled
    if enabled:
        schema = projected["tools"]["wiki-query"]["request_schema"]
        assert schema["required"] == ["query"]
        assert set(schema["properties"]) == {"query"}
        assert schema["additionalProperties"] is False
    config = AgentConfig.load(ROOT)
    for render in (attempt_system_prompt, baseline_system_prompt):
        prompt = render(context(tmp_path), config)
        assert ("wiki-query" in prompt) is enabled
        assert ("### Optional GPU Wiki" in prompt) is enabled
        if enabled:
            assert "never substitutes for required Evaluate evidence" in prompt
            assert "toolchain version" in prompt
            assert "not verified conclusions" in prompt
        assert ("runtime_tools.py update-direction --request" in prompt) == (
            "directions" in modules
        )
        assert ("runtime_tools.py record-experiment --request" in prompt) == (
            "experiments" in modules
        )
    with pytest.raises(SystemExit) as result:
        runtime_tools.main(["--help"])
    assert result.value.code == 0
    assert ("wiki-query" in capsys.readouterr().out) is enabled


@pytest.mark.parametrize("enabled", [False, None, 1, "true"])
def test_false_or_untyped_service_rejects_stale_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    enabled: object,
) -> None:
    contract(tmp_path, monkeypatch, enabled=enabled)
    assert not wiki_enabled()
    with pytest.raises(ValueError, match="enabled Wiki service"):
        project_contract(allow_baseline=False)
    with pytest.raises(ValueError, match="disabled"):
        runtime_tools.wiki_query(context(tmp_path), {"query": "tile layout"})


def test_wiki_requires_live_binding_even_with_injected_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ATREX_RUNTIME_CONTRACT_PATH", raising=False)
    assert not wiki_enabled()
    with pytest.raises(ValueError, match="disabled"):
        runtime_tools.wiki_query(context(tmp_path), {"query": "tile layout"})
    contract(tmp_path, monkeypatch, binding=False)
    assert not wiki_enabled()
    with pytest.raises(ValueError, match="disabled"):
        runtime_tools.wiki_query(context(tmp_path), {"query": "tile layout"})


@pytest.mark.parametrize("field", ["wiki_url", "wiki_capability"])
def test_wiki_requires_authority_before_any_http_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    contract(tmp_path, monkeypatch)
    attempt = context(tmp_path)
    setattr(attempt, field, None)
    with pytest.raises(RuntimeError, match="capability is unavailable"):
        runtime_tools.wiki_query(attempt, {"query": "tile layout"})


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"query": " "},
        {"query": None},
        {"query": 5},
        {"query": "q", "operator": "spoof"},
        {"query": "q", "attempt_id": "spoof"},
        {"query": "q", "capability": "spoof"},
        {"query": "q", "idempotency_key": "spoof"},
    ],
)
def test_wiki_only_accepts_a_nonblank_query(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, Any],
) -> None:
    contract(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        runtime_tools.wiki_query(context(tmp_path), payload)


def test_wiki_preserves_request_and_retries_with_runtime_authority_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    contract(tmp_path, monkeypatch)
    attempt = context(tmp_path)
    query = {"query": "  ZW-M890P 上 CUDA tile 的约束?\n"}
    before = deepcopy(query)
    content = {
        "query_id": "q-1",
        "records": [{"record_id": "internal::ppu", "text": "x"}],
        "notes": ["historical measurement"],
    }
    calls: list[urllib.request.Request] = []

    def exchange(request: urllib.request.Request) -> dict[str, Any]:
        calls.append(request)
        if len(calls) == 1:
            raise TimeoutError("retry")
        return {"schema_version": 1, "snapshot_digest": "runtime-audit-only", "content": content}

    monkeypatch.setattr(runtime_tools, "_exchange", exchange)
    assert runtime_tools.wiki_query(attempt, query) == content
    assert query == before
    assert calls[0] is calls[1]
    data = calls[0].data
    assert isinstance(data, bytes)
    wire = json.loads(data)
    assert wire == {
        "schema_version": 1,
        "attempt_id": attempt.attempt_id,
        "query": query["query"],
        "idempotency_key": runtime_tools._idempotency_key(
            "wiki", {"schema_version": 1, "attempt_id": attempt.attempt_id, **query}
        ),
    }
    assert calls[0].full_url == "http://runtime.invalid/v1/wiki/query"
    assert calls[0].headers["Authorization"] == f"Bearer {attempt.wiki_capability}"
    (tmp_path / "scratch").mkdir()
    request_path = tmp_path / "scratch/wiki-query.json"
    request_path.write_text(json.dumps(query))
    monkeypatch.setattr(runtime_tools, "_context", lambda command: attempt)
    assert runtime_tools.main(["wiki-query", "--request", str(request_path)]) == 0
    output = capsys.readouterr().out
    assert json.loads(output) == content
    assert attempt.wiki_capability not in output
    assert attempt.wiki_url not in output
    assert "runtime-audit-only" not in output


def test_wiki_schema_has_no_model_owned_authority_fields() -> None:
    schema = tool_request_schema("wiki-query")
    assert schema is not None
    assert schema["properties"] == {"query": {"type": "string", "minLength": 1, "pattern": r"\S"}}
