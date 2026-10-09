"""Render optional knowledge-tool guidance from the trusted Session contract."""

from __future__ import annotations

from runtime_contract import wiki_enabled


def with_wiki_instructions(prompt: str) -> str:
    if not wiki_enabled():
        return prompt
    invocation = "python3 agent/optimizer/src/runtime_tools.py"
    report = f"{invocation} attempt-report --request scratch/<request>.json"
    prompt = prompt.replace(
        report,
        report + f"\n{invocation} wiki-query --request scratch/<request>.json",
        1,
    )
    return prompt.rstrip() + (
        "\n\n### Optional GPU Wiki\n\n"
        "Use `wiki-query` for a focused hardware, DSL, implementation, or optimization question "
        "when existing task evidence leaves an actionable knowledge gap. It is available in "
        "both Bootstrap and optimization, independently of Journal modules. Write only "
        '`{"query":"What tile-layout constraints apply to this target GPU and DSL?"}` '
        "to `scratch/wiki-query.json`, then run "
        f"`{invocation} wiki-query --request scratch/wiki-query.json`. "
        "Runtime supplies the operator, hardware and DSL scope, authority, and retry identity; "
        "do not add those fields or call the knowledge service directly. The result contains "
        "`query_id`, `records`, and `notes`; read relevant content and applicability limits. "
        "Check the actual GPU/product, toolchain version, assumptions, and evidence quality. "
        "Historical measurements and interpretations are research leads, not verified conclusions "
        "about the current Kernel. Validate adopted recommendations with the appropriate Runtime "
        "tools; a Wiki result never substitutes for required Evaluate evidence. Stop research once "
        "one actionable hypothesis has adequate support. Cite exact returned Record IDs in "
        "`knowledge_used` only when they materially informed the work; do not invent IDs."
    )
