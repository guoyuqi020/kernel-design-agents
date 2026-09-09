# Agent Instructions

Keep reusable Agent methods small and task-agnostic. In a managed task session, the injected phase, workspace, task, and tool contracts define the execution boundary; the rules below describe how to work within it.

## Repository Rules

- Use English for repository-facing files, comments, documentation, prompts, and commit messages.
- Keep task-specific datasets, validators, benchmark logs, and candidate artifacts out of reusable Agent directories. Candidate implementation belongs in `work/kernel/`.
- Treat benchmark competitions, including MLSys-style work, as downstream tasks rather than the scope of reusable methods.
- Put temporary generated outputs, plans, and profile extracts in `scratch/`.
- Prefer documenting reusable workflow mechanics over documenting one task's private harness or acceptance thresholds.

## Phase instructions

Follow the supplied phase prompt for planning, implementation, evidence recording, and terminal handoff. Optimization uses `prompts/episode.md`; Bootstrap follows its separately supplied baseline workflow. Work in the prepared workspace and use the supplied task and tool contracts rather than redefining them.

## Optional Skills

Use available skills only when they are relevant to the active task:

- A domain knowledge skill for background research.
- A profiling or report-analysis skill for performance evidence.

No Skills are bundled by default. Consult `skills/README.md` for procedures added to the current task's reusable State and their managed-session paths. Do not install plugins or modify global CLI configuration.

The supplied hardware and DSL override Skill examples. Any added procedures must follow the supplied Gateway, measurement-reuse, and workspace contracts.
