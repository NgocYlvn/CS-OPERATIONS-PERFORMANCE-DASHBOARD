from __future__ import annotations

import re
import html
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from .config import *

def safe_float(value) -> float:
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        value = value.replace(",", "").strip()
        if value.startswith("="):
            return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def clean_col(col) -> str:
    col = str(col).replace("\n", " ").replace("\r", " ")
    col = re.sub(r"\s+", " ", col).strip()
    return col


def normalize_office(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def parse_month(value) -> pd.Timestamp | pd.NaT:
    if pd.isna(value) or value == "":
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        return pd.Timestamp(year=value.year, month=value.month, day=1)
    text = str(value).strip()

    # Adapter for the new MASTER DATA SOURCE workbook:
    # Month is stored as Apr..Mar while the dashboard logic still works with
    # real MonthDate values. FY2026 = Apr-Dec 2026 + Jan-Mar 2027.
    month_only = {
        "jan": (2027, 1), "feb": (2027, 2), "mar": (2027, 3),
        "apr": (2026, 4), "may": (2026, 5), "jun": (2026, 6),
        "jul": (2026, 7), "aug": (2026, 8), "sep": (2026, 9),
        "oct": (2026, 10), "nov": (2026, 11), "dec": (2026, 12),
    }
    key = text[:3].lower()
    if len(text) <= 4 and key in month_only:
        year, month = month_only[key]
        return pd.Timestamp(year=year, month=month, day=1)

    for fmt in ["%b-%y", "%b-%Y", "%Y-%m", "%m/%Y", "%Y/%m"]:
        try:
            dt = pd.to_datetime(text, format=fmt)
            return pd.Timestamp(year=dt.year, month=dt.month, day=1)
        except Exception:
            pass
    try:
        dt = pd.to_datetime(text, errors="coerce")
        if pd.isna(dt):
            return pd.NaT
        return pd.Timestamp(year=dt.year, month=dt.month, day=1)
    except Exception:
        return pd.NaT


def format_month(ts) -> str:
    if pd.isna(ts):
        return ""
    return pd.Timestamp(ts).strftime("%b-%y")


def numeric_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0)


def read_sheet(path: str | Path, sheet: str, header: int = 1) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, sheet_name=sheet, header=header, engine="openpyxl")
        df.columns = [clean_col(c) for c in df.columns]
        df = df.dropna(how="all")
        return df
    except Exception:
        return pd.DataFrame()


