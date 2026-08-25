---
name: release-model-package
description: Build, revise, validate, audit, or retire a versioned inference-weight delivery for a model repository. Use when packaging or publishing model weights, making a model independently deployable, producing safetensors/wheel/Docker/tar artifacts, defining an input-output contract, reproducing source-checkpoint inference, preparing a downstream handoff, or standardizing another release. Do not use this skill to infer model topology, licensing, upload rights, or repository commands without evidence.
---

# Release model package

Turn a verified model checkpoint or model family into a versioned, independently deployable, auditable
inference package. Keep the workflow generic; repository adapters supply paths, environments, model owners,
tests, contracts, and release mechanisms. A model-specific runtime and builder remain the source of topology
and numerical semantics.

## Repository adapter gate

Before acting, read the current repository's `.agents/skill-adapters/release-model-package.md` and validate:

- `adapter_version` is `1`, `skill` is `release-model-package`, `repository` is non-empty;
- every `repository_markers` entry is a repository-relative existing path;
- `capabilities` explicitly declares `inspect`, `build`, `audit`, `regression`, `retire`, and `update_docs`;
- the body contains non-empty `适用仓库`, `规则与权限`, `运行环境与临时路径`, `发布实现与 owner`,
  `验证矩阵`, `文档与证据`, and `拒绝条件` sections.

Missing or invalid adapter data blocks the corresponding capability. Capability is evidence that the repository
can support an action; it never grants user authorization for writes, uploads, publication, deletion, or retirement.

## Optional task Guard

Checksum closure is an existing release acceptance requirement, not speculative hardening. When Stop That Shit Guard
is armed, any build or audit that computes package or archive digests requires `hash=allow`. That contract permits
hashing only; it does not authorize building, writing outside `files=`, installing dependencies, uploading,
publication, or retirement.

## Workflow

### 1. Freeze a release charter

Read the adapter and its referenced repository contracts before choosing files or commands. Record:

- release ID and SemVer, audience, license/usage notice, redistribution and upload permission;
- exact source checkpoint set, model constructor/configuration, weight selection evidence, code revision;
- topology (single model, staged relay, ensemble, gate, feedback), public modes, cache/lazy-load semantics;
- input/output keys, shapes, axes, dtype, device, units/normalization, masks and horizon/batch bounds;
- normalization/preprocessing fingerprint, real evaluation window for golden data, numerical tolerances;
- target runtime, performance/memory gates, repository regression and Docker requirements;
- output directory, archive, checksum sidecar, internal report and old-version policy.

If authorization, source identity, input semantics, target platform, or a required acceptance threshold is unknown
and changes the resulting package, stop and ask the user. Do not infer license or upload permission from repository
visibility or phrases such as "open weights".

Use [assets/RELEASE_CHARTER.template.md](assets/RELEASE_CHARTER.template.md) as a working record. Keep internal
checkpoint paths, sample/run identities and selection details outside the public archive.

### 2. Prove the source model

For every candidate profile/stage/path, run real model inference on the target runtime and record finite outputs,
shapes, cold load, warm model-only inference, end-to-end latency and peak memory. Select weights from persisted
evaluation evidence and actual topology, never from a directory name.

### 3. Implement the independent boundary

Use repository adapter owners, normally a model runtime plus a model-specific export builder. Keep one stable
constructor and request method where possible:

```python
runtime = Runtime.from_pretrained(package_dir, device="cuda:0")
prediction = runtime.predict(inputs, mode="explicit-when-multiple")
```

Validate manifest and environment before loading large weights; validate checksums before strict-loading; reject
unsupported shapes, dtype/device, non-finite input, modes, horizons, missing files and incompatible runtime.
Builder output must use non-pickle weights and prove source tensor key/shape/dtype/value equivalence unless the
charter explicitly authorizes conversion and defines its error gate.

Do not expose training controls, arbitrary checkpoint replacement, raw training data, internal paths, or dynamic
batch/horizon behavior unless the contract explicitly requires them.

### 4. Build the minimum release tree

Use the adapter's owner and the following portable shape as a reference. The release charter decides which runtime,
weight, SDK, wheel, container and golden forms are required; remove inapplicable files rather than shipping empty
placeholders:

