#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_poscar(path: Path) -> dict[str, object]:
    lines = path.read_text().splitlines()
    scale = float(lines[1].split()[0])
    lattice = [[float(x) * scale for x in lines[i].split()] for i in range(2, 5)]
    counts = [int(x) for x in lines[6].split()]
    natoms = sum(counts)
    coord_start = 8
    coords = [[float(x) for x in lines[coord_start + i].split()[:3]] for i in range(natoms)]
    return {"lattice": lattice, "natoms": natoms, "coords": coords}


def vector_length(vec: list[float]) -> float:
    return sum(value * value for value in vec) ** 0.5


def analyze(initial: Path, final: Path) -> dict[str, object]:
    a = read_poscar(initial)
    b = read_poscar(final)
    lattice_lengths_a = [vector_length(vec) for vec in a["lattice"]]
    lattice_lengths_b = [vector_length(vec) for vec in b["lattice"]]
    lattice_delta = [after - before for before, after in zip(lattice_lengths_a, lattice_lengths_b)]
    max_coord_shift = max(
        (
            sum((after[i] - before[i]) ** 2 for i in range(3)) ** 0.5
            for before, after in zip(a["coords"], b["coords"])
        ),
        default=0.0,
    )
    return {
        "initial": str(initial),
        "final": str(final),
        "natoms": a["natoms"],
        "lattice_lengths_initial": lattice_lengths_a,
        "lattice_lengths_final": lattice_lengths_b,
        "lattice_length_delta": lattice_delta,
        "max_fractional_coordinate_shift": max_coord_shift,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two VASP POSCAR-like structures.")
    parser.add_argument("initial")
    parser.add_argument("final")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.initial).expanduser().resolve(), Path(args.final).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
