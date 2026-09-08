"""Execute the paired custom Evaluate examples without importing Torch or using a GPU."""

from __future__ import annotations

import inspect
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from tool_contracts import tool_request_schema

_PROMPT = Path(__file__).resolve().parents[1] / "prompts/attempt-tools.md"


def _example(text: str, path: str, language: str) -> str:
    pattern = rf"Contents of `{re.escape(path)}`:\n\n```{language}\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    assert match is not None, f"Missing paired Evaluate example: {path}"
    return match.group(1)


@dataclass(frozen=True)
class _Tensor:
    shape: tuple[int, ...]
    device: str
    dtype: str
    draw: int


class _Torch(ModuleType):
    Tensor = _Tensor
    float32 = "torch.float32"

    def __init__(self) -> None:
        super().__init__("torch")
        self.draws = 0

    def randn(self, shape: tuple[int, ...], *, device: str, dtype: str) -> _Tensor:
        self.draws += 1
        return _Tensor(shape, device, dtype, self.draws)

    def randn_like(self, tensor: _Tensor) -> _Tensor:
        return self.randn(tensor.shape, device=tensor.device, dtype=tensor.dtype)


class _VecAdd:
    def forward(self, left: _Tensor, right: _Tensor) -> tuple[_Tensor, _Tensor]:
        return left, right


@pytest.mark.parametrize("shape_id,num_elements", [("0", 1024), ("1", 4097)])
def test_custom_input_and_shapes_examples_match_the_public_vecadd_abi(
    monkeypatch: pytest.MonkeyPatch, shape_id: str, num_elements: int,
) -> None:
    text = _PROMPT.read_text(encoding="utf-8")
    source = _example(text, "scratch/custom-input.py", "python")
    shapes = json.loads(_example(text, "scratch/custom-shapes.json", "json"))
    assert shapes == {
        "0": {"input_kwargs": {"num_elements": 1024}, "init_kwargs": None},
        "1": {"input_kwargs": {"num_elements": 4097}, "init_kwargs": None},
    }
    torch = _Torch()
    monkeypatch.setitem(sys.modules, "torch", torch)
    namespace: dict[str, Any] = {}
    exec(compile(source, "scratch/custom-input.py", "exec"), namespace)
    make_inputs = namespace["_make_inputs"]
    shape = shapes[shape_id]
    inspect.signature(make_inputs).bind(**shape["input_kwargs"])
    model = _VecAdd(**(shape["init_kwargs"] or {}))

    for expected_draws in [(1, 2), (3, 4)]:
        inputs = make_inputs(**shape["input_kwargs"])
        assert isinstance(inputs, dict) and set(inputs) == {"left", "right"}
        inspect.signature(model.forward).bind(**inputs)
        left, right = model.forward(**inputs)
        assert left.shape == right.shape == (num_elements,)
        assert left.device == right.device == "cuda"
        assert left.dtype == right.dtype == torch.float32
        assert (left.draw, right.draw) == expected_draws
    assert torch.draws == 4


def test_custom_evaluate_call_reuses_both_documented_files() -> None:
    text = _PROMPT.read_text(encoding="utf-8")
    requests = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)]
    assert {
        "operation": "evaluate",
        "mode": "correctness_only",
        "input_path": "scratch/custom-input.py",
        "shapes_path": "scratch/custom-shapes.json",
    } in requests
    assert "Model.forward(left, right)" in text
    assert "init_kwargs" in text and "input_kwargs" in text
    assert "Do not hard-code\na random seed" in text
    assert "Prefer supplying both custom files together" in text


def test_custom_evaluate_schema_describes_generator_and_model_argument_mapping() -> None:
    schema = tool_request_schema("gateway-execute", operation="evaluate")
    assert schema is not None
    properties = schema["properties"]
    assert "_make_inputs(**input_kwargs)" in properties["input_py"]["description"]
    assert "Model.forward" in properties["input_py"]["description"]
    for field in ("shapes", "shapes_path"):
        description = properties[field]["description"]
        assert "input_kwargs" in description and "init_kwargs" in description
    assert "_make_inputs" in properties["input_path"]["description"]
