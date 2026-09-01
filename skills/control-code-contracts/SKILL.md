---
name: control-code-contracts
description: Audit and refactor parameter ownership, configuration interfaces, contexts, and numerical validation without weakening structural contracts or algorithm predicates. Use when changing function or constructor parameters, dataclass/Context/Settings fields, configuration or CLI schemas, option whitelists, JAX/JIT kernel inputs, solver validation, acceptance logic, or scientific/numerical code; also use for parameter-bloat, ignored-configuration, forwarding-interface, duplicate-state, or excessive-check reviews. Do not use for edits that cannot affect an interface or a numerical contract.
---

# Control Code Contracts

Reduce real freedom, duplicate ownership, and forwarding layers while retaining the contracts that prevent silent numerical corruption.

## Establish evidence before editing

1. Inspect repository instructions, the dirty worktree, maintained configurations, callers, consumers, tests, restart formats, and output contracts. Preserve unrelated work.
2. Record baseline counts for public configuration keys, CLI flags, context/settings fields, long function signatures, and non-State data containers. Do not use line count alone as the interface metric.
3. Trace each candidate from construction to its final numerical or external consumer. Do not delete from names or reference counts alone.

For every parameter or stored field, classify it as exactly one of:

- A: per-step runtime state or forcing;
- B: a physical, training, optimization, or experimental value that maintained cases genuinely vary;
- C: case-static configuration loaded once by its host owner;
- D: machine-static resource loaded once by its resource owner;
- E: immutable implementation constant;
- F: value derivable from authoritative A-E data;
- G: output, diagnostic, persistence, or restart contract.

Keep A and B as explicit typed interfaces. Let C and D have one host-side owner. Internalize E, derive F, and retain G only when an actual consumer exists.

## Gate interface additions

Before adding or retaining an interface, answer:

1. Who is the unique owner and final consumer?
2. Which maintained cases require distinct values, or what explicit requirement demands it?
3. Can existing state, configuration, or resources derive it?
4. Is it only a test-speed control or speculative future option?
5. Does it duplicate a value held by an engine, plan, settings object, context, or state?
6. Will removal change a JAX static signature, numerical result, public API, output, or restart format?

Reject the interface when the answers do not establish a real degree of freedom. Do not replace removed fields with nested wrappers, generic mappings, `**kwargs`, forwarding-only properties/functions, or aliases.

Parse strict configuration once on the host. Reject unknown and removed keys. Pass a minimal typed immutable snapshot to kernels. Do not store both the source object and expanded copies.

## Classify numerical validation

Classify every numerical check by its semantics rather than by its size:

- **Structural contract:** required fields; rank, exact or compatible shape; intentionally allowed broadcasting; dimension/name alignment; index bounds; valid structural resource layout. Retain it at the earliest authoritative boundary. Reject accidental broadcasting explicitly.
- **Algorithm predicate:** convergence, finite-value detection, step acceptance/backtracking, topology classification, denominator protection, or another condition that determines a branch, rollback, or accepted state. Retain it where the dynamic value is produced or committed.
- **External diagnostic contract:** emitted or persisted information consumed by users, acceptance tooling, monitoring, or restart. Retain the contract without making it a rejection predicate unless required.
- **Redundant or speculative check:** a duplicate with the same owner and same inputs, or an informational plausibility test with no consumer and no algorithmic effect. Remove or keep test-only as appropriate.

Do not treat eventual nonconvergence or a later failure as a replacement for a structural contract. A broadcast, misaligned dimension, or bad index can continue running and silently produce a wrong result.

Do not create a new public tolerance or switch merely to support a check. Reuse a tolerance that already defines solver semantics. Use a private immutable constant only for a true implementation invariant. If a check is dynamic inside JAX/JIT, implement it with JAX-compatible operations and preserve differentiability and atomic acceptance.

## Make reductions in order

Apply the smallest evidence-backed changes in this order:

1. dead and write-only fields;
2. derived duplicates;
3. repeated configuration or resource copies;
4. fixed options and test-only production controls;
5. forwarding-only interfaces and wrappers;
6. only then, duplicate or speculative numerical checks.

After each class, run focused tests. Do not add broad feature tests when a narrow structural or regression test proves the changed contract.

## Verify

Run the repository's syntax, lint, type, and focused unit checks. Add or retain focused negative tests for wrong rank/shape, missing required fields, accidental broadcasting, invalid indices, nonfinite values, nonconvergence, rejected steps, topology failure, and zero denominators when those paths are relevant to the change.

For JAX/JIT changes, compare eager and JIT results, PyTree structure, accepted state, and differentiation behavior. For persistence changes, test restart compatibility. Reject stale deleted keys and search for residual accesses.

Report:

- interfaces deleted, internalized, derived, retained, and added;
- structural contracts and algorithm predicates retained or moved;
- duplicate/speculative checks removed;
- before/after interface counts;
- numerical, JIT, and restart verification performed and any unverified scope.
