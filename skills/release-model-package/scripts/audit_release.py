#!/usr/bin/env python3
"""Audit a release tree and optional tar archive using repository-neutral checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

BASE_REQUIRED_FILES = {
    "INPUT_OUTPUT_CONTRACT.md",
    "README.md",
    "checksums.sha256",
    "release_manifest.json",
}
FEATURES = (
    "deployment-doc",
    "docker",
    "golden",
    "model-card",
    "safetensors",
    "sdk",
    "wheel",
)
PICKLE_SUFFIXES = {".pt", ".pth", ".ckpt", ".pkl", ".pickle"}
TEXT_NAMES = {"Dockerfile", ".dockerignore"}
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".sha256", ".toml", ".txt", ".yaml", ".yml"}
DEFAULT_FORBIDDEN = (
    r"/(?:home|workspace|workspaces|project|root)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+",
    r"\b(?:shot|sample)[_-]?(?:id|number)\s*[:=]\s*[\"']?[A-Za-z0-9_.-]+",
    r"\bfold[_-]?\d+\b",
    r"\b20\d{6}[_-]\d{6}\b",
)


class AuditError(RuntimeError):
    """Raised when a release violates the portable integrity floor."""


def _strict_json(path: Path) -> object:
    def reject_constant(value: str) -> object:
        raise ValueError(f"non-strict JSON constant: {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        payload: dict[str, object] = {}
        for key, value in pairs:
            if key in payload:
                raise ValueError(f"duplicate JSON key: {key}")
            payload[key] = value
        return payload

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid strict JSON: {path}: {exc}") from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _release_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise AuditError(f"symlink is forbidden: {relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise AuditError(f"special file is forbidden: {relative}")
        files[relative] = path
    return files


def _parse_checksums(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", raw_line)
        if match is None:
            raise AuditError(f"invalid checksum line {line_number}: {raw_line!r}")
        digest, relative = match.groups()
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or relative in records:
            raise AuditError(f"unsafe or duplicate checksum path: {relative}")
        records[relative] = digest
    if list(records) != sorted(records):
        raise AuditError("checksums.sha256 entries are not sorted")
    return records


def _validate_safetensors(path: Path) -> None:
    with path.open("rb") as handle:
        prefix = handle.read(8)
        if len(prefix) != 8:
            raise AuditError(f"truncated safetensors file: {path}")
        header_length = int.from_bytes(prefix, "little")
        if header_length <= 2 or header_length > path.stat().st_size - 8:
            raise AuditError(f"invalid safetensors header length: {path}")
        try:
            header = json.loads(handle.read(header_length).decode("utf-8"))
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            raise AuditError(f"invalid safetensors header: {path}: {exc}") from exc
    if not isinstance(header, dict):
        raise AuditError(f"safetensors header is not an object: {path}")
    tensors = [key for key in header if key != "__metadata__"]
    if not tensors:
        raise AuditError(f"safetensors contains no tensors: {path}")
    data_length = path.stat().st_size - 8 - header_length
    ranges: list[tuple[int, int, str]] = []
    for name in tensors:
        record = header[name]
        if not isinstance(record, dict) or not isinstance(record.get("dtype"), str):
            raise AuditError(f"invalid safetensors tensor metadata: {path}: {name}")
        shape = record.get("shape")
        offsets = record.get("data_offsets")
        if (
            not isinstance(shape, list)
            or not all(isinstance(value, int) and value >= 0 for value in shape)
            or not isinstance(offsets, list)
            or len(offsets) != 2
            or not all(isinstance(value, int) for value in offsets)
        ):
            raise AuditError(f"invalid safetensors shape/offsets: {path}: {name}")
        start, stop = offsets
        if start < 0 or stop < start or stop > data_length:
            raise AuditError(f"out-of-range safetensors offsets: {path}: {name}")
        ranges.append((start, stop, name))
    previous_stop = 0
    for start, stop, name in sorted(ranges):
        if start != previous_stop:
            raise AuditError(f"gapped or overlapping safetensors data: {path}: {name}")
        previous_stop = stop
    if previous_stop != data_length:
        raise AuditError(f"unclaimed trailing safetensors data: {path}")


def _scan_text(files: dict[str, Path], patterns: tuple[re.Pattern[str], ...]) -> None:
    for relative, path in files.items():
        if path.name not in TEXT_NAMES and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise AuditError(f"declared text file is not UTF-8: {relative}") from exc
        for pattern in patterns:
            match = pattern.search(content)
            if match is not None:
                excerpt = match.group(0)[:120]
                raise AuditError(f"forbidden path/identity pattern in {relative}: {excerpt!r}")


def _validate_archive(archive: Path, root: Path, files: dict[str, Path]) -> None:
    expected_files = [f"{root.name}/{relative}" for relative in sorted(files)]
    expected_directories = {
        root.name,
        *[
            f"{root.name}/{path.relative_to(root).as_posix()}"
            for path in root.rglob("*")
            if path.is_dir()
        ],
    }
    with tarfile.open(archive, "r:gz") as handle:
        all_members = handle.getmembers()
        for member in all_members:
            pure = PurePosixPath(member.name)
            if pure.is_absolute() or ".." in pure.parts:
                raise AuditError(f"unsafe archive member path: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise AuditError(f"archive symlink or special member is forbidden: {member.name}")
            if member.isdir() and member.name.rstrip("/") not in expected_directories:
                raise AuditError(f"archive contains an extra directory: {member.name}")
        members = [member for member in all_members if member.isfile()]
        if [member.name for member in members] != expected_files:
            raise AuditError("archive file members differ from the sorted release tree")
        for member, relative in zip(members, sorted(files), strict=True):
            extracted = handle.extractfile(member)
            if extracted is None:
                raise AuditError(f"cannot read archive member: {member.name}")
            digest = hashlib.sha256()
            while chunk := extracted.read(1024 * 1024):
                digest.update(chunk)
            if digest.hexdigest() != _sha256(files[relative]):
                raise AuditError(f"archive content differs from release tree: {member.name}")


def audit(args: argparse.Namespace) -> dict[str, object]:
    root = args.release_dir.expanduser().resolve()
    if not root.is_dir():
        raise AuditError(f"release directory does not exist: {root}")
    files = _release_files(root)
    missing = BASE_REQUIRED_FILES - files.keys()
    if missing:
        raise AuditError(f"required release files are missing: {sorted(missing)}")
    if not ({"LICENSE", "LICENSE.md", "USAGE_NOTICE.md"} & files.keys()):
        raise AuditError("release must contain LICENSE, LICENSE.md, or USAGE_NOTICE.md")

    for relative in args.require_file:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or relative not in files:
            raise AuditError(f"required file is missing or unsafe: {relative}")
    for pattern in args.require_glob:
        pure = PurePosixPath(pattern)
        if pure.is_absolute() or ".." in pure.parts:
            raise AuditError(f"required glob is unsafe: {pattern}")
        if not any(PurePosixPath(relative).match(pattern) for relative in files):
            raise AuditError(f"required glob matched no release file: {pattern}")

    # Adapters opt into delivery features; any artifact that is present is still validated below.
    for feature in args.require_feature:
        if feature == "deployment-doc" and "DEPLOYMENT.md" not in files:
            raise AuditError("required feature deployment-doc is missing DEPLOYMENT.md")
        if feature == "docker" and not {"Dockerfile", ".dockerignore"} <= files.keys():
            raise AuditError("required feature docker is missing Dockerfile or .dockerignore")
        if feature == "golden":
            for marker in ("golden_input.", "golden_expected."):
                if not any(name.startswith(f"fixtures/{marker}") for name in files):
                    raise AuditError(f"required feature golden is missing fixtures/{marker}*")
        if feature == "model-card" and "MODEL_CARD.md" not in files:
            raise AuditError("required feature model-card is missing MODEL_CARD.md")
        if feature == "safetensors" and not any(
            name.startswith("weights/") and name.endswith(".safetensors") for name in files
        ):
            raise AuditError("required feature safetensors is missing weights/*.safetensors")
        if feature == "sdk" and not any(name.startswith("sdk/") for name in files):
            raise AuditError("required feature sdk is missing sdk/*")
        if feature == "wheel" and not any(
            name.startswith("dist/") and name.endswith(".whl") for name in files
        ):
            raise AuditError("required feature wheel is missing dist/*.whl")
    pickle_files = [name for name in files if Path(name).suffix.lower() in PICKLE_SUFFIXES]
    if pickle_files:
        raise AuditError(f"pickle checkpoint/artifact is forbidden: {pickle_files}")

    manifest = _strict_json(files["release_manifest.json"])
    if not isinstance(manifest, dict) or not isinstance(manifest.get("release_id"), str):
        raise AuditError("release_manifest.json must contain string release_id")
    release_id = manifest["release_id"]
    if args.expected_release_id is not None and release_id != args.expected_release_id:
        raise AuditError(f"release id mismatch: manifest={release_id!r}, expected={args.expected_release_id!r}")
    if args.require_directory_name_match and root.name != release_id:
        raise AuditError(f"release directory name {root.name!r} differs from manifest {release_id!r}")
    for relative in ("normalization.json", "preprocessing.json"):
        if relative in files:
            _strict_json(files[relative])

    checksums = _parse_checksums(files["checksums.sha256"])
    expected_checksums = set(files) - {"checksums.sha256"}
    if set(checksums) != expected_checksums:
        raise AuditError(
            f"checksum closure mismatch: missing={sorted(expected_checksums - checksums.keys())}, "
            f"extra={sorted(checksums.keys() - expected_checksums)}"
        )
    for relative, expected in checksums.items():
        actual = _sha256(files[relative])
        if actual != expected:
            raise AuditError(f"checksum mismatch: {relative}: expected={expected}, actual={actual}")

    safetensors = [path for name, path in files.items() if name.endswith(".safetensors")]
    for path in safetensors:
        _validate_safetensors(path)
    wheels = [path for name, path in files.items() if name.endswith(".whl")]
    for wheel in wheels:
        if not zipfile.is_zipfile(wheel):
            raise AuditError(f"invalid wheel ZIP: {wheel}")
        with zipfile.ZipFile(wheel) as handle:
            bad_member = handle.testzip()
        if bad_member is not None:
            raise AuditError(f"corrupt wheel member: {wheel}: {bad_member}")

    patterns = tuple(re.compile(pattern, flags=re.IGNORECASE) for pattern in (*DEFAULT_FORBIDDEN, *args.forbid_regex))
    _scan_text(files, patterns)

    archive_digest: str | None = None
    if args.archive is not None:
        archive = args.archive.expanduser().resolve()
        if not archive.is_file():
            raise AuditError(f"archive does not exist: {archive}")
        _validate_archive(archive, root, files)
        archive_digest = _sha256(archive)
        if args.archive_sha256 is not None:
            sidecar = args.archive_sha256.expanduser().resolve()
            match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)\n?", sidecar.read_text(encoding="utf-8"))
            if match is None or match.group(1) != archive_digest or match.group(2) != archive.name:
                raise AuditError("archive SHA256 sidecar is invalid or does not match")
    elif args.archive_sha256 is not None:
        raise AuditError("--archive-sha256 requires --archive")

    return {
        "status": "PASSED",
        "release_id": release_id,
        "file_count": len(files),
        "weight_file_count": len(safetensors),
        "wheel_count": len(wheels),
        "archive_sha256": archive_digest,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_dir", type=Path)
    parser.add_argument("--expected-release-id")
    parser.add_argument("--require-directory-name-match", action="store_true")
    parser.add_argument("--require-feature", action="append", choices=FEATURES, default=[])
    parser.add_argument("--require-file", action="append", default=[])
    parser.add_argument("--require-glob", action="append", default=[])
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--archive-sha256", type=Path)
    parser.add_argument("--forbid-regex", action="append", default=[])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        result = audit(parse_args(argv))
    except (AuditError, OSError, re.error, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(f"release audit: FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
