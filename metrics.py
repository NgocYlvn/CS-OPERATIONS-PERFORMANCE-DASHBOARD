from __future__ import annotations

from typing import Dict
import numpy as np
import pandas as pd
from .config import *
from .common import *

def calculate_active_customers(shipment_df: pd.DataFrame) -> float:
    """
    Active Customers source: Shipment volume.
    For a single selected month, this returns the sum across selected offices.
    For multi-month / All selection, it returns the average monthly active-customer total
    because the source sheet contains monthly counts rather than customer-level IDs.
    """
    if shipment_df is None or shipment_df.empty or "Active Customers" not in shipment_df.columns:
        return 0.0

    d = shipment_df[["MonthDate", "Active Customers"]].copy()
    d["Active Customers"] = pd.to_numeric(d["Active Customers"], errors="coerce")
    d = d.dropna(subset=["MonthDate", "Active Customers"])

    if d.empty:
        return 0.0

    monthly = (
        d.groupby("MonthDate", as_index=False)["Active Customers"]
        .sum(min_count=1)
        .dropna(subset=["Active Customers"])
    )
    if monthly.empty:
        return 0.0

    if len(monthly) == 1:
        return float(monthly["Active Customers"].iloc[0])

    return float(monthly["Active Customers"].mean())


def calculate_kpis(hc, workload, fte, shipment) -> Dict[str, float]:
    total_workload_hours = float(workload["Workload Hours"].sum()) if not workload.empty and "Workload Hours" in workload.columns else 0.0
    required_fte_total_period = total_workload_hours / CAPACITY_HOURS_PER_FTE if total_workload_hours else 0.0

    # Capacity is summed over selected months. Actual FTE card is average monthly FTE.
    monthly_fte = pd.DataFrame()
    if not fte.empty:
        monthly_fte = fte.groupby("MonthDate", dropna=True)["Actual FTE"].sum().reset_index()
    actual_fte_avg = float(monthly_fte["Actual FTE"].mean()) if not monthly_fte.empty else 0.0
    capacity_hours = float((monthly_fte["Actual FTE"] * CAPACITY_HOURS_PER_FTE).sum()) if not monthly_fte.empty else 0.0
    required_fte_avg = required_fte_total_period / max(len(monthly_fte), 1) if not monthly_fte.empty else required_fte_total_period

    # HC is average monthly total when multiple months are selected.
    approved_hc = weighted_period_avg(hc, "Total Approved HC") if not hc.empty and "Total Approved HC" in hc.columns else 0.0
    actual_hc = weighted_period_avg(hc, "Total Actual HC") if not hc.empty and "Total Actual HC" in hc.columns else 0.0
    total_shipment = float(shipment["Total Shipment"].sum()) if not shipment.empty and "Total Shipment" in shipment.columns else 0.0
    util = safe_div(total_workload_hours, capacity_hours)
    fte_gap = actual_fte_avg - required_fte_avg
    return {
        "Approved HC": approved_hc,
        "Actual HC": actual_hc,
        "Actual FTE": actual_fte_avg,
        "Required FTE": required_fte_avg,
        "Capacity Hours": capacity_hours,
        "Workload Hours": total_workload_hours,
        "Utilization": util,
        "FTE Gap": fte_gap,
        "Total Shipment": total_shipment,
    }


def build_reconciliation(hc, workload, fte, shipment) -> pd.DataFrame:
    kpis = calculate_kpis(hc, workload, fte, shipment)
    rows = []
    # Reference values from HC if available.
    ref_actual_hc = weighted_period_avg(hc, "Total Actual HC") if not hc.empty and "Total Actual HC" in hc.columns else np.nan
    ref_approved_hc = weighted_period_avg(hc, "Total Approved HC") if not hc.empty and "Total Approved HC" in hc.columns else np.nan
    ref_required_hc = weighted_period_avg(hc, "Total Required HC") if not hc.empty and "Total Required HC" in hc.columns else np.nan
    ref_ship = shipment["Total Shipment"].sum() if not shipment.empty and "Total Shipment" in shipment.columns else np.nan

    def add(kpi, calc, ref, status="PASS", note=""):
        diff = calc - ref if pd.notna(ref) else np.nan
        rows.append({"KPI": kpi, "Calculated Value": calc, "Reference Value": ref, "Difference": diff, "Status": status, "Note": note})

    add("Total Approved HC", kpis["Approved HC"], ref_approved_hc, "PASS" if pd.notna(ref_approved_hc) else "WARNING", "Source: HC")
    add("Total Actual HC", kpis["Actual HC"], ref_actual_hc, "PASS" if pd.notna(ref_actual_hc) else "WARNING", "Source: HC")
    add("Total Shipment", kpis["Total Shipment"], ref_ship, "PASS" if pd.notna(ref_ship) else "WARNING", "Source: Shipment volume")
    add("Required FTE", kpis["Required FTE"], ref_required_hc, "WARNING", "Dashboard calculates from Workload Hours / 167.2; HC value is reference only.")
    add("Utilization", kpis["Utilization"], np.nan, "WARNING", "Dashboard formula: Workload Hours / Capacity Hours.")
    return pd.DataFrame(rows)
