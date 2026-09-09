# Kernel Design Agents

Kernel Design Agents (KDA) is a agent-centric workflow for using coding agents to research, implement, verify, and iterate on performance-sensitive CUDA kernel tasks.

This repository documents the early research prototype and is still under active development (we are looking for community feedbacks!). If you are interested in HAN Lab Mafia's  solution ranking #1~3 on tracks at MLSys Kernel Contest, please refer to [mit-han-lab/mlsys2026-flashinfer-contest](https://github.com/mit-han-lab/mlsys2026-flashinfer-contest) for perform evaluation and reproducement.

This fork adds an executable Optimizer using the Core execution layer while retaining the KDA workflow as its episode prompt. `atrex-bundle.json` declares `src/main.py`; `atrex-agent.json` selects phase prompts. Deployment and Skill packaging are documented in the Runtime [user guide](https://github.com/guoyuqi020/atrex-kernel-agent-runtime/blob/main/docs/user-guide.md#kda-optimizer) ([中文](https://github.com/guoyuqi020/atrex-kernel-agent-runtime/blob/main/docs/user-guide.zh.md#kda-optimizer)). Managed sessions follow the configured phase prompt and injected tool/workspace contract; [docs/agent-flow.md](docs/agent-flow.md) retains the generic upstream workflow for reference.

## Contents

| Path | Purpose |
|---|---|
| `docs/agent-flow.md` | Minimal end-to-end KDA workflow. |
| `prompts/README.md` | How to use prompt templates. |
| `prompts/episode.md` | Optimization workflow, adapted from KDA's original basic flow. |
| `CLAUDE.md` | Repository-facing agent instructions. |

## Getting Started
Clone this repository:

```bash
git clone git@github.com:guoyuqi020/kernel-design-agents.git
cd kernel-design-agents
```

No Skills or nested submodules are bundled by default. Skills added to reusable State remain supported: Runtime installs them into the current Claude/Codex session's private CLI Home. Do not link these Skills into global CLI configuration for managed runs. The Runtime Python environment supplies execution dependencies; this repository is an Agent Bundle, not a separately installable Python distribution.

## Minimal Flow

1. Runtime prepares a separate implementation workspace for the target task.
2. Runtime supplies the task contract: objective, constraints, validation command, and promotion criteria.
3. The selected backend starts a fresh agent session in that workspace.
4. Runtime loads `prompts/episode.md` with the task-specific context and tool contracts.
5. The agent writes a short plan draft to `scratch/draft.md` in the implementation workspace.
6. Convert the draft into an executable plan in `scratch/plan.md`.
7. Implement in small iterations, verifying after each meaningful change.
8. Record candidates, benchmark or evaluation results, profiling evidence, and final promotion decisions.

The workflow is intentionally independent of any single benchmark harness or hardware target. A downstream task can add its own evaluator, datasets, profiling tools, and domain-specific references.

## Optimizer Workspace Layout

Runtime prepares the workspace; the Agent does not construct it from this repository. A typical optimization Attempt has the following Agent-facing layout:

```text
workspace/
├── input/
│   ├── kernel/                 # read-only incumbent Kernel
│   └── evidence/               # read-only authorized reports and conversations
├── agent/optimizer/            # read-only implementation, config, and CLAUDE.md
├── work/kernel/                # writable candidate copied from the incumbent
├── prompts/                    # reusable phase prompts and tool instructions
├── memory/                     # reusable search experiences, lessons, and decisions
├── knowledge/                  # sourced knowledge and reference notes
├── skills/                     # reusable procedures; initially only an index
├── tools/                      # reusable tool scripts
├── hooks/                      # reusable backend hook scripts and definitions
├── sessions/                   # Runtime-managed capture and private CLI Home
└── scratch/                    # temporary plans, requests, probes, and outputs
    ├── draft.md                # written by the Agent before implementation
    └── plan.md                 # executable plan written by the Agent
```

The six reusable directories (`prompts/`, `memory/`, `knowledge/`, `skills/`, `tools/`, `hooks/`) are writable adaptive State. Each contains a `README.md` index that the Agent updates whenever it changes that directory's contents. Runtime selects and restores their starting snapshot according to the configured inheritance policy. Their packaged defaults are omitted from `agent/optimizer/` after State is seeded, so there is only one working copy.

Keep temporary profiling output and other one-off files in `scratch/`; these files are not inherited by later sessions or retries. Do not modify `input/`, `agent/optimizer/`, or `sessions/`. Claude/Codex Skills and Hooks are installed into the current session's private CLI Home, not global settings.

Direction and Experiment history and Gateway results live in Runtime storage and are accessed through the supplied tools. Submit the terminal report with `attempt-report`; local `benchmark.csv` or `candidates.jsonl` files are not required handoff artifacts. The repository's engineering `docs/` directory is not a reusable workspace directory—use `knowledge/` for reusable knowledge.