def ensure_cols(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    return df


def first_existing(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    clean_map = {clean_col(c).lower(): c for c in df.columns}
    for c in candidates:
        key = clean_col(c).lower()
        if key in clean_map:
            return clean_map[key]
    return None


def weighted_period_avg(df: pd.DataFrame, value_col: str, group_col: str = "MonthDate") -> float:
    """Average of valid monthly totals only; blank future months are excluded."""
    if df.empty or value_col not in df.columns or group_col not in df.columns:
        return 0.0

    valid = df[[group_col, value_col]].copy()
    valid[value_col] = pd.to_numeric(valid[value_col], errors="coerce")
    valid = valid.dropna(subset=[group_col, value_col])

    if valid.empty:
        return 0.0

    monthly = (
        valid.groupby(group_col, dropna=True)[value_col]
        .sum(min_count=1)
        .reset_index()
        .dropna(subset=[value_col])
    )
    if monthly.empty:
        return 0.0
    return float(monthly[value_col].mean())


def safe_div(num: float, den: float) -> float:
    return float(num) / float(den) if den not in [0, 0.0] and not pd.isna(den) else 0.0


def fmt_num(value: float, decimals: int = 1, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}{suffix}"


def fmt_int(value: float) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


def fmt_pct(value: float) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value * 100:,.1f}%"


def status_from_util(util: float) -> Tuple[str, str, str]:
    """Standard workload status rule used across KPI/status displays."""
    if util <= 0:
        return "NO DATA", COLORS["muted"], COLORS["light_blue"]
    if util < 0.90:
        return "LESS LOAD", COLORS["green"], "#DCFCE7"
    if util <= 0.95:
        return "BALANCED", COLORS["blue"], "#DBEAFE"
    if util <= 1.00:
        return "HIGH LOAD", COLORS["amber"], "#FEF3C7"
    return "OVERLOAD", COLORS["red"], "#FEE2E2"



def _office_compare_card(
    office_name: str,
    primary_label: str,
    primary_value: str,
    metrics: List[Tuple[str, str, str]],
    status_text: str,
    status_color: str,
    status_bg: str,
) -> None:
    # Render one compact office benchmark card. UI only.
    metric_html = "".join(
        f'<div class="office-compare-metric"><div class="office-compare-metric-label">{html.escape(str(label))}</div><div class="office-compare-metric-value {css_class}">{html.escape(str(value))}</div></div>'
        for label, value, css_class in metrics
    )
    st.markdown(
        f'<div class="office-compare-card" style="--office-status:{status_color};--office-status-bg:{status_bg};"><div class="office-compare-top"><div class="office-compare-name">{html.escape(str(office_name))}</div><div class="office-compare-status">{html.escape(str(status_text))}</div></div><div class="office-compare-primary"><div class="office-compare-primary-label">{html.escape(str(primary_label))}</div><div class="office-compare-primary-value">{html.escape(str(primary_value))}</div></div><div class="office-compare-grid">{metric_html}</div></div>',
        unsafe_allow_html=True,
    )


def _office_comparison_heading(title: str) -> None:
    st.markdown(
        f'<div class="office-comparison-heading">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )


def render_hc_office_comparison(hc_filtered_all_offices: pd.DataFrame) -> None:
    # Reuse existing HC source-of-truth functions and status thresholds.
    _office_comparison_heading("Utilization by Office")
    cols = st.columns(4, gap="small")
    for col, office_name in zip(cols, STANDARD_OFFICES):
        if hc_filtered_all_offices is not None and not hc_filtered_all_offices.empty and "Office" in hc_filtered_all_offices.columns:
            office_df = hc_filtered_all_offices[hc_filtered_all_offices["Office"] == office_name].copy()
        else:
            office_df = pd.DataFrame()

        if office_df.empty:
            actual = required = gap = util = float("nan")
            status_text, status_color, status_bg = "NO DATA", COLORS["muted"], COLORS["light_blue"]
        else:
            actual = weighted_period_avg(office_df, "Total Actual HC")
            required = weighted_period_avg(office_df, "Total Required HC")
            gap = required - actual
            util = hc_capacity_utilization(office_df)
            # Office status is determined by Office Workload (utilization),
            # using the standard workload thresholds:
            # < 90%       -> LESS LOAD / Green
            # 90% - 95%   -> BALANCED / Blue
            # >95% - 100% -> HIGH LOAD / Orange
            # >100%       -> OVERLOAD / Red
            if pd.isna(util):
                status_text, status_color, status_bg = "NO DATA", COLORS["muted"], COLORS["light_blue"]
            else:
                status_text, status_color, status_bg = status_from_util(util)

        gap_class = "negative" if (not pd.isna(gap) and gap > 0) else ("positive" if (not pd.isna(gap) and gap < 0) else "")
        gap_text = "N/A" if pd.isna(gap) else f"{gap:+,.2f}"
        with col:
            _office_compare_card(
                office_name,
                "Office Workload",
                "N/A" if pd.isna(util) else fmt_pct(util),
                [
                    ("Actual HC", "N/A" if pd.isna(actual) else fmt_num(actual, 2), ""),
                    ("Required HC", "N/A" if pd.isna(required) else fmt_num(required, 2), ""),
                    ("HC Gap", gap_text, gap_class),
                    ("Status", status_text.title(), ""),
                ],
                status_text, status_color, status_bg,
            )


def _fte_office_summary(office_fte: pd.DataFrame, selected_month: str) -> Tuple[float, float, float, Tuple[str, str, str]]:
    # Apply the exact Section 3 month logic to one office.
    if office_fte is None or office_fte.empty:
        return float("nan"), float("nan"), float("nan"), ("NO DATA", COLORS["muted"], COLORS["light_blue"])
    d = office_fte.copy()
    d["Available Time"] = pd.to_numeric(d.get("Available Time"), errors="coerce")
    d["Actual Working Time"] = pd.to_numeric(d.get("Actual Working Time"), errors="coerce")
    monthly = (
        d.dropna(subset=["MonthDate", "Available Time", "Actual Working Time"])
        .groupby("MonthDate", as_index=False)
        .agg(
            Total_Available_Time=("Available Time", "sum"),
            Total_Actual_Working_Time=("Actual Working Time", "sum"),
        )
    )
    if monthly.empty:
        return float("nan"), float("nan"), float("nan"), ("NO DATA", COLORS["muted"], COLORS["light_blue"])
    if str(selected_month).strip().lower() == "all":
        total_available = float(monthly["Total_Available_Time"].mean())
        total_actual = float(monthly["Total_Actual_Working_Time"].mean())
    else:
        row = monthly.sort_values("MonthDate").iloc[-1]
        total_available = float(row["Total_Available_Time"])
        total_actual = float(row["Total_Actual_Working_Time"])
    workload = safe_div(total_actual, total_available)
    return total_available, total_actual, workload, status_from_util(workload)


def render_fte_office_comparison(fte_filtered_all_offices: pd.DataFrame, selected_month: str) -> None:
    # Reuse exact Section 3 FTE formula / month handling.
    _office_comparison_heading("Office Workload per FTE")
    cols = st.columns(4, gap="small")
    for col, office_name in zip(cols, STANDARD_OFFICES):
        if fte_filtered_all_offices is not None and not fte_filtered_all_offices.empty and "Office" in fte_filtered_all_offices.columns:
            office_df = fte_filtered_all_offices[fte_filtered_all_offices["Office"] == office_name].copy()
        else:
            office_df = pd.DataFrame()
        available, actual, workload, status = _fte_office_summary(office_df, selected_month)
        status_text, status_color, status_bg = status
        variance = actual - available if not pd.isna(actual) and not pd.isna(available) else float("nan")
        variance_class = "negative" if (not pd.isna(variance) and variance > 0) else ("positive" if not pd.isna(variance) else "")
        with col:
            _office_compare_card(
                office_name,
                "FTE Workload",
                "N/A" if pd.isna(workload) else fmt_pct(workload),
                [
                    ("Available Time", "N/A" if pd.isna(available) else fmt_num(available, 0), ""),
                    ("Actual Time", "N/A" if pd.isna(actual) else fmt_num(actual, 0), ""),
                    ("Gap", "N/A" if pd.isna(variance) else fmt_num(variance, 0), variance_class),
                    ("Status", status_text.title(), ""),
                ],
                status_text, status_color, status_bg,
            )



def ui_icon_svg(kind: str, color: str, bg: str, circle_class: str = "kpi-icon-circle") -> str:
    """Inline corporate SVG icon - UI only, no external dependency."""
    icons = {
        "people": """
            <circle cx="12" cy="8" r="3"></circle>
            <circle cx="5.5" cy="10" r="2.2"></circle>
            <circle cx="18.5" cy="10" r="2.2"></circle>
            <path d="M7.5 20v-2.2c0-3 2-5.3 4.5-5.3s4.5 2.3 4.5 5.3V20"></path>
            <path d="M2 19v-1.4c0-2.3 1.5-4 3.6-4"></path>
            <path d="M22 19v-1.4c0-2.3-1.5-4-3.6-4"></path>
        """,
        "people_active": """
            <circle cx="10" cy="8" r="3"></circle>
            <path d="M4.5 20v-2.3c0-3.1 2.4-5.4 5.5-5.4s5.5 2.3 5.5 5.4V20"></path>
            <path d="M16 9l1.8 1.8L21 7"></path>
        """,
        "people_required": """
            <circle cx="9" cy="8" r="3"></circle>
            <path d="M3.5 20v-2.3c0-3.1 2.4-5.4 5.5-5.4s5.5 2.3 5.5 5.4V20"></path>
            <path d="M18 8v7M14.5 11.5h7"></path>
        """,
        "balance": """
            <path d="M12 4v16"></path>
            <path d="M6 7h12"></path>
            <path d="M6 7l-3 6h6L6 7z"></path>
            <path d="M18 7l-3 6h6l-3-6z"></path>
            <path d="M8 20h8"></path>
        """,
        "package": """
            <path d="M4 8l8-4 8 4-8 4-8-4z"></path>
            <path d="M4 8v8l8 4 8-4V8"></path>
            <path d="M12 12v8"></path>
        """,
        "customers": """
            <circle cx="9" cy="8" r="3"></circle>
            <circle cx="17" cy="9" r="2.5"></circle>
            <path d="M3.5 20v-2c0-3.1 2.4-5.3 5.5-5.3s5.5 2.2 5.5 5.3v2"></path>
            <path d="M15 14c2.8 0 5 1.8 5 4.5V20"></path>
        """,
        "clipboard": """
            <rect x="5" y="5" width="14" height="16" rx="2"></rect>
            <path d="M9 5V3h6v2"></path>
            <path d="M8.5 10h7M8.5 14h7M8.5 18h5"></path>
        """,
        "gauge": """
            <path d="M4 17a8 8 0 0 1 16 0"></path>
            <path d="M12 17l4-5"></path>
            <circle cx="12" cy="17" r="1.4"></circle>
        """,
        "target": """
            <circle cx="12" cy="12" r="8"></circle>
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 12l6-6"></path>
            <path d="M16 6h3v3"></path>
        """,
    }
    path = icons.get(kind, icons["clipboard"])
    return f'<span class="{circle_class}" style="color:{color};background:{bg};"><svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg></span>'


def hc_icon_for_label(label: str) -> str:
    key = str(label).upper()
    if "APPROVED" in key:
        return ui_icon_svg("people", "#06183F", "#EEF3F8")
    if "ACTUAL" in key:
        return ui_icon_svg("people_active", "#0DBAEE", "#E8F8FD")
    if "REQUIRED" in key:
        return ui_icon_svg("people_required", "#E6761B", "#FFF2E8")
    return ui_icon_svg("balance", "#6EA52B", "#F1F8E8")


def general_kpi_icon(label: str) -> str:
    key = str(label).lower()
    if "shipment" in key:
        return ui_icon_svg("package", "#0DBAEE", "#E8F8FD")
    if "customer" in key:
        return ui_icon_svg("customers", "#06183F", "#EEF3F8")
    if "workload" in key or "working time" in key or "available time" in key:
        return ui_icon_svg("clipboard", "#0DBAEE", "#E8F8FD")
    return ui_icon_svg("clipboard", "#06183F", "#EEF3F8")


def kpi_card(label: str, value: str, note: str = "", status: Optional[Tuple[str, str, str]] = None):
    badge = ""
    if status:
        txt, color, bg = status
        badge = f'<span class="status-badge" style="color:{color};background:{bg};">{txt}</span>'
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
            {badge}
        </div>
        """,
        unsafe_allow_html=True,
    )



def hc_detail_card(
    label: str,
    total_value: float,
    mng_value: Optional[float] = None,
    pic_value: Optional[float] = None,
    note_left: str = "MNG",
    note_right: str = "PIC",
    status_text: Optional[str] = None,
    status_color: Optional[str] = None,
    status_bg: Optional[str] = None,
):
    """Executive HC card with equal height and two aligned detail blocks at the bottom."""
    details_html = ""
    if mng_value is not None or pic_value is not None:
        left_decimals = 2 if "REQUIRED" in label.upper() else 0
        right_decimals = 2 if "REQUIRED" in label.upper() else 0
        left_val = fmt_num(mng_value or 0, left_decimals)
        right_val = fmt_num(pic_value or 0, right_decimals)
        details_html = f"""
        <div class="hc-detail-row">
            <div class="hc-detail-item">
                <div class="hc-detail-label">{note_left}</div>
                <div class="hc-detail-value">{left_val}</div>
            </div>
            <div class="hc-detail-divider"></div>
            <div class="hc-detail-item">
                <div class="hc-detail-label">{note_right}</div>
                <div class="hc-detail-value">{right_val}</div>
            </div>
        </div>
        """

    status_html = ""
    if status_text:
        status_html = (
            f'<span class="status-badge" '
            f'style="color:{status_color};background:{status_bg};margin-top:10px;">'
            f'{status_text}</span>'
        )

    # UI-only semantic color hierarchy for Office Capacity Snapshot:
    # Approved = Navy, Actual = Corporate Blue, Required = Orange.
    label_upper = label.upper()
    if "REQUIRED" in label_upper:
        total_color_class = "hc-total-required"
    elif "ACTUAL" in label_upper:
        total_color_class = "hc-total-actual"
    else:
        total_color_class = "hc-total-approved"

    st.markdown(
        f"""
        <div class="hc-kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="hc-main-row">
                {hc_icon_for_label(label)}
                <div class="hc-kpi-total {total_color_class}">{fmt_num(total_value, 2 if "REQUIRED" in label.upper() else 0)}</div>
            </div>
            {status_html}
            {details_html}
        </div>
        """,
        unsafe_allow_html=True,
    )



def hc_variance_card(
    label: str,
    value: float,
    formula_text: str,
    status_text: str,
    status_color: str,
    status_bg: str,
):
    """Centered variance card to visually balance the HC cards."""
    st.markdown(
        f"""
        <div class="hc-kpi-card hc-variance-card">
            <div class="kpi-label">{label}</div>
            <div class="hc-main-row">
                {ui_icon_svg("balance", "#6EA52B", "#F1F8E8")}
                <div class="hc-kpi-total" style="color:{status_color} !important;">{fmt_num(value, 2)}</div>
            </div>
            <div class="hc-variance-formula">{formula_text}</div>
            <span class="status-badge hc-variance-status"
                  style="color:{status_color};background:{status_bg};">
                {status_text}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )



def shipment_kpi_card(label: str, value: str, note: str = ""):
    """Equal-size centered KPI card for Shipment Volume section."""
    st.markdown(
        f"""
        <div class="shipment-kpi-card">
            <div class="shipment-kpi-label">{label}</div>
            <div class="shipment-kpi-value">{value}</div>
            <div class="shipment-kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def pic_kpi_card(label: str, value: str, note: str = "", unit: str = ""):
    """Compact numeric KPI card: Title -> Unit -> Value -> Note."""
    unit_html = f'<div class="pic-kpi-unit">Unit: {unit}</div>' if unit else ""
    st.markdown(
        f"""
        <div class="pic-kpi-card">
            <div class="pic-kpi-label">{label}</div>
            {unit_html}
            <div class="pic-kpi-value">{value}</div>
            <div class="pic-kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filtered_monthly_metric(
    df: pd.DataFrame,
    value_col: str,
    agg: str = "sum",
) -> float:
    """
    KPI helper:
    - Single month => exact selected-month aggregate.
    - All months => average of monthly aggregates.
    """
    if df is None or df.empty or value_col not in df.columns:
        return float("nan")

    d = df[["MonthDate", value_col]].copy()
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=["MonthDate", value_col])
    if d.empty:
        return float("nan")

    if agg == "sum":
        monthly = d.groupby("MonthDate")[value_col].sum(min_count=1)
    elif agg == "mean":
        monthly = d.groupby("MonthDate")[value_col].mean()
    else:
        raise ValueError("agg must be 'sum' or 'mean'")

    monthly = monthly.dropna()
    if monthly.empty:
        return float("nan")
    return float(monthly.mean())


