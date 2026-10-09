"""Knowledge declarations survive Journal reads and terminal report reconciliation."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
import test_runtime_tools as helpers
from test_runtime_tools import _runtime_owned_journals as _runtime_owned_journals

import runtime_tools
from runtime_tools import runtime_journal as real_runtime_journal
from sessions.tool_module_prompts import modular_tool_instructions
from tool_contracts import local_validation_issue, tool_recovery, tool_request_schema

KNOWLEDGE = [
    {
        "record_id": "internal_gpu_wiki::ppu15-resources-lowering",
        "finding": "Register pressure can reduce occupancy on the measured toolchain.",
        "application": "Reduced the live accumulator set and measured the exact candidate.",
    }
]


@pytest.mark.parametrize("directions_enabled", [False, True])
@pytest.mark.parametrize("allow_baseline", [False, True])
def test_experiment_knowledge_schema_is_optional_and_independent(
    directions_enabled: bool,
    allow_baseline: bool,
) -> None:
    schema = tool_request_schema(
        "record-experiment", allow_baseline=allow_baseline, directions_enabled=directions_enabled
    )
    assert schema is not None
    assert "knowledge_used" not in schema["required"]
    field = schema["properties"]["knowledge_used"]
    assert field["default"] == []
    assert field["items"]["additionalProperties"] is False
    assert set(field["items"]["required"]) == {"record_id", "finding", "application"}
    assert all(value["pattern"] == r"\S" for value in field["items"]["properties"].values())


@pytest.mark.parametrize("directions_enabled", [False, True])
@pytest.mark.parametrize("declared", [False, True])
def test_experiment_keeps_exact_request_and_does_not_need_wiki(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    directions_enabled: bool,
    declared: bool,
) -> None:
    monkeypatch.delenv("ATREX_RUNTIME_CONTRACT_PATH", raising=False)
    context = helpers._context(tmp_path)
    request = helpers._experiment()
    if not directions_enabled:
        request.pop("direction_id")
    if declared:
        request["knowledge_used"] = deepcopy(KNOWLEDGE)
    before = deepcopy(request)
    calls: list[dict[str, Any]] = []

    def post(_url: str, _capability: str, path: str, value: dict[str, Any]) -> dict[str, Any]:
        assert path == "/v1/runtime/journals"
        calls.append(value)
        return {"result": {"status": "recorded", "experiment_id": "experiment_" + "a" * 32}}

    monkeypatch.setattr(runtime_tools, "runtime_journal", real_runtime_journal)
    monkeypatch.setattr(runtime_tools, "_post", post)
    runtime_tools.record_experiment(context, request)
    assert request == before
    assert calls[0]["request"] == before
    assert ("knowledge_used" in calls[0]["request"]) is declared
    expected = {
        "schema_version": 2,
        "attempt_id": context.attempt_id,
        "operation": "experiment_record",
        "request": before,
    }
    assert calls[0]["idempotency_key"] == runtime_tools._idempotency_key(
        "runtime-journal", expected
    )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "record-id",
        {},
        ["record-id"],
        [{}],
        [{**KNOWLEDGE[0], "extra": "no"}],
        [{**KNOWLEDGE[0], "record_id": " "}],
        [{**KNOWLEDGE[0], "finding": "\n"}],
        [{**KNOWLEDGE[0], "application": 3}],
    ],
)
def test_experiment_rejects_malformed_knowledge_before_journal_write(
    tmp_path: Path,
    value: object,
) -> None:
    context = helpers._context(tmp_path)
    request = {**helpers._experiment(), "knowledge_used": value}
    with pytest.raises(ValueError, match="Experiment knowledge_used") as result:
        runtime_tools.record_experiment(context, request)
    assert helpers._fake_state(context)["experiments"] == []
    issue = local_validation_issue(str(result.value))
    assert issue["path"].startswith("knowledge_used")
    recovery = tool_recovery(
        "record-experiment", detail=str(result.value), directions_enabled=False
    )
    assert recovery is not None
    assert "no new query is required" in recovery[0]["instruction"]


@pytest.mark.parametrize("declared", [False, True])
def test_experiment_knowledge_round_trip_into_list_load_and_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    declared: bool,
) -> None:
    monkeypatch.delenv("ATREX_RUNTIME_CONTRACT_PATH", raising=False)
    context = helpers._context(tmp_path)
    direction = helpers._propose_and_start_direction(context)
    request = helpers._experiment(direction)
    if declared:
        request["knowledge_used"] = deepcopy(KNOWLEDGE)
    receipt = runtime_tools.record_experiment(context, request)
    experiment_id = receipt["experiment_id"]
    expected = KNOWLEDGE if declared else []
    stored = deepcopy(helpers._fake_state(context)["experiments"])
    loaded = runtime_tools.load_experiment(context, {"experiment_id": experiment_id})
    assert loaded["knowledge_used"] == expected
    runtime_tools.list_experiments(context, {"file": "scratch/index.json"})
    index = json.loads((context.workspace / "scratch/index.json").read_text())
    assert index["experiments"][0]["knowledge_used"] == expected
    helpers._complete_direction(context, direction)
    runtime_tools.attempt_report(context, helpers._report(experiment_id))
    report = json.loads(context.report_path.read_text())
    assert report["experiments"][0]["knowledge_used"] == expected
    assert helpers._fake_state(context)["experiments"] == stored


@pytest.mark.parametrize(
    "modules",
    [
        frozenset(),
        frozenset({"directions"}),
        frozenset({"experiments"}),
        frozenset({"directions", "experiments"}),
    ],
)
def test_experiment_prompt_only_teaches_declaration_when_module_enabled(
    monkeypatch: pytest.MonkeyPatch,
    modules: frozenset[str],
) -> None:
    monkeypatch.delenv("ATREX_RUNTIME_CONTRACT_PATH", raising=False)
    template = (Path(__file__).parents[1] / "prompts/attempt-tools.md").read_text()
    prompt = modular_tool_instructions(template, "cuda", modules)
    assert ("Optional knowledge_used defaults to []" in prompt) is ("experiments" in modules)
    if "experiments" in modules:
        assert "not proof of adoption" in prompt
        assert "including when Wiki is disabled" in prompt
