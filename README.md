# CS OPERATIONS PERFORMANCE DASHBOARD — Refactored

## Run
```bash
streamlit run app.py
```

Keep the default workbook `(Not for Office Input) MASTER DATA SOURCE.xlsm` in the same working folder as before, or use the existing Upload Excel File control.

## What changed
Only code organization. The baseline logic, formulas, filter behavior, HTML, Plotly rendering code and CSS cascade are preserved.

## Structure
- `app.py` — launcher and original Streamlit page config
- `dashboard/config.py` — constants, theme, sheet names
- `dashboard/styles.py` — all original CSS blocks in original cascade order
- `dashboard/common.py` — shared helpers and UI primitives
- `dashboard/data.py` — Excel loading, normalization and filters
- `dashboard/activity.py` — C/A/S/E workload detail rendering
- `dashboard/metrics.py` — KPI/reconciliation calculation helpers
- `dashboard/charts.py` — chart/table presentation functions
- `dashboard/cover.py` — Home/Cover page
- `dashboard/main_logic.py` — dashboard orchestration

## Maintenance rule
Do not change formulas while editing UI modules, and do not change CSS while editing data/calculation modules. Validate the same workbook + Month + Office against the baseline after every change.
