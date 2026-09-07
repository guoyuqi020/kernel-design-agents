from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agent_config import AgentConfig
from backends import DEFAULT_BACKEND_REGISTRY
from sessions import attempt, lineage_bootstrap

ROOT = Path(__file__).resolve().parents[1]


def _context() -> Any:
    return SimpleNamespace(
        manifest={
            "dsl": "triton",
            "operator": "vector_add",
            "hardware_target": "sm_120",
            "context": {
                "dsl": "triton",
                "operator": "vector_add",
                "hardware_target": "sm_120",
                "epoch_number": 2,
                "attempt_ordinal": 1,
            },
        },
        agent_problem={"objective": "Add two vectors", "shape_domain": {"size": 1024}},
        evidence_prompt="## Prepared workspace\nRead prior evidence through the supplied tools.",
    )


def test_episode_keeps_basic_flow_without_unfilled_contract() -> None:
    config = AgentConfig.load(ROOT, {})
    prompt = attempt.render_prompt(_context(), config)
    for sentence in (
        "Your job is to produce the best correct implementation for the task described below.",
        "Research only the references needed for this task.",
        "Implement one candidate at a time.",
        "Keep the final change scoped to the task contract.",
        "The main risks and unknowns.",
        "Candidate implementation directions ranked by expected value and risk.",
        "Do not start implementation until the draft exists.",
    ):
        assert sentence in prompt
    assert "<fill in" not in prompt
    assert "docs/draft.md" not in prompt
    assert "scratch/draft.md" in prompt
    assert '"dsl": "triton"' in prompt
    assert '"hardware_target": "sm_120"' in prompt
    assert "update-direction" in prompt
    assert "record-experiment" in prompt
    assert "attempt-report" in prompt
    assert "## Public operator contract" in prompt


@pytest.mark.parametrize("backend", ("claude", "codex", "qodercli", "pi"))
def test_repository_instructions_reach_all_backends(backend: str) -> None:
    config = AgentConfig.load(ROOT, {})
    instructions = attempt.render_system_prompt(_context(), config)
    repository_instructions = (ROOT / "CLAUDE.md").read_text().strip()
    assert instructions.count(repository_instructions) == 1
    command = DEFAULT_BACKEND_REGISTRY.create(backend).build_command(
        "task", "session-test", "high", "", system_prompt=instructions,
    )
    assert sum(repository_instructions in argument for argument in command) == 1


def test_managed_prompt_state_and_readonly_repository_instructions(tmp_path: Path) -> None:
    repository = tmp_path / "agent/optimizer"
    repository.mkdir(parents=True)
    shutil.copy2(ROOT / "CLAUDE.md", repository / "CLAUDE.md")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    value = json.loads((ROOT / "atrex-agent.json").read_text())
    value["prompt_root"] = "workspace"
    (repository / "atrex-agent.json").write_text(json.dumps(value))
    config = AgentConfig.load(repository, {}, workspace=tmp_path)
    assert config.repository_instructions == repository / "CLAUDE.md"
    assert config.prompt_path("optimization_attempt") == tmp_path / "prompts/episode.md"
    (tmp_path / "prompts/episode.md").write_text("Learned next-session workflow.")
    assert "Learned next-session workflow." in attempt.render_prompt(_context(), config)
    assert not (tmp_path / "CLAUDE.md").exists()  # No duplicate CLI auto-discovery copy.


def test_repository_instructions_reject_links(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    shutil.copy2(ROOT / "atrex-agent.json", tmp_path / "atrex-agent.json")
    (tmp_path / "CLAUDE.md").symlink_to(ROOT / "CLAUDE.md")
    with pytest.raises(ValueError, match=r"regular CLAUDE\.md"):
        AgentConfig.load(tmp_path, {})


def test_bootstrap_stays_a_special_attempt() -> None:
    config = AgentConfig.load(ROOT, {})
    prompt = lineage_bootstrap.render_prompt(_context(), config)
    instructions = lineage_bootstrap.render_system_prompt(_context(), config)
    assert "A slower but correct candidate is valid" in prompt
    assert "Do not use `pivot` during Bootstrap" in prompt
    assert "Bootstrap follows its separately supplied baseline workflow" in instructions
    assert instructions.count("# Agent Instructions") == 1
    assert "--request scratch/<request>.json" in instructions


@pytest.mark.parametrize("phase", (attempt, lineage_bootstrap))
def test_evaluate_options_reach_managed_session_instructions(phase: Any) -> None:
    config = AgentConfig.load(ROOT, {})
    instructions = phase.render_system_prompt(_context(), config)
    assert "mode=full|correctness_only" in instructions
    assert "input_py or input_path" in instructions
    assert "shapes or shapes_path" in instructions
    assert "without performance measurement or automatic profiling" in instructions
    assert "requires a successful full evaluation using" in instructions
    assert "input_scope" in instructions


def test_episode_is_the_only_optimization_workflow() -> None:
    config = AgentConfig.load(ROOT, {})
    assert config.prompt_path("optimization_attempt") == ROOT / "prompts/episode.md"
    assert not (ROOT / "prompts/basic-flow.md").exists()
    instructions = (ROOT / "CLAUDE.md").read_text()
    assert "prompts/episode.md" in instructions
    assert "1. " not in instructions


def test_managed_instructions_do_not_recommend_humanize() -> None:
    config = AgentConfig.load(ROOT, {})
    for phase in (attempt, lineage_bootstrap):
        text = phase.render_prompt(_context(), config) + phase.render_system_prompt(
            _context(), config,
        )
        assert "humanize" not in text.lower()
        assert "external planning plugin" not in text.lower()
    for path in ("README.md", "skills/README.md"):
        assert "humanize" not in (ROOT / path).read_text().lower()
