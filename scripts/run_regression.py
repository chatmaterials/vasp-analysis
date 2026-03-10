#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    single = run_json("scripts/analyze_vasp_result.py", "fixtures/completed", "--json")
    ensure(single["completed"] is True, "completed fixture should be complete")
    ensure(abs(single["final_energy_eV"] + 10.54321) < 1e-6, "single-run energy should parse")

    compare = run_json("scripts/compare_vasp_results.py", "fixtures/compare/alpha", "fixtures/compare/beta", "--json")
    ensure(compare["results"][0]["path"].endswith("alpha"), "alpha should be lower in energy than beta")
    ensure(compare["results"][1]["relative_energy_meV"] > 0, "beta should have positive relative energy")
    structure = run_json("scripts/structure_change_vasp.py", "fixtures/compare/alpha/POSCAR", "fixtures/compare/beta/POSCAR", "--json")
    ensure(structure["natoms"] == 2, "structure comparison should keep the atom count")
    ensure(any(abs(delta) > 0 for delta in structure["lattice_length_delta"]), "structure comparison should detect a lattice difference")
    dos = run_json("scripts/analyze_vasp_dos.py", "fixtures/completed", "--json")
    ensure(abs(dos["dos_at_fermi"] - 0.2) < 1e-6, "DOS analysis should parse DOS at the Fermi level")
    band = run_json("scripts/analyze_vasp_band.py", "fixtures/completed", "--json")
    ensure(abs(band["band_gap_eV"] - 1.1) < 1e-6, "band analysis should parse the band gap")
    ensure(band["is_direct_gap"] is True, "fixture should produce a direct band gap")
    magnetism = run_json("scripts/analyze_vasp_magnetism.py", "fixtures/completed", "--json")
    ensure(abs(magnetism["total_moment_muB"] - 1.2) < 1e-6, "magnetism analysis should parse the total moment")
    ensure(abs(magnetism["max_local_moment_muB"] - 1.3) < 1e-6, "magnetism analysis should parse the largest local moment")
    voltage = run_json("scripts/analyze_vasp_voltage.py", "fixtures/battery/host", "fixtures/battery/lithiated", "--reference-energy", "-1.50", "--json")
    ensure(abs(voltage["average_voltage_V"] - 1.0) < 1e-6, "voltage analysis should parse the average insertion voltage")
    neb = run_json("scripts/analyze_vasp_neb.py", "fixtures/neb", "--json")
    ensure(abs(neb["forward_barrier_eV"] - 0.7) < 1e-6, "NEB analysis should parse the forward barrier")
    ensure(abs(neb["reverse_barrier_eV"] - 0.8) < 1e-6, "NEB analysis should parse the reverse barrier")
    ensure(neb["highest_image"] == "02", "NEB analysis should identify the highest-energy image")
    temp_dir = Path(tempfile.mkdtemp(prefix="vasp-analysis-report-"))
    try:
        report_path = Path(run("scripts/export_analysis_report.py", "fixtures/completed", "--output", str(temp_dir / "ANALYSIS_REPORT.md")).stdout.strip())
        report_text = report_path.read_text()
        ensure("# Analysis Report" in report_text, "analysis report should have an analysis-report heading")
        ensure("Final energy" in report_text, "analysis report should include the final energy")
        ensure("## DOS" in report_text and "## Band" in report_text and "## Magnetism" in report_text, "analysis report should include DOS, band, and magnetism sections when files are present")
    finally:
        shutil.rmtree(temp_dir)

    print("vasp-analysis regression passed")


if __name__ == "__main__":
    main()
