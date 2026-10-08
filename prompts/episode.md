# Kernel optimization attempt

You are working in a task implementation workspace. Your job is to produce the best correct implementation for the task described below.

## Task Contract

- Task name: the operator in the injected Trusted task context.
- Objective: improve the incumbent Kernel while preserving the Public operator contract.
- Correctness requirements: the public semantics, ABI, tolerances, and invariants; exact evaluation cases remain private.
- Performance or quality target: improve measured performance across the evaluation domain, not a reconstructed hidden case table.
- Allowed implementation approaches: the injected DSL is binding; do not introduce another DSL or a fallback implementation.
- Validation command: save `{"operation":"evaluate","latency_prediction":"retained"}` to `scratch/evaluate.json` (replace the prediction with your actual expectation), then run `python3 agent/optimizer/src/runtime_tools.py gateway-execute --request scratch/evaluate.json`.
- Evaluation command: the same full Evaluate measures correctness and performance for the exact current `work/kernel/` tree. Check and Dev are diagnostic probes, not final validation.
- Promotion criteria: nominate a correctly evaluated candidate with credible evidence; the controller applies retention and promotion policy, not the Agent's conclusion.

## Workflow

1. Read the repository structure, existing implementation, tests, and task documentation available in this workspace.
2. Identify the baseline behavior and the validation path. Recover only relevant history and reuse matching trusted measurements. For exact historical source, register an explicit `adopt` decision with real before/after Result Artifact digests; Runtime validates its successful ordinary full-Evaluate evidence without changing the original Trial's ownership.
3. Research only the references needed for this task.
4. Write an implementation-plan draft to `scratch/draft.md`.
5. Turn the draft into an executable plan before editing code; keep it in `scratch/plan.md`.
6. Implement one candidate at a time.
7. Run validation after each meaningful candidate, reusing an existing matching result rather than repeating the same measurement.
8. Record candidate results, parent relationships, and evidence through the supplied Journal tools as work proceeds.
9. Keep the final change scoped to the task contract.

## Plan Draft Requirements

Keep the draft in `scratch/draft.md` brief:

- The chosen change and expected effect, separating baseline facts from assumptions.
- The main risks and unknowns, and the last viable candidate to restore.
- The next concrete edit or focused probe.
- The next validation command and evidence that would support or reject the change.

Do not start implementation until the draft exists. A concise draft and executable plan are sufficient.
Once a step is actionable, write the change or run the focused probe instead of expanding the
entire design. For a complex rewrite, first save the smallest end-to-end implementation that can
be checked against the public contract, then add optimizations incrementally. Do not wait to
resolve every layout, pipeline, and boundary question before the first implementation or probe.
Keep `scratch/plan.md` current with the next step. After an interruption, inspect the saved source
and plan and continue from them; do not restart the entire design without new evidence.

## Execution and evidence

- Edit candidate code only under `work/kernel/`. Use `scratch/` for temporary plans, probe scripts, requests, profiler extracts, and logs. The injected workspace contract defines the read-only inputs and reusable directories.
- Route GPU execution, compilation, JIT, benchmarking, profiling, and disassembly through `gateway-execute`. Skill examples teach analysis methods; they do not authorize local GPU execution, dependency installation, service changes, or hidden-case reconstruction.
- For a multi-line remote probe, write a script under `scratch/` and pass it in Dev `file_paths`; do not embed the script in the command string. Use `python3` for Python commands.
- Register and start a Direction with `update-direction` when beginning its research or exploration, not only when editing the Kernel. Follow the shared tool contract for the single in-progress Direction and per-Attempt limits.
- After every decisive measured keep, restoration, or direction-ending result, call `record-experiment` before another edit. Supply the exact before/after Result Artifact digests; Runtime resolves their Kernel and Result Artifacts. Separate factual evidence from analysis. Negative results are first-class evidence.
- Use relevant included Skills and references for research or report analysis. Local Skill references are not measurements of the current candidate.
- Treat `prompts/` and `skills/` as read-only Agent Revision content. Use applicable Skills, but
  record task-specific hypotheses, evidence, and conclusions in the Runtime Direction
  and Experiment Journal. Only reusable executable helpers belong in writable `tools/`; update its
  index whenever a Tool is added, changed, renamed, or removed. Evolver—not this
  Optimizer session—may curate only task-independent Prompts, Skills, and Tools from completed
  Session evidence. It does not choose Kernel optimization directions.

## Terminal handoff

Build the terminal Report incrementally during experiments. Submit it with `attempt-report` using the shared tool schema; correct validation errors and resubmit when needed. Close every in-progress Direction before a successful handoff. Stop with an evaluated candidate, an exhausted or reverted direction, or a genuine blocker; never invent measurements to finish. Chat text or a local benchmark log does not replace the terminal Report.

An exact restored Kernel may be nominated using a Runtime-accepted `adopt` decision that binds
matching historical full-Evaluate evidence; do not rerun it just to obtain a new Result Artifact digest.
Agent ABBA remains exploratory and cannot replace ordinary full-Evaluate evidence. Runtime's
authoritative ABBA runs only after terminal Report handoff and does not create an Agent Trial;
do not wait for that later comparison to record an Experiment or submit the Report.
`blocked` or `pivot` may have zero Experiments and empty Findings. Before handoff, close
started Directions with an honest stopping reason and `hypothesis_status`; unmeasured or inconclusive
work can close `unresolved` with empty support, even without a Gateway call. Select relevant
Experiment IDs or direct `supporting_results` only when evidence exists. No diagnostic call or
fabricated record is required to finish. Lifecycle is not a verdict:
untested reasoning stays unresolved. Preserve this distinction in Findings, memory, and Skills;
never promote incidental interpretations in unrelated Experiments into established constraints.
Never fabricate evidence to exit.
