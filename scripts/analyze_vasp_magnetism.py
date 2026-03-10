#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def analyze_path(path: Path) -> dict[str, object]:
    outcar = path / "OUTCAR" if path.is_dir() else path
    text = outcar.read_text(errors="ignore")
    total_match = re.search(r"magnetization\s+([\-0-9.Ee+]+)\s*$", text, re.MULTILINE)
    total_moment = float(total_match.group(1)) if total_match else None
    lines = text.splitlines()
    local_moments: list[dict[str, object]] = []
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("magnetization (x)"):
            for candidate in lines[idx + 1 :]:
                parts = candidate.split()
                if len(parts) < 5:
                    if local_moments:
                        break
                    continue
                if not parts[0].isdigit():
                    if local_moments:
                        break
                    continue
                local_moments.append(
                    {
                        "ion": int(parts[0]),
                        "s": float(parts[1]),
                        "p": float(parts[2]),
                        "d": float(parts[3]),
                        "tot": float(parts[4]),
                    }
                )
            break
    max_local = max((abs(item["tot"]) for item in local_moments), default=None)
    observations = []
    if total_moment is not None:
        observations.append("Total magnetic moment extracted from OUTCAR.")
    if max_local is not None and max_local > 1.0:
        observations.append("At least one atom carries a sizable local moment.")
    return {
        "path": str(path),
        "total_moment_muB": total_moment,
        "local_moments": local_moments,
        "max_local_moment_muB": max_local,
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze magnetic moments from a VASP OUTCAR or result directory.")
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
