# vasp-analysis

Standalone skill for post-run VASP result analysis and multi-run comparison.

## Install

```bash
npx skills add chatmaterials/vasp-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_vasp_result.py fixtures/completed --json
python3 scripts/compare_vasp_results.py fixtures/compare/alpha fixtures/compare/beta --json
python3 scripts/structure_change_vasp.py fixtures/compare/alpha/POSCAR fixtures/compare/beta/POSCAR --json
python3 scripts/analyze_vasp_dos.py fixtures/completed --json
python3 scripts/analyze_vasp_band.py fixtures/completed --json
python3 scripts/analyze_vasp_magnetism.py fixtures/completed --json
python3 scripts/analyze_vasp_voltage.py fixtures/battery/host fixtures/battery/lithiated --reference-energy -1.50 --json
python3 scripts/analyze_vasp_neb.py fixtures/neb --json
python3 scripts/export_analysis_report.py fixtures/completed
python3 scripts/run_regression.py
```
