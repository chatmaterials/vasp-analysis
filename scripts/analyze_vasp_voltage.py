#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_energy(path: Path) -> float:
    outcar = (path / "OUTCAR") if path.is_dir() else path
    text = outcar.read_text(errors="ignore")
    matches = re.findall(r"TOTEN\s*=\s*([\-0-9.Ee+]+)", text)
    if not matches:
        raise SystemExit(f"No TOTEN found in {outcar}")
    return float(matches[-1])


def analyze(host: Path, lithiated: Path, li_reference_energy: float, delta_ion: int = 1) -> dict[str, object]:
    e_host = read_energy(host)
    e_lithiated = read_energy(lithiated)
    voltage = -(e_lithiated - e_host - delta_ion * li_reference_energy) / delta_ion
    return {
        "host": str(host),
        "lithiated": str(lithiated),
        "host_energy_eV": e_host,
        "lithiated_energy_eV": e_lithiated,
        "reference_energy_per_ion_eV": li_reference_energy,
        "delta_ion": delta_ion,
        "average_voltage_V": voltage,
        "observations": ["Average insertion voltage estimated from total energies."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate an average insertion voltage from two VASP states.")
    parser.add_argument("host")
    parser.add_argument("lithiated")
    parser.add_argument("--reference-energy", type=float, required=True, help="Reference energy per inserted ion in eV, e.g. Li metal energy per atom.")
    parser.add_argument("--delta-ion", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.host).expanduser().resolve(),
        Path(args.lithiated).expanduser().resolve(),
        args.reference_energy,
        args.delta_ion,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
