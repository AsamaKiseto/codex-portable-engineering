# Model release framework

## 1. Charter

Before implementation, record release identity, authority/license, exact source checkpoints, topology, public
input/output, runtime, evidence, acceptance thresholds, delivery artifacts and old-version policy. Mark unknown
fields `blocked`; do not infer them.

## 2. Ownership

- Repository runtime: public API, validation, construction, rollout/fusion, normalization, lazy loading, cache and
  compatibility errors.
- Model-specific builder: checkpoint extraction, tensor equivalence, golden generation, manifest, wheel, docs,
  security scan, reproducible archive and internal report.
- Minimal SDK: independently installable runtime source; it must not import repository source paths.
- Release assets: Dockerfile, README, contract, deployment, model card, usage/license and examples.
- Portable audit: generic tree, strict JSON, checksum, non-pickle weight, wheel/tar closure and obvious leakage;
  it does not prove model semantics.

Do not abstract model-specific topology into a cross-repository framework until a second release demonstrates stable
model-independent logic. Keep topology and numerical semantics with the model owner.

## 3. Release tree

Always include README, input/output contract, usage/license terms, manifest and checksum closure. Select deployment,
model card, normalization/preprocessing, weight format, SDK/package, golden, container and examples from the repository
contract and release charter. Safetensors, wheels and Docker are supported forms, not cross-repository assumptions.
Keep archive and internal report outside the tree.

## 4. Runtime contract

Prefer one constructor and request method. Validate manifest and static files before large weight loads, checksums
before strict-load, and all input/output shape, dtype, finite, mode, mask, device and horizon rules. Fix staged relay,
ensemble, gate, feedback, forward-count, lazy-load and cache semantics in manifest and tests.

## 5. Weight and evidence handling

Record source checkpoint digest and private locator only in the internal report; expose public profile/stage names.
Extract only explicit model/state-dict tensor fields. Compare tensor keys, count, shape, dtype and exact values after
conversion. If conversion is authorized, record method, error budget and task-level regression instead of claiming
exact equivalence. Generate golden input from a real de-identified evaluation window and expected output with the
source runtime.

## 6. Build and security

Use deterministic archive paths/order, fixed metadata and gzip time. Reject symlinks, special files, pickle artifacts,
unregistered files, logs, training/evaluation artifacts, secrets and internal locators. Checksums cover every regular
file except their own file. Default output is local; registry, Hub, PyPI, GitHub, object storage and image pushes are
separate external side effects.

## 7. Versioning and retirement

PATCH is documentation/build-only, MINOR is backward-compatible capability, and MAJOR changes API, manifest, weight
topology, default semantics or compatibility. Rebuild all derived artifacts after any final change. Retire old
releases only after required gates pass and the user authorizes the exact deletion/alias scope.
