# <release-id> input/output contract

## Public API

List the constructor, request method and CLI. For multiple modes, state whether mode is explicit and whether a default
exists.

## Input

For every field list name, container, shape, axes, dtype, device, normalized/physical representation, units, complete
channel order, time alignment, finite/range rules, missing/mask behavior and required status. State rejected fields
and implicit conversion policy.

## Inference semantics

Document batch/horizon, stage/rollout/ensemble/gate, forward count, history rolling, teacher forcing, feedback,
lazy-load/cache and precision. Delete inapplicable subsections.

## Output

List every output field's name, shape, axes, dtype, device, representation, units/denormalization, finite or allowed
NaN positions, masks and ordering guarantees.

## File protocol

List input/output file formats, keys, forbidden extra keys, compression/endianness/allow_pickle policy and CLI examples.

## Errors and versions

List contract, integrity and compatibility errors, failure timing, manifest schema, current release ID, supported
compatibility versions and explicit unsupported platform/precision/batch/horizon/preprocessing ranges.
