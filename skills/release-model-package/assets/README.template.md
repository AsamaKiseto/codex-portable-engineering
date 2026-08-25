# <release-id>

State the model capability, target platform, precision, batch/horizon and the one input file/request to one output
file/response boundary. Link the input/output contract and usage/license notice.

## Verify and extract

```bash
sha256sum -c <release-id>.tar.gz.sha256
tar -xzf <release-id>.tar.gz
cd <release-id>
```

Write the success marker and stop conditions for checksum failure.

## Host and image

Document OS/arch, GPU/driver, Docker and toolkit requirements, network/offline dependencies, and a pinned base-image
digest. Show the build command and image identity check.

## Golden self-check

Provide complete commands that create a writable output directory, run each public mode and compare expected values in
the same image. Print a unique `PASSED` marker only after keys, shapes, dtypes and tolerance checks pass.

## Business input and inference

List required keys, shapes, dtype, axes/channels/time, normalization, masks, finite rules and mode semantics. Provide
a real-input example, complete Docker commands and output inspection for every mode.

## Resident Python API and troubleshooting

Show wheel installation and a constructor reused across predictions. Distinguish Docker cold start from resident warm
latency. Cover bind-mount permissions, GPU visibility, runtime compatibility, contract errors, checksum failures and
offline dependency behavior.

## Documentation index

Link contract, deployment, model card, manifest, normalization/preprocessing, checksums and usage/license files.
