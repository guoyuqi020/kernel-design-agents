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

`limits.optimizer_attempts` is a hard capacity, not permission to mint work. Normal multi-Branch
organizations must spend it exactly. Runtime also supports controlled Challenger-only evolution
topologies such as Isolated-Evolve and Retained-Evolve: the Active Branch is omitted, the sole
Challenger spends the exact configured single-Branch budget, and no same-Epoch Agent comparison is
performed.

The public SDK intentionally hides Attempt identities and the JSONL wire protocol. Use `create_pool`
to define a Branch's Trajectory count and number of rounds, then call `run_pools`. Every round starts
from each Trajectory's immutable initial State unless Workflow explicitly routes a completed
Attempt's `output_state` into that Trajectory's next round. Thus reset, retention, broadcast, and
conditional State flow are Workflow code rather than Runtime policy flags. An optional
`after_round` callback can inspect normalized outcomes and call `route_kernel` or `route_state`.
The private SDK deterministically translates each logical round into replay-safe Attempt identities,
while Runtime validates every State reference and remains responsible for materialization,
execution, evaluation, recovery, gates, persistence, selection, and cross-Epoch scheduling.
