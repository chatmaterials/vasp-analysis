#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_energy(path: Path) -> float:
    outcar = path / "OUTCAR"
    text = outcar.read_text(errors="ignore")
    matches = re.findall(r"TOTEN\s*=\s*([\-0-9.Ee+]+)", text)
    if not matches:
        raise SystemExit(f"No TOTEN found in {outcar}")
    return float(matches[-1])


def analyze(root: Path) -> dict[str, object]:
    image_dirs = sorted([path for path in root.iterdir() if path.is_dir() and path.name.isdigit()])
    if not image_dirs:
        raise SystemExit("No numbered NEB image directories were found")
    images = []
    for image in image_dirs:
        images.append({"image": image.name, "energy_eV": read_energy(image)})
    reference = images[0]["energy_eV"]
    for image in images:
        image["relative_energy_eV"] = image["energy_eV"] - reference
    highest_rel = max(image["relative_energy_eV"] for image in images)
    reaction_energy = images[-1]["relative_energy_eV"]
    forward_barrier = highest_rel
    reverse_barrier = highest_rel - reaction_energy
    highest = max(images, key=lambda item: item["relative_energy_eV"])
    return {
        "path": str(root),
        "images": images,
        "barrier_eV": forward_barrier,
        "forward_barrier_eV": forward_barrier,
        "reverse_barrier_eV": reverse_barrier,
        "reaction_energy_eV": reaction_energy,
        "highest_image": highest["image"],
        "observations": ["NEB barrier estimated from image energies relative to the initial state."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a simple VASP NEB image set.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
