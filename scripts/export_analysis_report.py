#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_vasp_result import analyze_path
from analyze_vasp_band import analyze_path as analyze_band
from analyze_vasp_dos import analyze_path as analyze_dos
from analyze_vasp_magnetism import analyze_path as analyze_magnetism


def render_markdown(record: dict[str, object]) -> str:
    lines = [
        "# Analysis Report",
        "",
        f"Source: `{record['path']}`",
        "",
        f"- Completed: `{str(record['completed']).lower()}`",
        f"- Ionic converged: `{str(record['ionic_converged']).lower()}`",
    ]
    if record.get("final_energy_eV") is not None:
        lines.append(f"- Final energy (eV): `{record['final_energy_eV']:.6f}`")
    if record.get("energy_per_atom_eV") is not None:
        lines.append(f"- Energy per atom (eV): `{record['energy_per_atom_eV']:.6f}`")
    if record.get("max_force_eV_A") is not None:
        lines.append(f"- Max force (eV/Ang): `{record['max_force_eV_A']:.4f}`")
    lines.extend(["", "## Observations"])
    lines.extend(f"- {item}" for item in record["observations"])
    source = Path(str(record["path"]))
    if (source / "DOSCAR").exists():
        dos = analyze_dos(source)
        lines.extend(
            [
                "",
                "## DOS",
                f"- Fermi level (eV): `{dos['efermi_eV']:.4f}`",
                f"- DOS at Fermi: `{dos['dos_at_fermi']:.4f}`",
                f"- Peak DOS: `{dos['peak_dos']:.4f}` at `{dos['peak_energy_eV']:.4f}` eV",
            ]
        )
    if (source / "EIGENVAL").exists():
        band = analyze_band(source)
        lines.extend(
            [
                "",
                "## Band",
                f"- Band gap (eV): `{band['band_gap_eV']:.4f}`",
                f"- Direct gap: `{str(band['is_direct_gap']).lower()}`",
                f"- VBM (eV): `{band['vbm_eV']:.4f}`",
                f"- CBM (eV): `{band['cbm_eV']:.4f}`",
            ]
        )
    if "ISPIN = 2" in (source / "INCAR").read_text() and (source / "OUTCAR").exists():
        mag = analyze_magnetism(source)
        lines.extend(
            [
                "",
                "## Magnetism",
                f"- Total moment (muB): `{mag['total_moment_muB']:.4f}`" if mag["total_moment_muB"] is not None else "- Total moment (muB): `unknown`",
                f"- Max local moment (muB): `{mag['max_local_moment_muB']:.4f}`" if mag["max_local_moment_muB"] is not None else "- Max local moment (muB): `unknown`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def default_output(source: Path) -> Path:
    if source.is_file():
        return source.parent / f"{source.stem}.ANALYSIS_REPORT.md"
    return source / "ANALYSIS_REPORT.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown analysis report for a VASP result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()
    source = Path(args.path).expanduser().resolve()
    record = analyze_path(source)
    output = Path(args.output).expanduser().resolve() if args.output else default_output(source)
    output.write_text(render_markdown(record))
    print(output)


if __name__ == "__main__":
    main()
