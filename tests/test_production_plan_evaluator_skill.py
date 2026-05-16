from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "production-plan-evaluator"
SKILL = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_has_discoverable_frontmatter_without_process_shortcut():
    text = read(SKILL)
    assert text.startswith("---\n")
    fm = text.split("---", 2)[1]
    assert "name: production-plan-evaluator" in fm
    desc = re.search(r"description:\s*(.+)", fm).group(1)
    assert desc.startswith("Use when")
    assert len(desc) < 500
    # Description should trigger loading, not replace reading the skill body.
    forbidden_process_words = ["three-layer", "Gate Review", "Final Gate", "Evidence Ledger"]
    assert not any(word in desc for word in forbidden_process_words)


def test_skill_body_encodes_three_layer_sop_and_final_gate_contract():
    text = read(SKILL)
    required = [
        "Layer 1", "Gate Review", "Layer 2", "Elevation", "Layer 3", "Final Gate",
        "Go", "Conditional Go", "No-Go", "Defer", "now vs defer",
        "must not design a new solution", "must compare now vs defer",
        "No evidence, no final verdict",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_skill_requires_deficiency_challenge_evidence_and_exception_governance():
    text = read(SKILL)
    required = [
        "at least three", "deficiencies", "Evidence Ledger", "L1", "L2", "L3", "L4",
        "exception approval", "compensating controls", "owner", "review date",
        "official", "industry", "service-native",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_reference_files_exist_and_cover_contracts():
    expected = ["evidence-ledger.md", "exception-template.md", "calibration-cases.md"]
    for name in expected:
        assert (REFS / name).exists(), name

    evidence = read(REFS / "evidence-ledger.md")
    for item in ["L1", "L2", "L3", "L4", "Conflict", "Minimum evidence"]:
        assert item in evidence

    exception = read(REFS / "exception-template.md")
    for item in ["Reason for deviation", "Constraint source", "Compensating controls", "Rollback proof", "owner", "review date"]:
        assert item in exception

    calibration = read(REFS / "calibration-cases.md")
    for item in ["Service lifecycle", "Database migration", "Kubernetes", "Certificate", "Expected verdict"]:
        assert item in calibration


def test_no_extra_auxiliary_docs_created():
    forbidden = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}
    present = {p.name for p in SKILL_DIR.glob("*.md")}
    assert not (present & forbidden)
