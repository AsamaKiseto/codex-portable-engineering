# Model release acceptance gates

Run gates in order and preserve command, environment, exit code and key measurements in an internal report. A failed
required gate means the package is not deliverable; changes to release files restart at the earliest affected gate.

## Gate 0: Evidence freeze

Verify checkpoint identity, model configuration, normalization/preprocessing fingerprint, evaluation baseline and real
source-runtime inference. Stop when authority, input semantics, source identity or target platform is unknown.

## Gate 1: Static integrity

Use strict JSON, tree/allowlist/checksum closure, validation for the charter's selected weight/runtime formats, no
symlink/special/pickle files, security scan for identities, credentials and internal paths, and reproducible archive
checks. Configure the bundled generic audit with required feature/file/glob flags and run it in addition to
model-specific checks.

## Gate 2: Source weights

Map every public file to one source checkpoint. Strict-load with the source constructor and compare every tensor's key,
count, shape, dtype and value. For authorized conversion, use the charter's error and task gates rather than exactness.

## Gate 3: Interface and topology

Test missing/extra keys, bad shape/length/dtype/device, non-finite values, unsupported masks/modes/horizons, missing or
tampered files and runtime incompatibility. Verify staged ranges, forward count, history rolling, feedback, branch
independence and lazy-load/cache behavior.

## Gate 4: Golden values

Generate de-identified golden input from a real evaluation window. Generate expected outputs with the source runtime,
then compare all public keys/shapes/dtypes/finite masks and values in every mode. Align task metrics with frozen
evaluation evidence.

## Gate 5: Clean install

Install the wheel in a clean environment with no repository `PYTHONPATH`; run Python and CLI golden round trips and
verify output files, keys, shapes and dtypes.

## Gate 6: Docker and README

Verify archive first, build from an empty task directory with pinned image digest, run GPU/runtime checks, execute every
README command and record cache/network limitations honestly.

## Gate 7: Performance and regressions

Measure cold/load/warm model-only/end-to-end separately, p50/p95 as required, peak memory and each mode. Run adapter-
mapped tests, release-specific tests, lint/type checks and knowledge synchronization.

## Gate 8: Final archive and retirement

After the last release-file change, rebuild wheel/tar/checksums; audit final tree/archive and compare version identity.
Only then declare ready. Retire old versions only with explicit authorization; retain source training artifacts.

Final report rows: Release, Contract, Equivalence, Install, Docker, Performance, Security, Regression, Limits and
Retirement.
