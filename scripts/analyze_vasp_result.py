#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="ignore") if path.exists() else ""


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace("D", "e").replace("d", "e"))
    except ValueError:
        return None


def count_atoms(poscar: Path) -> int | None:
    text = read_text(poscar).splitlines()
    if len(text) < 7:
        return None
    for index in (5, 6):
        try:
            values = [int(item) for item in text[index].split()]
        except ValueError:
            continue
        if values:
            return sum(values)
    return None


def extract_max_force(text: str) -> float | None:
    lines = text.splitlines()
    last_max = None
    for i, line in enumerate(lines):
        if "TOTAL-FORCE (eV/Angst)" not in line:
            continue
        forces = []
        for candidate in lines[i + 1 :]:
            parts = candidate.split()
            if len(parts) < 6:
                if forces:
                    break
                continue
            try:
                fx, fy, fz = map(float, parts[-3:])
            except ValueError:
                if forces:
                    break
                continue
            forces.append((fx * fx + fy * fy + fz * fz) ** 0.5)
        if forces:
            last_max = max(forces)
    return last_max


def analyze_path(path: Path) -> dict[str, object]:
    outcar = read_text(path / "OUTCAR")
    oszicar = read_text(path / "OSZICAR")
    energies = re.findall(r"TOTEN\s*=\s*([\-0-9.Ee+]+)", outcar)
    final_energy = to_float(energies[-1]) if energies else None
    completed = "General timing and accounting informations for this job" in outcar
    ionic_converged = "reached required accuracy - stopping structural energy minimisation" in outcar
    natoms = count_atoms(path / "POSCAR")
    max_force = extract_max_force(outcar)
    observations: list[str] = []
    if completed and ionic_converged:
        observations.append("Run completed and ionic relaxation converged.")
    elif completed:
        observations.append("Run completed but ionic convergence was not confirmed.")
    else:
        observations.append("Run appears incomplete.")
    if max_force is not None and max_force > 0.05:
        observations.append("Residual forces remain comparatively large.")
    if "BRMIX" in outcar or "BRMIX" in oszicar:
        observations.append("Charge-mixing instability was reported.")
    energy_per_atom = final_energy / natoms if final_energy is not None and natoms else None
    return {
        "path": str(path),
        "completed": completed,
        "ionic_converged": ionic_converged,
        "natoms": natoms,
        "final_energy_eV": final_energy,
        "energy_per_atom_eV": energy_per_atom,
        "max_force_eV_A": max_force,
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a VASP result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    record = analyze_path(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
