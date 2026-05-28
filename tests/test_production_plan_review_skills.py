import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

GATE = ROOT / "production-plan-gate-review"
ELEVATION = ROOT / "production-plan-elevation"
FINAL_GATE = ROOT / "production-plan-final-gate"
GATE_VALIDATOR = GATE / "scripts" / "validate_gate_record.py"
SKILL_DIRS = [GATE, ELEVATION, FINAL_GATE]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    assert text.startswith("---\n")
    return text.split("---", 2)[1]


def load_gate_validator():
    spec = importlib.util.spec_from_file_location("validate_gate_record", GATE_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_gate_record():
    return {
        "schema_version": "gate-review.v2",
        "normalized_proposal": {
            "goal": "restart production nginx safely",
            "current_plan": "use a wrapper script to stop and start nginx",
            "production_impact": "public traffic path",
            "constraints": ["no full outage"],
            "success_criteria": ["traffic remains healthy"],
            "rollback_expectation": "restore prior service-manager path",
            "owner_handoff": "SRE on-call owns execution and handoff",
        },
        "path_steps": [
            {
                "step_id": "S1",
                "phase": "precheck",
                "action": "check current service state",
                "preconditions": ["host access"],
                "execution_detail": "systemctl status nginx",
                "expected_result": "service state is known",
                "verification": "status output captured",
                "rollback": "no state change",
                "owner": "SRE",
                "evidence_refs": ["EV1"],
                "marker": "OK",
                "finding_refs": [],
            },
            {
                "step_id": "S2",
                "phase": "execute",
                "action": "restart through wrapper",
                "preconditions": ["wrapper exists"],
                "execution_detail": "./nginx-wrapper restart",
                "expected_result": "nginx restarts",
                "verification": "curl health endpoint",
                "rollback": "systemctl restart nginx",
                "owner": "SRE",
                "evidence_refs": ["EV2"],
                "marker": "RISK",
                "finding_refs": ["F1"],
            },
            {
                "step_id": "S3",
                "phase": "rollback",
                "action": "rollback failed wrapper restart",
                "preconditions": ["prior service state known"],
                "execution_detail": "restore systemd-managed service path",
                "expected_result": "nginx is managed by systemd again",
                "verification": "systemctl status nginx",
                "rollback": "not proven",
                "owner": "SRE",
                "evidence_refs": [],
                "marker": "NEED-EVIDENCE",
                "finding_refs": ["F2"],
                "missing_evidence": ["rollback rehearsal output"],
            },
            {
                "step_id": "S4",
                "phase": "handoff",
                "action": "handoff wrapper ownership",
                "preconditions": ["runbook exists"],
                "execution_detail": "publish wrapper runbook",
                "expected_result": "operators know ownership",
                "verification": "runbook review record",
                "rollback": "return to systemd runbook",
                "owner": "SRE manager",
                "evidence_refs": ["EV3"],
                "marker": "ELEVATE",
                "finding_refs": ["F3"],
            },
        ],
        "evidence_ledger": [
            {
                "evidence_id": "EV1",
                "claim": "nginx is service-manager controlled",
                "tier": "L3",
                "source": "systemctl output",
                "environment_date": "2026-05-23",
                "confidence": "high",
                "impact": "precheck confidence",
            },
            {
                "evidence_id": "EV2",
                "claim": "wrapper bypasses native reload semantics",
                "tier": "L1",
                "source": "systemd and nginx docs",
                "environment_date": "2026-05-23",
                "confidence": "medium",
                "impact": "execution risk",
            },
            {
                "evidence_id": "EV3",
                "claim": "handoff owner is unclear",
                "tier": "L4",
                "source": "author statement",
                "environment_date": "2026-05-23",
                "confidence": "low",
                "impact": "operational risk",
            },
        ],
        "alternative_checks": [
            {
                "step_id": "S2",
                "current_method": "wrapper restart",
                "native_or_standard_alternatives": ["systemctl reload nginx", "nginx -t before reload"],
                "better_option": "systemd-managed reload with config test",
                "evidence_basis": ["EV2"],
                "why_current_is_weaker": "wrapper obscures service ownership",
                "recommendation": "elevate to service-native path",
            },
            {
                "step_id": "S4",
                "current_method": "manual wrapper handoff",
                "native_or_standard_alternatives": ["standard service runbook"],
                "better_option": "document systemd ownership and runbook",
                "evidence_basis": ["EV3"],
                "why_current_is_weaker": "manual ownership is not auditable",
                "recommendation": "require exception or native path",
            },
        ],
        "deficiency_chains": [
            {
                "finding_id": "F1",
                "step_id": "S2",
                "defect": "wrapper bypasses native service controls",
                "evidence_refs": ["EV2"],
                "production_consequence": "restart semantics may diverge from operator expectations",
                "required_fix_or_proof": "use native reload or provide exception proof",
                "elevation_required": True,
            },
            {
                "finding_id": "F2",
                "step_id": "S3",
                "defect": "rollback rehearsal is missing",
                "evidence_refs": [],
                "production_consequence": "failed restart may extend outage",
                "required_fix_or_proof": "capture rollback rehearsal output",
                "elevation_required": False,
            },
            {
                "finding_id": "F3",
                "step_id": "S4",
                "defect": "handoff path is nonstandard",
                "evidence_refs": ["EV3"],
                "production_consequence": "future operators may not know ownership",
                "required_fix_or_proof": "standard runbook or exception approval",
                "elevation_required": True,
            },
        ],
        "gate_checks": [
            {
                "gate": "rollback",
                "status": "fail",
                "evidence_refs": [],
                "blocking_issue": "rollback rehearsal missing",
                "next_action": "collect rollback proof",
            }
        ],
        "elevation_entry": {
            "elevation_required": True,
            "trigger_sources": ["S2", "S4"],
            "blocking_path_steps": ["S2", "S3", "S4"],
            "what_elevation_must_solve": ["native service control", "rollback proof", "handoff ownership"],
        },
    }


def test_three_independent_skills_have_discoverable_frontmatter():
    expected = {
        GATE: "production-plan-gate-review",
        ELEVATION: "production-plan-elevation",
        FINAL_GATE: "production-plan-final-gate",
    }
    for skill_dir, name in expected.items():
        skill = skill_dir / "SKILL.md"
        assert skill.exists(), skill
        fm = frontmatter(read(skill))
        assert f"name: {name}" in fm
        desc = re.search(r"description:\s*(.+)", fm).group(1)
        assert desc.startswith("Use when")
        assert len(desc) < 500


def test_old_combined_evaluator_skill_is_removed():
    old_skill = ROOT / "production-plan-evaluator" / "SKILL.md"
    assert not old_skill.exists()
    readme = read(ROOT / "README.md")
    assert "production-plan-evaluator" not in readme


def test_gate_review_contract_focuses_on_path_and_elevation_entry_not_final_gate():
    text = read(GATE / "SKILL.md")
    required = [
        "Implementation Path Canvas",
        "Step Executability Matrix",
        "Alternative / Baseline Checks",
        "Structured Gate Record",
        "schema_version",
        "gate-review.v2",
        "PathStep contract",
        "AlternativeCheck contract",
        "DeficiencyChain contract",
        "orchestrator-state-machine.md",
        "calibration-cases.md",
        "Path Findings Map",
        "Evidence Ledger",
        "at least three deficiency chains",
        "Elevation Required?",
        "Elevation Entry",
        "[OK]",
        "[GAP]",
        "[RISK]",
        "[ELEVATE]",
        "[NEED-EVIDENCE]",
        "No final admission",
        "No skipped alternatives",
        "No evidence-backed check, no OK",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    forbidden = ["Allowed verdicts", "Final Gate Report"]
    assert not any(item in text for item in forbidden)


def test_elevation_contract_designs_candidates_but_does_not_approve():
    text = read(ELEVATION / "SKILL.md")
    required = [
        "Gate Review v2 Structured Gate Record",
        "Consume Gate v2, do not redo it",
        "`ELEVATE`, `RISK`, and `NEED-EVIDENCE` blockers",
        "Gate Review output",
        "1–3 elevated candidate paths",
        "Current Plan Retention Conditions",
        "Elevated Candidate Options",
        "Recommended Path for Final Gate",
        "Cutover path",
        "Rollback path",
        "Verification and observability",
        "Owner and handoff",
        "Exception Approval",
        "Never output final",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    assert "Allowed verdicts" not in text


def test_final_gate_contract_approves_without_designing():
    text = read(FINAL_GATE / "SKILL.md")
    required = [
        "Gate Review v2 Structured Gate Record",
        "Consume Gate v2, do not redo it",
        "Gate v2 Structured Record Status",
        "No design in Final Gate",
        "Allowed verdicts",
        "Go",
        "Conditional Go",
        "No-Go / Return to Design",
        "Defer / Need Evidence",
        "Hard Gate Checklist",
        "Now vs Defer Comparison",
        "Conditions and Proof Forms",
        "proof form, owner, and deadline",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    forbidden = ["1–3 elevated candidate paths", "Elevated Candidate Options"]
    assert not any(item in text for item in forbidden)


def test_reference_files_exist_for_each_independent_skill():
    expected = {
        GATE: [
            "calibration-cases.md",
            "evidence-ledger.md",
            "orchestrator-state-machine.md",
            "path-canvas-template.md",
        ],
        ELEVATION: ["elevation-options-template.md", "exception-template.md"],
        FINAL_GATE: ["evidence-ledger.md", "final-gate-checklist.md"],
    }
    for skill_dir, names in expected.items():
        for name in names:
            assert (skill_dir / "references" / name).exists(), f"{skill_dir.name}/{name}"
    assert GATE_VALIDATOR.exists()


def test_readme_documents_ordered_three_skill_workflow():
    text = read(ROOT / "README.md")
    required = [
        "production-plan-gate-review",
        "production-plan-elevation",
        "production-plan-final-gate",
        "Gate v2 structured record",
        "validate_gate_record.py",
        "Do not ask one skill to complete all three stages",
        "old combined flow encouraged shallow one-pass reviews",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_gate_record_validator_accepts_complete_record():
    validator = load_gate_validator()
    assert validator.validate_record(valid_gate_record()) == []


def test_gate_record_validator_rejects_missing_step_id():
    validator = load_gate_validator()
    record = valid_gate_record()
    del record["path_steps"][0]["step_id"]
    errors = validator.validate_record(record)
    assert any("path_steps[0].step_id is required" in error for error in errors)


def test_gate_record_validator_rejects_empty_rollback_detail():
    validator = load_gate_validator()
    record = valid_gate_record()
    record["path_steps"][0]["rollback"] = ""
    errors = validator.validate_record(record)
    assert any("path_steps[0].rollback must not be empty" in error for error in errors)


def test_gate_record_validator_rejects_ok_without_evidence():
    validator = load_gate_validator()
    record = valid_gate_record()
    record["path_steps"][0]["evidence_refs"] = []
    errors = validator.validate_record(record)
    assert any("marked OK must include evidence_refs" in error for error in errors)


def test_gate_record_validator_rejects_risk_without_alternative_check():
    validator = load_gate_validator()
    record = valid_gate_record()
    record["alternative_checks"] = [
        alternative for alternative in record["alternative_checks"] if alternative["step_id"] != "S2"
    ]
    errors = validator.validate_record(record)
    assert any("marked RISK must have an alternative_check" in error for error in errors)


def test_gate_record_validator_rejects_need_evidence_without_missing_evidence():
    validator = load_gate_validator()
    record = valid_gate_record()
    del record["path_steps"][2]["missing_evidence"]
    errors = validator.validate_record(record)
    assert any("marked NEED-EVIDENCE must include missing_evidence" in error for error in errors)


def test_gate_record_validator_cli_accepts_json_file(tmp_path):
    record_path = tmp_path / "gate-record.json"
    record_path.write_text(json.dumps(valid_gate_record()), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(GATE_VALIDATOR), str(record_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Gate record is valid." in result.stdout
