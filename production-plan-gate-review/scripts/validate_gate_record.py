#!/usr/bin/env python3
"""Validate a Gate Review v2 structured record."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PHASES = {"precheck", "prepare", "execute", "verify", "rollback", "observe", "handoff"}
MARKERS = {"OK", "GAP", "RISK", "ELEVATE", "NEED-EVIDENCE"}
TIERS = {"L1", "L2", "L3", "L4"}

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "normalized_proposal",
    "path_steps",
    "evidence_ledger",
    "alternative_checks",
    "deficiency_chains",
    "gate_checks",
    "elevation_entry",
}

NORMALIZED_REQUIRED = {
    "goal",
    "current_plan",
    "production_impact",
    "constraints",
    "success_criteria",
    "rollback_expectation",
    "owner_handoff",
}

PATH_STEP_REQUIRED = {
    "step_id",
    "phase",
    "action",
    "preconditions",
    "execution_detail",
    "expected_result",
    "verification",
    "rollback",
    "owner",
    "evidence_refs",
    "marker",
    "finding_refs",
}

EVIDENCE_REQUIRED = {
    "evidence_id",
    "claim",
    "tier",
    "source",
    "environment_date",
    "confidence",
    "impact",
}

ALTERNATIVE_REQUIRED = {
    "step_id",
    "current_method",
    "native_or_standard_alternatives",
    "better_option",
    "evidence_basis",
    "why_current_is_weaker",
    "recommendation",
}

DEFICIENCY_REQUIRED = {
    "finding_id",
    "step_id",
    "defect",
    "evidence_refs",
    "production_consequence",
    "required_fix_or_proof",
    "elevation_required",
}

GATE_CHECK_REQUIRED = {
    "gate",
    "status",
    "evidence_refs",
    "blocking_issue",
    "next_action",
}

ELEVATION_ENTRY_REQUIRED = {
    "elevation_required",
    "trigger_sources",
    "blocking_path_steps",
    "what_elevation_must_solve",
}


def present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def require_fields(errors: list[str], location: str, item: Any, required: set[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"{location} must be an object")
        return
    for field in sorted(required):
        if field not in item:
            errors.append(f"{location}.{field} is required")


def validate_refs(
    errors: list[str],
    location: str,
    refs: Any,
    valid_ids: set[str],
    ref_kind: str,
) -> None:
    if not isinstance(refs, list):
        errors.append(f"{location} must be a list")
        return
    for ref in refs:
        if ref not in valid_ids:
            errors.append(f"{location} contains unknown {ref_kind} '{ref}'")


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    require_fields(errors, "record", record, TOP_LEVEL_REQUIRED)
    if errors:
        return errors

    if record.get("schema_version") != "gate-review.v2":
        errors.append("record.schema_version must be 'gate-review.v2'")

    normalized = record.get("normalized_proposal")
    require_fields(errors, "normalized_proposal", normalized, NORMALIZED_REQUIRED)
    if isinstance(normalized, dict):
        for field in sorted(NORMALIZED_REQUIRED):
            if not present(normalized.get(field)):
                errors.append(f"normalized_proposal.{field} must not be empty")

    path_steps = record.get("path_steps")
    evidence_ledger = record.get("evidence_ledger")
    alternative_checks = record.get("alternative_checks")
    deficiency_chains = record.get("deficiency_chains")
    gate_checks = record.get("gate_checks")
    elevation_entry = record.get("elevation_entry")

    for name, value in [
        ("path_steps", path_steps),
        ("evidence_ledger", evidence_ledger),
        ("alternative_checks", alternative_checks),
        ("deficiency_chains", deficiency_chains),
        ("gate_checks", gate_checks),
    ]:
        if not isinstance(value, list):
            errors.append(f"{name} must be a list")

    if not isinstance(path_steps, list) or not path_steps:
        errors.append("path_steps must contain at least one step")
        path_steps = []
    if not isinstance(evidence_ledger, list):
        evidence_ledger = []
    if not isinstance(alternative_checks, list):
        alternative_checks = []
    if not isinstance(deficiency_chains, list):
        deficiency_chains = []
    if not isinstance(gate_checks, list):
        gate_checks = []

    evidence_ids: set[str] = set()
    for index, evidence in enumerate(evidence_ledger):
        location = f"evidence_ledger[{index}]"
        require_fields(errors, location, evidence, EVIDENCE_REQUIRED)
        if not isinstance(evidence, dict):
            continue
        evidence_id = evidence.get("evidence_id")
        if not present(evidence_id):
            errors.append(f"{location}.evidence_id must not be empty")
        else:
            evidence_ids.add(str(evidence_id))
        if evidence.get("tier") not in TIERS:
            errors.append(f"{location}.tier must be one of {sorted(TIERS)}")
        for field in EVIDENCE_REQUIRED - {"evidence_id", "tier"}:
            if not present(evidence.get(field)):
                errors.append(f"{location}.{field} must not be empty")

    step_ids: set[str] = set()
    step_markers: dict[str, str] = {}
    step_finding_refs: dict[str, list[str]] = {}
    for index, step in enumerate(path_steps):
        location = f"path_steps[{index}]"
        require_fields(errors, location, step, PATH_STEP_REQUIRED)
        if not isinstance(step, dict):
            continue
        step_id = step.get("step_id")
        if not present(step_id):
            errors.append(f"{location}.step_id must not be empty")
            continue
        step_id = str(step_id)
        if step_id in step_ids:
            errors.append(f"{location}.step_id '{step_id}' is duplicated")
        step_ids.add(step_id)

        phase = step.get("phase")
        marker = step.get("marker")
        if phase not in PHASES:
            errors.append(f"{location}.phase must be one of {sorted(PHASES)}")
        if marker not in MARKERS:
            errors.append(f"{location}.marker must be one of {sorted(MARKERS)}")
        else:
            step_markers[step_id] = marker

        for field in PATH_STEP_REQUIRED - {"step_id", "phase", "marker", "evidence_refs", "finding_refs"}:
            if not present(step.get(field)):
                errors.append(f"{location}.{field} must not be empty")

        validate_refs(errors, f"{location}.evidence_refs", step.get("evidence_refs"), evidence_ids, "evidence_id")
        finding_refs = step.get("finding_refs")
        if not isinstance(finding_refs, list):
            errors.append(f"{location}.finding_refs must be a list")
            finding_refs = []
        step_finding_refs[step_id] = [str(ref) for ref in finding_refs]

        if marker == "OK":
            if not present(step.get("evidence_refs")):
                errors.append(f"{location} marked OK must include evidence_refs")
            if not present(step.get("verification")):
                errors.append(f"{location} marked OK must include verification")
        if marker in {"RISK", "ELEVATE"} and not present(finding_refs):
            errors.append(f"{location} marked {marker} must include finding_refs")
        if marker == "NEED-EVIDENCE" and not present(step.get("missing_evidence")):
            errors.append(f"{location} marked NEED-EVIDENCE must include missing_evidence")

    alternative_step_ids: set[str] = set()
    for index, alternative in enumerate(alternative_checks):
        location = f"alternative_checks[{index}]"
        require_fields(errors, location, alternative, ALTERNATIVE_REQUIRED)
        if not isinstance(alternative, dict):
            continue
        step_id = alternative.get("step_id")
        if step_id not in step_ids:
            errors.append(f"{location}.step_id references unknown path step '{step_id}'")
        else:
            alternative_step_ids.add(str(step_id))
        for field in ALTERNATIVE_REQUIRED - {"step_id"}:
            if not present(alternative.get(field)):
                errors.append(f"{location}.{field} must not be empty")

    finding_ids: set[str] = set()
    for index, chain in enumerate(deficiency_chains):
        location = f"deficiency_chains[{index}]"
        require_fields(errors, location, chain, DEFICIENCY_REQUIRED)
        if not isinstance(chain, dict):
            continue
        finding_id = chain.get("finding_id")
        if not present(finding_id):
            errors.append(f"{location}.finding_id must not be empty")
        else:
            finding_ids.add(str(finding_id))
        if chain.get("step_id") not in step_ids:
            errors.append(f"{location}.step_id references unknown path step '{chain.get('step_id')}'")
        validate_refs(errors, f"{location}.evidence_refs", chain.get("evidence_refs"), evidence_ids, "evidence_id")
        for field in DEFICIENCY_REQUIRED - {"finding_id", "step_id", "evidence_refs", "elevation_required"}:
            if not present(chain.get(field)):
                errors.append(f"{location}.{field} must not be empty")
        if not isinstance(chain.get("elevation_required"), bool):
            errors.append(f"{location}.elevation_required must be boolean")

    for step_id, marker in step_markers.items():
        if marker in {"RISK", "ELEVATE"} and step_id not in alternative_step_ids:
            errors.append(f"path step '{step_id}' marked {marker} must have an alternative_check")
        for finding_ref in step_finding_refs.get(step_id, []):
            if finding_ref not in finding_ids:
                errors.append(f"path step '{step_id}' references unknown finding_id '{finding_ref}'")

    if len(path_steps) >= 3 and len(deficiency_chains) < 3:
        errors.append("deficiency_chains must contain at least three items when path_steps has three or more steps")

    for index, gate_check in enumerate(gate_checks):
        location = f"gate_checks[{index}]"
        require_fields(errors, location, gate_check, GATE_CHECK_REQUIRED)
        if not isinstance(gate_check, dict):
            continue
        for field in GATE_CHECK_REQUIRED - {"evidence_refs"}:
            if not present(gate_check.get(field)):
                errors.append(f"{location}.{field} must not be empty")
        validate_refs(errors, f"{location}.evidence_refs", gate_check.get("evidence_refs"), evidence_ids, "evidence_id")

    require_fields(errors, "elevation_entry", elevation_entry, ELEVATION_ENTRY_REQUIRED)
    if isinstance(elevation_entry, dict):
        elevation_required = elevation_entry.get("elevation_required")
        if not isinstance(elevation_required, bool):
            errors.append("elevation_entry.elevation_required must be boolean")
        blocking_steps = elevation_entry.get("blocking_path_steps")
        if isinstance(blocking_steps, list):
            for step_id in blocking_steps:
                if step_id not in step_ids:
                    errors.append(f"elevation_entry.blocking_path_steps references unknown path step '{step_id}'")
        elif blocking_steps is not None:
            errors.append("elevation_entry.blocking_path_steps must be a list")
        for field in ELEVATION_ENTRY_REQUIRED - {"elevation_required", "blocking_path_steps"}:
            if not isinstance(elevation_entry.get(field), list):
                errors.append(f"elevation_entry.{field} must be a list")
        if elevation_required is True:
            for field in ELEVATION_ENTRY_REQUIRED - {"elevation_required"}:
                if not present(elevation_entry.get(field)):
                    errors.append(f"elevation_entry.{field} must not be empty when elevation_required is true")
        if any(marker == "ELEVATE" for marker in step_markers.values()) and elevation_entry.get("elevation_required") is not True:
            errors.append("elevation_entry.elevation_required must be true when any path step is ELEVATE")

    return errors


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_gate_record.py <gate-record.json>", file=sys.stderr)
        return 2

    try:
        record = load_json(Path(argv[1]))
    except Exception as exc:  # noqa: BLE001 - CLI should report parse/load failures plainly.
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate_record(record)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Gate record is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
