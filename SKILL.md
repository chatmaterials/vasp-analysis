---
name: "vasp-analysis"
description: "Use when the task is to analyze completed or partially completed VASP results, including energy extraction, convergence interpretation, structure or force summaries, comparing multiple VASP runs, and writing compact reports from OUTCAR, OSZICAR, INCAR, or POSCAR."
---

# VASP Analysis

Use this skill for post-run VASP result analysis rather than workflow setup.

## When to use

- analyze a completed or incomplete VASP run
- compare energies across multiple VASP directories
- summarize convergence, forces, or status from `OUTCAR` and `OSZICAR`
- write a compact status or comparison report from existing results

## Use the bundled helpers

- `scripts/analyze_vasp_result.py`
  Summarize a single VASP result directory.
- `scripts/compare_vasp_results.py`
  Compare multiple VASP result directories by energy and status.
- `scripts/structure_change_vasp.py`
  Compare two VASP structures and summarize lattice or coordinate changes.
- `scripts/analyze_vasp_dos.py`
  Extract DOS-oriented summary data from `DOSCAR`.
- `scripts/analyze_vasp_band.py`
  Extract band-gap-oriented summary data from `EIGENVAL`.
- `scripts/analyze_vasp_magnetism.py`
  Extract total and local magnetic moments from `OUTCAR`.
- `scripts/analyze_vasp_voltage.py`
  Estimate an average insertion voltage from two VASP states.
- `scripts/analyze_vasp_neb.py`
  Estimate a simple NEB barrier from numbered VASP image directories.
- `scripts/export_analysis_report.py`
  Export a markdown analysis report from a VASP result directory.

## Guardrails

- Do not claim a scientific conclusion from an incomplete or unconverged run.
- Distinguish raw extraction from interpretation.
- If directories are not numerically comparable, say so plainly.
