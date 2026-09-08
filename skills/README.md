# Skills index

Store reusable procedures: when to apply a method, its steps, prerequisites, and validation criteria.
Use knowledge/ for reference knowledge, memory/ for search lessons, and tools/ for executable scripts.

For CLI discovery, use `<skill-name>/SKILL.md` with YAML `name` and `description` frontmatter;
place supporting scripts/references inside that Skill directory. Before each Claude/Codex
Optimizer or Bootstrap session, Runtime copies these Skill directories into its private CLI Home.
Loose notes and README files are not registered Skills. Edit the originals here for persistence;
installed copies are session-local and refreshed at the next launch.

Whenever you add, change, rename, or remove a Skill, update this README with its path, purpose,
trigger conditions, dependencies, and limitations. Read this index before adding duplicates.
Keep Skills concise and general where possible; do not store credentials or raw traces.

## Contents

- `ncu-report-skill/SKILL.md`: Nsight Compute analysis workflow, diagnosis playbook, report templates, and helper scripts. Use when actual profiler evidence can resolve an implementation question.

## Managed-session use

The included Skill is a pinned upstream snapshot. Keep its reference material intact and read only what the current question needs.

- The injected hardware architecture and DSL are authoritative. B200/SM100 examples do not mean the current device is B200; do not assume SM100-only instructions work on SM120 or another target.
- For profiler collection use `gateway-execute` with `operation="profile"` and the supported level, source, and selection options. Do not run local `ncu`, compile a harness locally, or install Nsight dependencies. Do not assume two full/source profiles are always necessary; reuse existing matching measurements and collect only evidence needed for the decision.
- Upstream `profile/<run_name>/` paths become `scratch/profile/<run_name>/`. Select inputs only from public domains or the supported opaque `shape_id`, not guessed hidden cases.
- `ncu_report` helpers require a real accessible report file and the matching Nsight Python module. A normalized Gateway Profile result does not promise either. Analyze its returned metrics when that is the evidence available; if more is needed, use a supported remote Dev probe or report the missing capability. Never invent a local report path or silently install dependencies.
- No global Skill/plugin installation is needed. Keep durable additions indexed here and temporary outputs under `scratch/`.