def hc_capacity_utilization(df: pd.DataFrame) -> float:
    """
    Capacity Utilization KPI source of truth:
    sheet HC -> column "Capacity Utilization (%)".

    Single Office / Month:
        use the source value directly.

    All Offices:
        calculate each month's overall utilization as the Actual-HC-weighted
        average of the office source percentages, then average across selected months.

    Blank future months are excluded.
    """
    if df is None or df.empty or "HC Utilization" not in df.columns:
        return float("nan")

    cols = ["MonthDate", "HC Utilization"]
    if "Total Actual HC" in df.columns:
        cols.append("Total Actual HC")

    d = df[cols].copy()
    d["HC Utilization"] = pd.to_numeric(d["HC Utilization"], errors="coerce")
    if "Total Actual HC" in d.columns:
        d["Total Actual HC"] = pd.to_numeric(d["Total Actual HC"], errors="coerce")

    d = d.dropna(subset=["MonthDate", "HC Utilization"])
    if d.empty:
        return float("nan")

    monthly_values = []

    for _, g in d.groupby("MonthDate"):
        # If only one row/office for the month, this is the exact source value.
        if len(g) == 1:
            monthly_values.append(float(g["HC Utilization"].iloc[0]))
            continue

        # All Offices: weight by Actual HC so larger offices contribute appropriately.
        if "Total Actual HC" in g.columns:
            valid = g["Total Actual HC"].notna() & (g["Total Actual HC"] > 0)
            if valid.any():
                weighted = (
                    g.loc[valid, "HC Utilization"]
                    * g.loc[valid, "Total Actual HC"]
                ).sum() / g.loc[valid, "Total Actual HC"].sum()
                monthly_values.append(float(weighted))
                continue

        # Fallback only if HC weights are unavailable.
        monthly_values.append(float(g["HC Utilization"].mean()))

    monthly_values = [v for v in monthly_values if not pd.isna(v)]
    return float(np.mean(monthly_values)) if monthly_values else float("nan")



