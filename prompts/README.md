# Prompts index

This directory stores versioned phase prompts and the shared tool protocol. It is read-only in
managed Optimizer and Bootstrap sessions; Evolver may revise it for a later Agent Revision.

Whenever you add, change, rename, or remove a prompt, update this README with its path, purpose, and dependencies. Preserve configured phase paths. Keep temporary requests and raw traces in scratch/, not here.

## Available Templates

| Path | Purpose |
|---|---|
| `episode.md` | Executed optimization prompt, including explicit adoption of matching historical evidence; depends on the shared Session tools and trusted Runtime Journal/evaluation contract. |
| `framework_baseline.md` | First correct DSL implementation and honest blocked handoff without fabricated experiments; depends on the shared Report schema and Runtime Bootstrap validation. |
| `generalize_agent_problem.md` | Public operator-contract generation, without hidden evaluator cases. |
| `attempt-tools.md` | Exact CLI, Journal, and terminal Report contracts shared by Bootstrap and Attempts, including the 1 MiB request limit, paired input/Shape examples, exploratory versus authoritative ABBA, historical `adopt` decisions, zero-experiment blocked/pivot reports, and local file-error repair; depends on `src/runtime_tools.py`, `src/tool_contracts.py`, and the trusted Runtime request/report contracts. |

## How To Use

Managed sessions load the configured phase prompt automatically. `episode.md` is the sole optimization workflow prompt; its plans use `scratch/draft.md` and `scratch/plan.md`.

Do not add private evaluator details or reconstructed hidden cases to any prompt.
