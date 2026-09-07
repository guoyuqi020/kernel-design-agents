# Prompts index

This directory stores the Agent's phase prompts and shared tool protocol. In managed sessions it is writable, inherited State; edits affect later fresh sessions, not the current conversation.

Whenever you add, change, rename, or remove a prompt, update this README with its path, purpose, and dependencies. Preserve configured phase paths. Keep temporary requests and raw traces in scratch/, not here.

## Available Templates

| Path | Purpose |
|---|---|
| `episode.md` | Executed optimization prompt: basic flow adapted to the supplied task and tool contracts. |
| `framework_baseline.md` | First correct DSL implementation before optimization begins. |
| `generalize_agent_problem.md` | Public operator-contract generation, without hidden evaluator cases. |
| `attempt-tools.md` | Exact CLI, Journal, and terminal Report contracts shared by Bootstrap and Attempts, including custom-input and correctness-only evaluation, Evaluate comparisons, and local file-error repair; depends on `src/runtime_tools.py`, `src/tool_contracts.py`, and the trusted Runtime request/report contracts. |

## How To Use

Managed sessions load the configured phase prompt automatically. `episode.md` is the sole optimization workflow prompt; its plans use `scratch/draft.md` and `scratch/plan.md`.

Do not add private evaluator details or reconstructed hidden cases to any prompt.
