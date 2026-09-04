#!/usr/bin/env python3
"""Convert TruffleHog JSONL into a secret-safe CI evidence report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
FINDINGS_EXIT_CODE = 183


def _safe_location(row: dict[str, Any]) -> dict[str, Any]:
    data = ((row.get("SourceMetadata") or {}).get("Data") or {})
    source = data.get("Git") or data.get("Filesystem") or {}
    return {
        "file": str(source.get("file") or "unknown"),
        "line": int(source.get("line") or 0),
        "commit": str(source.get("commit") or ""),
    }


def build_report(
    input_path: Path,
    *,
    scope: str,
    scanner_exit_code: int,
    scanner_version: str,
    source_commit: str | None = None,
    source_base_commit: str | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, Any]:
    findings = []
    for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not row.get("DetectorName"):
            raise ValueError(f"invalid TruffleHog result at line {line_number}")
        findings.append({
            "detector_name": str(row["DetectorName"]),
            "detector_type": int(row.get("DetectorType") or 0),
            "verified": bool(row.get("Verified")),
            **_safe_location(row),
        })

    if scanner_exit_code == 0 and findings:
        raise ValueError("TruffleHog returned findings with a success exit code")
    if scanner_exit_code == FINDINGS_EXIT_CODE and not findings:
        raise ValueError("TruffleHog returned the findings exit code without findings")

    if scanner_exit_code == 0:
        status = "clean"
    elif scanner_exit_code == FINDINGS_EXIT_CODE:
        status = "findings"
    else:
        status = "error"
    return {
        "schema_version": SCHEMA_VERSION,
        "scanner": "trufflehog",
        "scanner_version": scanner_version,
        "scope": scope,
        "status": status,
        "scanner_exit_code": scanner_exit_code,
        "source_commit": source_commit,
        "source_base_commit": source_base_commit,
        "artifact_sha256": artifact_sha256.lower() if artifact_sha256 else None,
        "finding_count": len(findings),
        "verified_count": sum(1 for finding in findings if finding["verified"]),
        "findings": findings,
    }


def _error_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scanner": "trufflehog",
        "scanner_version": args.scanner_version,
        "scope": args.scope,
        "status": "error",
        "scanner_exit_code": args.scanner_exit_code,
        "source_commit": args.source_commit,
        "source_base_commit": args.source_base_commit,
        "artifact_sha256": args.artifact_sha256.lower() if args.artifact_sha256 else None,
        "finding_count": 0,
        "verified_count": 0,
        "findings": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scope", required=True, choices=("git-history", "git-changes", "release-artifact", "repository-snapshot"))
    parser.add_argument("--scanner-exit-code", type=int, required=True)
    parser.add_argument("--scanner-version", required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--source-base-commit")
    parser.add_argument("--artifact-sha256")
    args = parser.parse_args(argv)
    try:
        report = build_report(
            args.input,
            scope=args.scope,
            scanner_exit_code=args.scanner_exit_code,
            scanner_version=args.scanner_version,
            source_commit=args.source_commit,
            source_base_commit=args.source_base_commit,
            artifact_sha256=args.artifact_sha256,
        )
        rc = 0
    except (OSError, ValueError, TypeError):
        report = _error_report(args)
        rc = 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "scope": report["scope"],
        "status": report["status"],
        "finding_count": report["finding_count"],
    }, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
