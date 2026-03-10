#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_vasp_result import analyze_path


def compare(paths: list[Path]) -> dict[str, object]:
    records = [analyze_path(path) for path in paths]
    energies = [record["final_energy_eV"] for record in records if record["final_energy_eV"] is not None]
    reference = min(energies) if energies else None
    for record in records:
        energy = record["final_energy_eV"]
        record["relative_energy_meV"] = (energy - reference) * 1000.0 if energy is not None and reference is not None else None
    records.sort(key=lambda item: (item["final_energy_eV"] is None, item["final_energy_eV"]))
    return {"reference_energy_eV": reference, "results": records}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare multiple VASP result directories.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = compare([Path(path).expanduser().resolve() for path in args.paths])
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