def pic_utilization_card(util: float):
    if pd.isna(util):
        value = "N/A"
        pct = 0
        color = COLORS["muted"]
    else:
        value = fmt_pct(util)
        pct = max(0, min(util * 100, 125))
        _, color, _ = status_from_util(util)

    width_pct = min(pct / 125 * 100, 100)
    st.markdown(
        f"""
        <div class="pic-status-card">
            <div class="pic-status-left">
                <div class="pic-status-title">CAPACITY UTILIZATION</div>
                <div class="pic-status-value">{value}</div>
            </div>
            <div class="pic-progress-track">
                <div class="pic-progress-fill"
                     style="width:{width_pct:.1f}%;background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overall_workload_status_card(util: float):
    if pd.isna(util):
        status_text, color, bg = "NO DATA", COLORS["muted"], COLORS["light_blue"]
    else:
        status_text, color, bg = status_from_util(util)

    st.markdown(
        f"""
        <div class="workload-status-panel">
            <div class="pic-status-title">OVERALL WORKLOAD STATUS</div>
            <div class="workload-status-text"
                 style="color:{color};background:{bg};
                        border-radius:999px;padding:8px 14px;">
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def pair_panel_title(text: str):
    """Shared title style for chart/table pairs so both columns align visually."""
    st.markdown(
        f"""
        <div style="
            color:{COLORS['navy']};
            font-family:{UI['font_family']};
            font-size:{UI['chart_title_size']}px;
            line-height:1.25;
            font-weight:700;
            min-height:28px;
            display:flex;
            align-items:center;
            margin:0 0 8px 2px;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_layout(
    fig: go.Figure,
    height: int = UI["chart_height"],
    *,
    show_legend: bool = True,
    legend_position: str = "top",
    margin_left: int = 52,
    margin_right: int = 36,
    margin_top: int = 62,
    margin_bottom: int = 44,
) -> go.Figure:
    """Shared Executive/Corporate Plotly layout — UI only."""
    legend_cfg = dict(
        font=dict(size=UI["axis_size"]),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
    )

    if legend_position == "top":
        legend_cfg.update(
            orientation="h",
            yanchor="bottom",
            y=1.015,
            xanchor="right",
            x=1,
        )
    elif legend_position == "bottom":
        legend_cfg.update(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0,
        )
    else:
        legend_cfg.update(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=COLORS["text"],
            family=UI["font_family"],
            size=UI["axis_size"],
        ),
        # Preserve an existing Plotly title when one is explicitly set.
        # If the chart uses an external pair_panel_title(), keep Plotly title text blank
        # to prevent some Plotly/Streamlit versions from rendering "undefined".
        title=dict(
            text=(fig.layout.title.text or "") if getattr(fig.layout, "title", None) else "",
            font=dict(
                size=UI["chart_title_size"],
                color=COLORS["navy"],
                family=UI["font_family"],
            ),
            x=0.0,
            xanchor="left",
            y=0.985,
            yanchor="top",
            pad=dict(t=0, b=8),
        ),
        margin=dict(
            l=margin_left,
            r=margin_right,
            t=margin_top,
            b=margin_bottom,
        ),
        legend=legend_cfg,
        showlegend=show_legend,
        hoverlabel=dict(
            font=dict(family=UI["font_family"], size=UI["axis_size"]),
            bgcolor="#FFFFFF",
            bordercolor=COLORS["border"],
        ),
        hovermode="closest",
    )

    fig.update_xaxes(
        gridcolor=COLORS["grid"],
        gridwidth=0.7,
        zeroline=False,
        showline=False,
        tickfont=dict(size=UI["axis_size"]),
        title_font=dict(size=UI["axis_size"], color=COLORS["gray_dark"]),
        automargin=True,
        ticks="",
    )
    fig.update_yaxes(
        gridcolor=COLORS["grid"],
        gridwidth=0.7,
        zeroline=False,
        showline=False,
        tickfont=dict(size=UI["axis_size"]),
        title_font=dict(size=UI["axis_size"], color=COLORS["gray_dark"]),
        automargin=True,
        ticks="",
    )
    return fig
