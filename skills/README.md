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

No Skills are bundled by default. Add and index reusable procedures here when needed.

## Managed-session use

- The injected hardware architecture, DSL, Gateway, and workspace contracts are authoritative over any added Skill's examples.
- GPU execution and profiler collection use the supplied Gateway tools. Reuse matching measurements and collect only evidence needed for the decision.
- No global Skill/plugin installation is needed. Keep durable additions indexed here and temporary outputs under `scratch/`.
