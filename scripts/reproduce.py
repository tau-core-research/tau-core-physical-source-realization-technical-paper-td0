from pathlib import Path
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "physical_source_submission_source"


def run(*args, cwd=None):
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    subprocess.run(args, cwd=cwd or ROOT, check=True, env=env)


def main():
    if shutil.which("tectonic") is None:
        raise SystemExit("tectonic is required")
    run(sys.executable, "scripts/freeze_p3_clp3_seed.py")
    run(sys.executable, "scripts/audit_p3_clp3_instantiation.py")
    run(sys.executable, "scripts/freeze_p1_ambient_certificate.py")
    run(sys.executable, "scripts/audit_p1_ambient_certificate.py")
    run(sys.executable, "scripts/freeze_p1_source_envelope_separator.py")
    run(sys.executable, "scripts/audit_p1_source_envelope_separator.py")
    run(sys.executable, "scripts/freeze_p1_envelope_connector_selector.py")
    run(sys.executable, "scripts/audit_p1_envelope_connector_selector.py")
    run(sys.executable, "scripts/freeze_p1_record_clifford_embedding.py")
    run(sys.executable, "scripts/audit_p1_record_clifford_embedding.py")
    run(sys.executable, "scripts/freeze_p1_record_clifford_landing.py")
    run(sys.executable, "scripts/audit_p1_record_clifford_landing.py")
    run(sys.executable, "scripts/freeze_p1_record_clifford_source_completion.py")
    run(sys.executable, "scripts/audit_p1_record_clifford_source_completion.py")
    run(sys.executable, "scripts/freeze_p1_joint_graded_representation.py")
    run(sys.executable, "scripts/audit_p1_joint_graded_representation.py")
    run(sys.executable, "scripts/freeze_p1_joint_carrier_minimality.py")
    run(sys.executable, "scripts/audit_p1_joint_carrier_minimality.py")
    run(sys.executable, "scripts/freeze_single_source_law.py")
    run(sys.executable, "scripts/audit_single_source_law.py")
    run(sys.executable, "scripts/check_derivations.py")
    run(sys.executable, "scripts/build_figures.py")
    run("tectonic", "main.tex", cwd=SOURCE)
    run(sys.executable, "scripts/build_arxiv_source.py")
    run(sys.executable, "-m", "pytest", "-q")
    print("PHYSICAL_SOURCE_TECHNICAL_COMPANION_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
