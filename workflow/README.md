# Epoch Workflow

Every file in this directory is versioned Agent code. Runtime executes the program selected by the
Active Agent Revision's `atrex-bundle.json` once per Epoch. A program implements
`run_epoch(epoch: EpochRuntime)` and hands it to `serve`; it cannot start another Epoch. The SDK in
`runtime.py` lets that function create Branch-local Pools, advance synchronized rounds, inspect
trusted outcomes, route accepted Kernels or compatible State into the next round, and complete the
current Epoch.

Runtime remains authoritative for the fixed resource envelope, Attempt execution, Gateway access,
evaluation, recovery, comparison, promotion, and durable state. Workflow code receives no Registry,
Gateway credential, hidden-Test, or arbitrary process-launch authority.

`main.py` is the only Workflow entry carried by this Agent Revision. Runtime constructs controlled
production and ablation revisions by materializing the selected external template as `main.py`;
alternative arm implementations are not included in the Bundle or shown to Evolver. Repeated
control instances have independent Lineage-local Agent Revision identities even when Runtime
materializes the same initial program.

Every organization must spend `limits.optimizer_attempts` exactly. A program may change topology,
but it cannot mint additional Attempts.

The public SDK intentionally hides Attempt ordinals and the JSONL wire protocol. Use `create_pool`
to define a Branch's Trajectory count, number of rounds, and State policy, then call `run_pools`.
An optional `after_round` callback can inspect normalized outcomes and call `route_kernel` or
`route_state` for the next round. The private SDK layer deterministically translates each logical
round into replay-safe Attempt identities, so a Workflow restart replays completed rounds without
duplicating work. Runtime validates every route and remains responsible for execution, evaluation,
recovery, gates, persistence, selection, and cross-Epoch scheduling.
