#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze_path(path: Path) -> dict[str, object]:
    eig = path / "EIGENVAL" if path.is_dir() else path
    lines = eig.read_text().splitlines()
    if len(lines) < 8:
        raise SystemExit("EIGENVAL is too short to analyze")
    nelect, nkpoints, nbands = [int(x) for x in lines[5].split()[:3]]
    blocks = []
    i = 7
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        k_parts = lines[i].split()
        if len(k_parts) < 4:
            break
        kpoint = tuple(float(x) for x in k_parts[:3])
        bands = []
        for j in range(nbands):
            parts = lines[i + 1 + j].split()
            bands.append((int(parts[0]), float(parts[1]), float(parts[2])))
        blocks.append((kpoint, bands))
        i += nbands + 2
    occupied = []
    empty = []
    for kpoint, bands in blocks:
        for _, energy, occ in bands:
            if occ > 0.5:
                occupied.append((energy, kpoint))
            else:
                empty.append((energy, kpoint))
    vbm, vbm_k = max(occupied, key=lambda item: item[0])
    cbm, cbm_k = min(empty, key=lambda item: item[0])
    gap = cbm - vbm
    return {
        "path": str(path),
        "nelect": nelect,
        "nkpoints": nkpoints,
        "nbands": nbands,
        "vbm_eV": vbm,
        "cbm_eV": cbm,
        "band_gap_eV": gap,
        "is_direct_gap": tuple(round(x, 8) for x in vbm_k) == tuple(round(x, 8) for x in cbm_k),
        "observations": ["Positive band gap extracted from occupied and empty states." if gap > 0 else "No positive band gap was detected."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a VASP EIGENVAL file or result directory.")
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
