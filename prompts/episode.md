# Kernel optimization attempt

You are working in a task implementation workspace. Your job is to produce the best correct implementation for the task described below.

## Task Contract

- Task name: the operator in the injected Trusted task context.
- Objective: improve the incumbent Kernel while preserving the Public operator contract.
- Correctness requirements: the public semantics, ABI, tolerances, and invariants; exact evaluation cases remain private.
- Performance or quality target: improve measured performance across the evaluation domain, not a reconstructed hidden case table.
- Allowed implementation approaches: the injected DSL is binding; do not introduce another DSL or a fallback implementation.
- Validation command: save `{"operation":"evaluate"}` to `scratch/evaluate.json`, then run `python3 agent/optimizer/src/runtime_tools.py gateway-execute --request scratch/evaluate.json`.
- Evaluation command: the same full Evaluate measures correctness and performance for the exact current `work/kernel/` tree. Check and Dev are diagnostic probes, not final validation.
- Promotion criteria: nominate a correctly evaluated candidate with credible evidence; the controller applies retention and promotion policy, not the Agent's conclusion.

## Workflow

1. Read the repository structure, existing implementation, tests, and task documentation available in this workspace.
2. Identify the baseline behavior and the validation path. Recover only relevant history and reuse matching trusted measurements. For exact historical source, register an explicit `adopt` decision with real before/after Trial IDs; Runtime validates its successful ordinary full-Evaluate evidence without changing the original Trial's ownership.
3. Research only the references needed for this task.
4. Write an implementation-plan draft to `scratch/draft.md`.
5. Turn the draft into an executable plan before editing code; keep it in `scratch/plan.md`.
6. Implement one candidate at a time.
7. Run validation after each meaningful candidate, reusing an existing matching result rather than repeating the same measurement.
8. Record candidate results, parent relationships, and evidence through the supplied Journal tools as work proceeds.
9. Keep the final change scoped to the task contract.

## Plan Draft Requirements

The draft in `scratch/draft.md` should include:

- The current baseline and how it is validated.
- The main risks and unknowns.
- Candidate implementation directions ranked by expected value and risk.
- The first concrete implementation steps.
- The exact validation and evaluation commands to run.
- The evidence required to promote, revise, or reject a candidate.

Do not start implementation until the draft exists. A concise draft and executable plan are sufficient.

## Execution and evidence

- Edit candidate code only under `work/kernel/`. Use `scratch/` for temporary plans, probe scripts, requests, profiler extracts, and logs. The injected workspace contract defines the read-only inputs and reusable directories.
- Route GPU execution, compilation, JIT, benchmarking, profiling, and disassembly through `gateway-execute`. Skill examples teach analysis methods; they do not authorize local GPU execution, dependency installation, service changes, or hidden-case reconstruction.
- For a multi-line remote probe, write a script under `scratch/` and pass it in Dev `file_paths`; do not embed the script in the command string. Use `python3` for Python commands.
- Register and start a Direction with `update-direction` when beginning its research or exploration, not only when editing the Kernel. Follow the shared tool contract for the single in-progress Direction and per-Attempt limits.
- After every decisive measured keep, restoration, or direction-ending result, call `record-experiment` before another edit. Supply the exact before/after Kernel Trial IDs; Runtime resolves their Kernel and Result Artifacts. Separate factual evidence from analysis. Negative results are first-class evidence.
- Use relevant included Skills and references for research or report analysis. Local Skill references are not measurements of the current candidate.
- Treat `prompts/`, `insights/`, and `skills/` as read-only Agent Revision content. Use applicable
  Skills and Insights, but record new hypotheses, evidence, and conclusions in the Runtime Direction
  and Experiment Journal. Only reusable executable helpers belong in writable `tools/`; update its
  index whenever a Tool is added, changed, renamed, or removed. Evolver—not this
  Optimizer session—curates Prompts, Insights, and Skills from completed Session evidence.

## Terminal handoff

Build the terminal Report incrementally during experiments. Submit it with `attempt-report` using the shared tool schema; correct validation errors and resubmit when needed. Close every in-progress Direction before a successful handoff. Stop with an evaluated candidate, an exhausted or reverted direction, or a genuine blocker; never invent measurements to finish. Chat text or a local benchmark log does not replace the terminal Report.

An exact restored Kernel may be nominated using a Runtime-accepted `adopt` decision that binds
matching historical full-Evaluate evidence; do not rerun it just to obtain a new Trial ID.
Agent ABBA remains exploratory and cannot replace ordinary full-Evaluate evidence. Runtime's
authoritative ABBA runs only after terminal Report handoff and does not create an Agent Trial;
do not wait for that later comparison to record an Experiment or submit the Report.
When no experiment was completed, `blocked` or `pivot` permits zero Experiments and empty Findings.
Close any `in_progress` Direction with `block` or `defer` first; never fabricate evidence to exit.