```text
<release-id>/
├── README.md
├── INPUT_OUTPUT_CONTRACT.md
├── DEPLOYMENT.md
├── MODEL_CARD.md
├── LICENSE | USAGE_NOTICE.md
├── Dockerfile / .dockerignore
├── release_manifest.json
├── checksums.sha256
├── normalization.json / preprocessing.json
├── weights/**/*.safetensors
├── dist/<runtime-wheel>.whl
├── sdk/<runtime-package>/**
├── fixtures/golden_input.* / golden_expected.*
└── examples/**
```

Keep `<release-id>.tar.gz`, its SHA256 sidecar and the internal build report outside the release directory.
Only manifest/checksum allowlisted files enter the archive; no symlinks, pickle checkpoints, logs, controls,
training data, identities, secrets or repository-absolute paths.

Use [assets/README.template.md](assets/README.template.md),
[assets/INPUT_OUTPUT_CONTRACT.template.md](assets/INPUT_OUTPUT_CONTRACT.template.md), and
[assets/RELEASE_CHARTER.template.md](assets/RELEASE_CHARTER.template.md) as starting points. Replace every
placeholder and remove irrelevant sections before delivery.

### 5. Run acceptance gates

Read [references/release-framework.md](references/release-framework.md) for ownership and package structure,
then [references/acceptance-gates.md](references/acceptance-gates.md) before testing. Run gates in order:

0. evidence freeze and source inference;
1. static tree, strict JSON, allowlist, checksums, safetensors, wheel, archive and security scan;
2. source checkpoint tensor equivalence and strict-load;
3. interface negative cases, topology/forward-count/rollout/mode/cache semantics;
4. source-runtime versus package-runtime golden values and task baseline;
5. clean wheel install with no repository `PYTHONPATH` leakage;
6. tar-to-empty-directory Docker build and README from-tar rehearsal;
7. adapter-mapped tests, release-specific tests, lint/type checks and knowledge synchronization;
8. rebuild final artifacts after the last change and audit the final directory and archive.

Run the portable audit script from this Skill directory:

```bash
python scripts/audit_release.py <release-dir> \
  --expected-release-id <release-id> \
  --require-directory-name-match \
  --require-feature safetensors \
  --require-feature wheel \
  --require-feature sdk \
  --require-feature golden \
  --require-feature docker \
  --archive <release-id>.tar.gz \
  --archive-sha256 <release-id>.tar.gz.sha256
```

Replace the feature flags with the charter's actual delivery forms. Use repeatable `--require-file` or
`--require-glob` for repository formats such as ONNX, TensorRT, MLX or a non-wheel runtime. The script always checks
base docs, license/usage terms, strict JSON, checksum closure, forbidden pickle suffixes and any safetensors, wheels
or archive that is present. It is a generic integrity floor, not proof of model numerical correctness or license
compliance. Preserve command, environment, exit code, target revision and key measurements for every required gate.
A failed required gate means the package is not deliverable.

### 6. Retire old versions only last

Do not delete source checkpoints. Retire or delete old release directories, archives, aliases and compatibility
branches only after the new version passes required gates and the user explicitly authorizes the exact scope. Keep
active compatibility logic near its owner with the repository's required compatibility marker and durable reference.

### 7. Report evidence and limits

Report release directory, archive and SHA256, public API, contract, source/package equivalence, golden tolerance,
clean-install and Docker results, performance/memory, security audit, mapped regressions, knowledge sync, untested
platforms/cache/network boundaries, and old-version disposition. Distinguish builder self-check, clean-environment
verification, and Docker-from-tar rehearsal. Local generation is not upload or publication.

## Non-negotiable boundaries

- Never place `.pt`, `.pth`, `.ckpt`, training data, logs, controls, sample/shot/fold/run identity, credentials,
  or internal absolute paths in the public package.
- Never quantize, lower precision, rename tensors, or alter preprocessing silently.
- Never use random input as the golden oracle; expected output must come from the source runtime.
- Never claim Docker cold-start is resident warm latency, or the reverse.
- Never deliver without explicit license/usage terms and a complete checksum/manifest closure. Require the charter's
  actual weight/runtime forms explicitly instead of assuming every repository uses safetensors, wheels or Docker.
- Never upload, push images, publish packages, or delete old releases without explicit user authorization.

## Bundled resources

- `scripts/audit_release.py`: generic tree/checksum/strict JSON/safetensors/wheel/tar audit; run it from the
  repository or Skill checkout as shown above.
- `references/release-framework.md`: owner boundaries, release tree, runtime contract, evidence, security and
  SemVer guidance.
- `references/acceptance-gates.md`: ordered acceptance gates and minimum final report table.
- `assets/*.template.md`: working templates; do not ship placeholders.
