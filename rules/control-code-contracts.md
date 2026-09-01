## Parameter ownership and interface control

- Treat every new configuration key, CLI flag, environment variable, public function or constructor parameter, and `Context`/`Settings`/dataclass field as an API expansion. Default to rejecting the expansion.
- Before adding an interface, identify its only owner and real consumer, prove that it is per-step state/forcing or that maintained cases need different values, and show that it cannot be derived from existing authoritative data or kept as an immutable implementation constant. An explicit user requirement can supply the case-variation evidence.
- Do not expose production parameters only to accelerate tests. Change test fixtures, input size, or test-only helpers instead.
- Parse configuration and machine resources once on the host, reject unknown keys, and pass only the smallest typed immutable snapshot actually consumed. Do not retain both a configuration/resource object and copies of its fields.
- Do not use `dict`, `**kwargs`, pass-through properties/functions, forwarding-only wrappers, or synonymous names to conceal interface size.
- A refactor whose purpose is to reduce interface or ownership complexity must not increase public interface counts without explicit user approval. Report before/after counts and any justified exception.
- Use the `$control-code-contracts` skill for parameter-ownership audits, interface refactors, configuration-schema changes, and numerical-validation changes.

## Numerical contracts and algorithm predicates

- Never delete or weaken structural contracts merely to reduce code size. Preserve checks for required fields, array rank and shape, explicitly permitted broadcasting, aligned dimensions/names, valid index ranges, and other structure needed to prevent valid-looking but incorrect execution.
- Preserve algorithm predicates that define correctness or atomic state transitions: convergence, finite-value detection, step acceptance or backtracking, topology classification, and division-by-zero or singular-denominator protection.
- Do not rely on a later crash, residual, or visible wrong result when an earlier structural contract prevents silent broadcasting, misalignment, invalid indexing, or corrupted accepted state.
- Place each contract at its earliest authoritative boundary and give it one owner. Remove only demonstrably duplicate checks, not independent checks of dynamic values that can change after validation.
- Do not add public tolerances or switches solely for validation. Reuse the algorithm's existing semantic tolerance, or use a private immutable constant when the threshold is an implementation invariant.
- Keep diagnostics that are externally consumed, but do not turn informational plausibility metrics into rejection predicates without an explicit algorithmic requirement.
- For JAX/JIT code, keep host-checkable structure validation outside compiled loops and retain dynamic predicates inside the kernel using JAX-compatible control flow. Preserve eager/JIT agreement, differentiability, PyTree structure, and atomic acceptance semantics.
