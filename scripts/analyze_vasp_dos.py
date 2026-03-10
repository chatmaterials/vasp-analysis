#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze_path(path: Path) -> dict[str, object]:
    doscar = path / "DOSCAR" if path.is_dir() else path
    lines = doscar.read_text().splitlines()
    if len(lines) < 7:
        raise SystemExit("DOSCAR is too short to analyze")
    header = lines[5].split()
    emin = float(header[0])
    emax = float(header[1])
    nedos = int(float(header[2]))
    efermi = float(header[3])
    entries = []
    for line in lines[6 : 6 + nedos]:
        parts = line.split()
        if len(parts) < 3:
            continue
        entries.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if not entries:
        raise SystemExit("DOSCAR contains no DOS entries")
    nearest = min(entries, key=lambda item: abs(item[0] - efermi))
    peak = max(entries, key=lambda item: item[1])
    observations = []
    if abs(nearest[1]) < 1e-6:
        observations.append("DOS at the Fermi level is effectively zero in the sampled data.")
    else:
        observations.append("Finite DOS is present at the sampled Fermi level.")
    return {
        "path": str(path),
        "emin_eV": emin,
        "emax_eV": emax,
        "nedos": nedos,
        "efermi_eV": efermi,
        "dos_at_fermi": nearest[1],
        "peak_dos": peak[1],
        "peak_energy_eV": peak[0],
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a VASP DOSCAR file or result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_path(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
