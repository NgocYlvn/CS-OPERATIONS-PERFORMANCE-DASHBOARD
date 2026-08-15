from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import numpy as np
import pandas as pd
import streamlit as st
from .config import *
from .common import *

def load_data(path: str, cache_token: str = "") -> Dict[str, pd.DataFrame]:
    """
    FAST workbook loader:
    - Open Excel workbook only ONCE with pd.ExcelFile.
    - Parse required sheets from the same workbook handle.
    - cache_token invalidates Streamlit cache when file content changes.
    """
    data: Dict[str, pd.DataFrame] = {}

    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
        available_sheets = set(xls.sheet_names)
    except Exception:
        return {key: pd.DataFrame() for key in SHEET_NAMES}

    for key, sheet in SHEET_NAMES.items():
        if sheet not in available_sheets:
            data[key] = pd.DataFrame()
            continue

        try:
            df = pd.read_excel(
                xls,
                sheet_name=sheet,
                header=1,
            )
            df.columns = [clean_col(c) for c in df.columns]
            df = df.dropna(how="all")
            data[key] = df
        except Exception:
            data[key] = pd.DataFrame()

    return data



@st.cache_data(show_spinner=False)
def prepare_hc(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Office", "MonthDate"])
    df = df.copy()
    office_col = first_existing(df, ["Office", "OFFICE"])
    month_col = first_existing(df, ["Month"])
    if not office_col or not month_col:
        return pd.DataFrame(columns=["Office", "MonthDate"])
    df["Office"] = df[office_col].map(normalize_office)
    df["MonthDate"] = df[month_col].map(parse_month)
    mapping = {
        "Approved HC MNG": ["Approved HC – MNG", "Approved HC (MNG)"],
        "Approved HC PIC": ["Approved HC – PIC", "Approved HC (PIC)"],
        "Total Approved HC": ["Total Approved HC"],
        "Actual HC MNG": ["Actual HC – MNG", "Actual HC (MNG)"],
        "Actual HC PIC": ["Actual HC – PIC", "Actual HC (PIC)"],
        "Total Actual HC": ["Total Actual HC", "Total Actual  HC"],
        "Required HC MNG": ["Required HC – MNG", "Required HC (MNG)"],
        "Required HC PIC": ["Required HC – PIC", "Required HC (PIC)"],
        "Total Required HC": ["Total Required HC"],
        "HC Available Hours": [
            "Total Available Standard Time (95%x8x22xPIC)",
            "Total Available Time (95%x8x22x total PIC) (i)",
        ],
        "HC Actual Working Hours": [
            "Total actual Working Time (=C+A+S+E)",
            "Total actual Working Time (=C+A+S+E) (ii)",
        ],
        "HC Actual Workload per PIC": ["Actual workload/PIC (hour)"],
        "HC Utilization": [
            "Capacity Utilization (%)",
            "HC Utilization (%)",
            "Office Workload (%) (ii /i)",
        ],
        "HC Status": [
            "Overal Workload Status",
            "Overal  Workload Status",
            "Overall Workload Status",
            "Office Workload Status",
            "HC Status",
        ],
    }
    for new, candidates in mapping.items():
        col = first_existing(df, candidates)
        if col:
            df[new] = df[col]
    # Fallback calculations
    if "Total Approved HC" not in df.columns:
        df["Total Approved HC"] = numeric_series(df.get("Approved HC MNG", 0)) + numeric_series(df.get("Approved HC PIC", 0))
    if "Total Actual HC" not in df.columns:
        df["Total Actual HC"] = numeric_series(df.get("Actual HC MNG", 0)) + numeric_series(df.get("Actual HC PIC", 0))
    hc_numeric_cols = [
        "Approved HC MNG", "Approved HC PIC", "Total Approved HC",
        "Actual HC MNG", "Actual HC PIC", "Total Actual HC",
        "Required HC MNG", "Required HC PIC", "Total Required HC",
        "HC Available Hours", "HC Actual Working Hours",
        "HC Actual Workload per PIC", "HC Utilization"
    ]
    for col in hc_numeric_cols:
        if col in df.columns:
            # IMPORTANT: keep blank Excel cells as NaN.
            # Do not convert future blank months to 0 because that distorts averages/trends.
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["MonthDate"])

    # Keep only HC rows that actually contain HC data.
    hc_key_cols = [
        c for c in [
            "Total Approved HC", "Total Actual HC", "Total Required HC",
            "Approved HC MNG", "Approved HC PIC",
            "Actual HC MNG", "Actual HC PIC",
            "Required HC MNG", "Required HC PIC"
        ] if c in df.columns
    ]
    if hc_key_cols:
        df = df.dropna(subset=hc_key_cols, how="all")

    return df


@st.cache_data(show_spinner=False)
def prepare_workload(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Office", "MonthDate", "Segment"])

    df = df.copy()
    office_col = first_existing(df, ["Office", "OFFICE"])
    month_col = first_existing(df, ["Month"])
    segment_col = first_existing(df, ["Segment"])

    if not office_col or not month_col or not segment_col:
        return pd.DataFrame(columns=["Office", "MonthDate", "Segment"])

    df["Office"] = df[office_col].map(normalize_office)
    df["MonthDate"] = df[month_col].map(parse_month)
    df["Segment"] = df[segment_col].astype(str).str.strip().str.upper()

    # Canonical dashboard fields remain unchanged.
    # Only source-header aliases are expanded for the renamed MASTER DATA SOURCE workbook.
    component_map = {
        "Core Workload (min)": [
            "Core Workload (min)",
            "C Total Time (min)",
        ],
        "Ancillary Workload (min)": [
            "Ancillary Workload (min)",
            "A Total Time (min)",
        ],
        "Supporting Workload (min)": [
            "Supporting Workload (min)",
            "S Total time (min)",
            "S Total Time (min)",
        ],
        "Exception Workload (min)": [
            "Exception Workload (min)",
            "E Total Time (min)",
        ],
        "Total Workload (min)": [
            "Total Workload (min)",
            "Total time (min)",
        ],
        "Workload Share": [
            "% of Network",
            "CS Allocation (%)",
        ],
        "Office HC Allocation Ratio": [
            "OFFICE HC ALLOCATION RATIO TO Bus",
            "CS Allocation (FTE)",
        ],
        "Core Volume": [
            "Core Volume",
            "C Volume",
        ],
        "Ancillary Volume": [
            "Ancillary Volume",
            "A Volume",
        ],
        "Supporting Volume": [
            "Supporting Volume",
            "S Volume",
        ],
        "Exception Volume": [
            "Exception Volume",
            "E Volume",
        ],
    }

    for canonical, candidates in component_map.items():
        col = first_existing(df, candidates)
        if col:
            df[canonical] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[canonical] = 0.0

    if df["Total Workload (min)"].sum() == 0:
        df["Total Workload (min)"] = (
            df["Core Workload (min)"]
            + df["Ancillary Workload (min)"]
            + df["Supporting Workload (min)"]
            + df["Exception Workload (min)"]
        )

    df["Workload Hours"] = df["Total Workload (min)"] / 60
    df["Core Hours"] = df["Core Workload (min)"] / 60
    df["Ancillary Hours"] = df["Ancillary Workload (min)"] / 60
    df["Supporting Hours"] = df["Supporting Workload (min)"] / 60
    df["Exception Hours"] = df["Exception Workload (min)"] / 60
    df["Service Label"] = df["Segment"].map(SERVICE_LABELS).fillna(df["Segment"])

    return df.dropna(subset=["MonthDate"])


@st.cache_data(show_spinner=False)
def prepare_fte(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize PIC workload while preserving the new source fields from
    sheet "2. FTE Workload".

    Canonical output:
        Office
        CS PIC
        MonthDate
        Available Time
        Actual Working Time
        Actual FTE
        FTE Workload Status

    New MASTER DATA SOURCE:
        Office
        Month
        CS PIC Name
        Total Available Time (95%x8x22x1) (i)
        Total Actual Working Time (=C+A+S+E) (ii)
        FTE Workload (ii /i)
        FTE Workload Status

    Legacy wide-format input remains supported as a fallback.
    """
    base = [
        "Office",
        "CS PIC",
        "MonthDate",
        "Available Time",
        "Actual Working Time",
        "Actual FTE",
        "FTE Workload Status",
    ]

    if df.empty:
        return pd.DataFrame(columns=base)

    df = df.copy()

    office_col = first_existing(df, ["OFFICE", "Office"])
    pic_col = first_existing(df, ["CS PIC", "PIC", "CS PIC Name"])

    if not office_col or not pic_col:
        return pd.DataFrame(columns=base)

    # --------------------------------------------------------
    # New long-format source
    # --------------------------------------------------------
    month_col = first_existing(df, ["Month"])

    available_col = first_existing(
        df,
        [
            "Total Available Time (95%x8x22x1) (i)",
            "Total Available Time",
            "Available Time",
        ],
    )

    actual_time_col = first_existing(
        df,
        [
            "Total Actual Working Time (=C+A+S+E) (ii)",
            "Total Actual Working Time",
            "Actual Working Time",
        ],
    )

    factor_col = first_existing(
        df,
        [
            "FTE Workload (ii /i)",
            "FTE Workload (ii / i)",
            "FTE Workload",
            "FTE Workload",
        ],
    )

    status_col = first_existing(
        df,
        [
            "FTE Workload Status",
            "Workload Status",
        ],
    )

    if month_col and (factor_col or actual_time_col):
        keep_cols = [office_col, month_col, pic_col]
        for c in [available_col, actual_time_col, factor_col, status_col]:
            if c and c not in keep_cols:
                keep_cols.append(c)

        long = df[keep_cols].copy()

        long["Office"] = long[office_col].map(normalize_office)
        long["CS PIC"] = long[pic_col].astype(str).str.strip()
        long["MonthDate"] = long[month_col].map(parse_month)

        # Use source values directly whenever available.
        if available_col:
            long["Available Time"] = pd.to_numeric(
                long[available_col], errors="coerce"
            )
        else:
            long["Available Time"] = CAPACITY_HOURS_PER_FTE

        if actual_time_col:
            long["Actual Working Time"] = pd.to_numeric(
                long[actual_time_col], errors="coerce"
            )
        else:
            long["Actual Working Time"] = np.nan

        if factor_col:
            long["Actual FTE"] = pd.to_numeric(
                long[factor_col], errors="coerce"
            )
        else:
            long["Actual FTE"] = np.nan

        # Fallback only when a source field is missing.
        missing_fte = long["Actual FTE"].isna()
        long.loc[missing_fte, "Actual FTE"] = (
            long.loc[missing_fte, "Actual Working Time"]
            / long.loc[missing_fte, "Available Time"].replace(0, np.nan)
        )

        missing_actual = long["Actual Working Time"].isna()
        long.loc[missing_actual, "Actual Working Time"] = (
            long.loc[missing_actual, "Actual FTE"]
            * long.loc[missing_actual, "Available Time"]
        )

        if status_col:
            long["FTE Workload Status"] = (
                long[status_col].astype(str).str.strip()
            )
        else:
            long["FTE Workload Status"] = long["Actual FTE"].apply(
                lambda x: status_from_util(float(x))[0]
                if pd.notna(x) else "NO DATA"
            )

        long = long[
            (long["Office"] != "")
            & (long["CS PIC"] != "")
            & (~long["MonthDate"].isna())
            & (long["Actual FTE"].notna())
        ]

        return long[base].reset_index(drop=True)

    # --------------------------------------------------------
    # Legacy wide-format source
    # --------------------------------------------------------
    month_cols = [
        c for c in df.columns
        if not pd.isna(parse_month(c))
    ]

    if not month_cols:
        return pd.DataFrame(columns=base)

    long = df.melt(
        id_vars=[office_col, pic_col],
        value_vars=month_cols,
        var_name="Month",
        value_name="Actual FTE",
    )

    long["Office"] = long[office_col].map(normalize_office)
    long["CS PIC"] = long[pic_col].astype(str).str.strip()
    long["MonthDate"] = long["Month"].map(parse_month)
    long["Actual FTE"] = pd.to_numeric(long["Actual FTE"], errors="coerce")

    long["Available Time"] = CAPACITY_HOURS_PER_FTE
    long["Actual Working Time"] = (
        long["Actual FTE"] * long["Available Time"]
    )
    long["FTE Workload Status"] = long["Actual FTE"].apply(
        lambda x: status_from_util(float(x))[0]
        if pd.notna(x) else "NO DATA"
    )

    long = long[
        (long["Office"] != "")
        & (~long["MonthDate"].isna())
        & (long["Actual FTE"].notna())
    ]

    return long[base].reset_index(drop=True)



@st.cache_data(show_spinner=False)
def prepare_shipment(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return (
            pd.DataFrame(columns=["Office", "MonthDate", "Total Shipment", "Active Customers"]),
            pd.DataFrame(columns=["Office", "MonthDate", "Mode", "Volume"]),
        )

    df = df.copy()
    office_col = first_existing(df, ["Office", "OFFICE"])
    month_col = first_existing(df, ["Month"])
    active_col = first_existing(
        df,
        [
            "Active Customers",
            "Total No. of Active Customers",
        ],
    )
    total_col = first_existing(
        df,
        [
            "TOTAL",
            "Total",
            "Total No. of shipment",
            "Total No. of Shipment",
        ],
    )

    if not office_col or not month_col:
        return pd.DataFrame(), pd.DataFrame()

    df["Office"] = df[office_col].map(normalize_office)
    df["MonthDate"] = df[month_col].map(parse_month)

    df["Total Shipment"] = (
        pd.to_numeric(df[total_col], errors="coerce")
        if total_col else np.nan
    )
    df["Active Customers"] = (
        pd.to_numeric(df[active_col], errors="coerce")
        if active_col else np.nan
    )

    df = df.dropna(subset=["MonthDate"])
    df = df.dropna(subset=["Total Shipment", "Active Customers"], how="all")
    df["Total Shipment"] = df["Total Shipment"].fillna(0)
    df["Active Customers"] = df["Active Customers"].fillna(0)

    # Legacy workbook contained mode columns directly.
    # New master summary sheet contains only Active Customers + Total Shipment.
    excluded = {
        office_col, month_col, active_col, total_col,
        "Office", "MonthDate", "Active Customers", "Total Shipment"
    }
    mode_cols = [
        c for c in df.columns
        if c not in excluded and not str(c).startswith("Unnamed")
    ]

    if mode_cols:
        mode_long = df.melt(
            id_vars=["Office", "MonthDate"],
            value_vars=mode_cols,
            var_name="Mode",
            value_name="Volume",
        )
        mode_long["Volume"] = pd.to_numeric(mode_long["Volume"], errors="coerce").fillna(0)
        mode_long = mode_long[mode_long["Volume"] > 0]
    else:
        mode_long = pd.DataFrame(columns=["Office", "MonthDate", "Mode", "Volume"])

    return df, mode_long


@st.cache_data(show_spinner=False)
def prepare_customer(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Prefer office-specific customer sheets when available; otherwise use 11. Vol. by Customer.
    office_sheets = ["customer_had", "customer_han", "customer_hlc", "customer_hcm"]
    frames = []
    for key in office_sheets:
        df = data.get(key, pd.DataFrame())
        if df.empty:
            continue
        frames.append(customer_wide_to_long(df))
    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if combined.empty:
        combined = customer_wide_to_long(data.get("customer_ns", pd.DataFrame()))
    return combined


@st.cache_data(show_spinner=False)
def customer_wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Office", "Customer", "MonthDate", "Volume"])
    df = df.copy()
    office_col = first_existing(df, ["Office", "OFFICE"])
    cust_col = first_existing(df, ["Customer", "CUSTOMER", "Customer Name"])
    if not office_col or not cust_col:
        return pd.DataFrame(columns=["Office", "Customer", "MonthDate", "Volume"])
    month_cols = [c for c in df.columns if parse_month(c) is not pd.NaT and not pd.isna(parse_month(c))]
    if not month_cols:
        return pd.DataFrame(columns=["Office", "Customer", "MonthDate", "Volume"])
    long = df.melt(id_vars=[office_col, cust_col], value_vars=month_cols, var_name="Month", value_name="Volume")
    long["Office"] = long[office_col].map(normalize_office)
    long["Customer"] = long[cust_col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    long["MonthDate"] = long["Month"].map(parse_month)
    long["Volume"] = numeric_series(long["Volume"])
    long = long[(long["Volume"] > 0) & (long["Customer"] != "") & (~long["MonthDate"].isna())]
    return long[["Office", "Customer", "MonthDate", "Volume"]]


@st.cache_data(show_spinner=False)
def prepare_case_detail(
    df: pd.DataFrame,
    activity_type: str,
) -> pd.DataFrame:
    """
    Normalize detail sheets C / A / S / E into long format.

    C/A/S expected pattern:
        Office | Scope/Code | Apr-26 ... Mar-27 | Total

    E expected pattern:
        Office | Code | BU | Criteria | Exception Detail | Apr-26 ... Mar-27 | Total

    The parser is intentionally tolerant to header wording so the dashboard
    remains usable when the source template adds descriptive columns.
    """
    base_cols = [
        "Activity Type", "Office", "Code", "BU", "Criteria",
        "Detail", "MonthDate", "Volume"
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=base_cols)

    d = df.copy()
    d.columns = [clean_col(c) for c in d.columns]

    office_col = first_existing(d, ["Office", "OFFICE"])
    if not office_col:
        return pd.DataFrame(columns=base_cols)

    # Identify month columns strictly by parseable month headers.
    month_cols = []
    for c in d.columns:
        parsed = parse_month(c)
        if not pd.isna(parsed):
            month_cols.append(c)

    if not month_cols:
        return pd.DataFrame(columns=base_cols)

    # Descriptive columns before month columns.
    code_col = first_existing(d, ["Scope", "CODE", "Code", "Service Code"])
    bu_col = first_existing(d, ["BU", "Segment", "Service"])
    criteria_col = first_existing(d, ["Criteria"])
    detail_col = first_existing(
        d,
        [
            "Scope details",       # Sheet A
            "Job details",         # Sheet S
            "EXCEPTION DETAIL",    # Sheet E
            "Exception Detail",
            "Detail",
            "Description",
            "Activity",
        ],
    )

    id_cols = [office_col]
    for c in [code_col, bu_col, criteria_col, detail_col]:
        if c and c not in id_cols:
            id_cols.append(c)

    long = d.melt(
        id_vars=id_cols,
        value_vars=month_cols,
        var_name="Month",
        value_name="Volume",
    )

    long["Office"] = long[office_col].map(normalize_office)
    long["MonthDate"] = long["Month"].map(parse_month)
    long["Volume"] = pd.to_numeric(long["Volume"], errors="coerce")

    long["Code"] = (
        long[code_col].astype(str).str.strip()
        if code_col else ""
    )
    long["BU"] = (
        long[bu_col].astype(str).str.strip().str.upper()
        if bu_col else ""
    )
    long["Criteria"] = (
        long[criteria_col].astype(str).str.strip()
        if criteria_col else ""
    )
    long["Detail"] = (
        long[detail_col].astype(str).str.strip()
        if detail_col else ""
    )
    long["Activity Type"] = activity_type

    # Keep only rows that contain real activity data.
    # Blank cells and 0-volume months are excluded so detail tabs show only months
    # that actually have C/A/S/E data in the corresponding source sheet.
    long = long[
        (long["Office"] != "")
        & (~long["MonthDate"].isna())
        & (long["Volume"].notna())
        & (long["Volume"] > 0)
    ].copy()

    return long[base_cols].reset_index(drop=True)



@st.cache_data(show_spinner=False)
def prepare_code_note_map(df: pd.DataFrame) -> Dict[str, str]:
    """
    Sheet 'Ghi chú':
        Col A = Scope of Job code
        Col B = description.

    Used mainly for Core Service codes such as AE-CTAB:
        suffix CTAB -> "Customs + Trucking + Air"

    A/S/E sheets already contain their own descriptive columns
    (Scope details / Job details / EXCEPTION DETAIL), which take priority.
    """
    if df is None or df.empty or df.shape[1] < 2:
        return {}

    d = df.copy()
    code_col = d.columns[0]
    desc_col = d.columns[1]

    d[code_col] = d[code_col].astype(str).str.strip().str.upper()
    d[desc_col] = d[desc_col].astype(str).str.strip()

    # Remove title/header/blank rows.
    d = d[
        d[code_col].ne("")
        & d[desc_col].ne("")
        & d[code_col].ne("SCOPE OF JOB")
        & d[code_col].ne("NAN")
        & d[desc_col].ne("nan")
    ].copy()

    return dict(zip(d[code_col], d[desc_col]))


def add_code_description(
    df: pd.DataFrame,
    activity_type: str,
    note_map: Dict[str, str],
) -> pd.DataFrame:
    """
    Create the dashboard field 'Code Description'.

    Priority:
    1) A/S/E: source description already available in the corresponding sheet.
    2) C: lookup suffix of Scope code against sheet 'Ghi chú'
       e.g. AE-ABBB -> ABBB -> Air Freight Only.
    3) Fallback: lookup whole code in 'Ghi chú'.
    """
    if df is None or df.empty:
        return df

    d = df.copy()
    d["Code"] = d["Code"].fillna("").astype(str).str.strip()
    d["Detail"] = d["Detail"].fillna("").astype(str).str.strip()

    def _decode(row):
        code = str(row.get("Code", "")).strip().upper()
        source_detail = str(row.get("Detail", "")).strip()

        # Ancillary / Supporting / Exception: use source wording first.
        if activity_type != "Core Service" and source_detail:
            return source_detail

        # Core: AE-CTAB -> CTAB
        suffix = code.split("-", 1)[1] if "-" in code else code
        if suffix in note_map:
            return note_map[suffix]

        if code in note_map:
            return note_map[code]

        # Defensive fallback if a source detail exists.
        return source_detail

    d["Code Description"] = d.apply(_decode, axis=1)
    return d


def prepare_resolution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sheet 'CS Resolutions Rate'
    Source structure:
        OFFICE | Month | Total abnormality/month |
        No of abnormality resolved by CS | CS Resolution rate

    Dashboard rules:
    - Only months with actual source data are retained.
    - Resolution Rate is recalculated from Resolved / Total Abnormality
      so the dashboard does not depend on Excel formula cache.
    """
    cols = [
        "Office", "MonthDate",
        "Total Abnormality", "Resolved", "Resolution Rate",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=cols)

    d = df.copy()
    office_col = first_existing(d, ["OFFICE", "Office"])
    month_col = first_existing(d, ["Month"])
    total_col = first_existing(
        d, ["Total abnormality/month", "Total abnormality", "Total Exception Case"]
    )
    resolved_col = first_existing(
        d, ["No of abnormality resolved by CS", "Resolved", "No of Exception Case Resolved by CS"]
    )

    if not office_col or not month_col or not total_col or not resolved_col:
        return pd.DataFrame(columns=cols)

    d["Office"] = d[office_col].map(normalize_office)
    d["MonthDate"] = d[month_col].map(parse_month)

    # Preserve blanks first; do not convert future empty months to zero.
    d["Total Abnormality"] = pd.to_numeric(d[total_col], errors="coerce")
    d["Resolved"] = pd.to_numeric(d[resolved_col], errors="coerce")

    # Keep only rows/months where the source contains actual activity data.
    d = d[
        (d["Office"] != "")
        & (~d["MonthDate"].isna())
        & (
            d["Total Abnormality"].notna()
            | d["Resolved"].notna()
        )
    ].copy()

    if d.empty:
        return pd.DataFrame(columns=cols)

    d["Total Abnormality"] = d["Total Abnormality"].fillna(0)
    d["Resolved"] = d["Resolved"].fillna(0)

    d["Resolution Rate"] = np.where(
        d["Total Abnormality"] > 0,
        d["Resolved"] / d["Total Abnormality"],
        np.nan,
    )

    return d[cols].reset_index(drop=True)


@st.cache_data(show_spinner=False)
def prepare_yvf(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sheet 'YVF' — source structure:
        OFFICE | [Month, if available] |
        Total YVF booking/month | Total IFF shipment/month | YVF booking ratio

    Rules:
    - Preserve the source structure; do not invent months.
    - If a Month column exists, parse it and allow Month/Year filtering.
    - Rows where both YVF Booking and IFF Shipment are blank are excluded,
      so future empty periods never appear on the dashboard.
    - Recalculate YVF Booking Ratio = YVF Booking / IFF Shipment to avoid
      stale Excel formula-cache values.
    """
    base_cols = [
        "Office", "MonthDate",
        "YVF Booking", "IFF Shipment", "YVF Booking Ratio",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=base_cols)

    d = df.copy()

    office_col = first_existing(d, ["OFFICE", "Office"])
    month_col = first_existing(d, ["Month"])
    yvf_col = first_existing(
        d, ["Total YVF booking/month", "Total YVF booking"]
    )
    iff_col = first_existing(
        d, ["Total IFF shipment/month", "Total IFF shipment", "Total IFF Booking"]
    )

    if not office_col or not yvf_col or not iff_col:
        return pd.DataFrame(columns=base_cols)

    d["Office"] = d[office_col].map(normalize_office)
    d["MonthDate"] = (
        d[month_col].map(parse_month)
        if month_col else pd.NaT
    )

    # Preserve blanks first so empty/future periods are not converted to zeros.
    d["YVF Booking"] = pd.to_numeric(d[yvf_col], errors="coerce")
    d["IFF Shipment"] = pd.to_numeric(d[iff_col], errors="coerce")

    d = d[
        (d["Office"] != "")
        & (
            d["YVF Booking"].notna()
            | d["IFF Shipment"].notna()
        )
    ].copy()

    if d.empty:
        return pd.DataFrame(columns=base_cols)

    d["YVF Booking"] = d["YVF Booking"].fillna(0)
    d["IFF Shipment"] = d["IFF Shipment"].fillna(0)

    d["YVF Booking Ratio"] = np.where(
        d["IFF Shipment"] > 0,
        d["YVF Booking"] / d["IFF Shipment"],
        np.nan,
    )

    return d[base_cols].reset_index(drop=True)



def all_periods(*dfs: pd.DataFrame) -> List[pd.Timestamp]:
    periods = []
    for df in dfs:
        if df is not None and not df.empty and "MonthDate" in df.columns:
            periods.extend(df["MonthDate"].dropna().unique().tolist())
    return sorted(pd.to_datetime(pd.Series(periods)).dropna().drop_duplicates().tolist())


def apply_filters(df: pd.DataFrame, year: str, month: str, office: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    if "MonthDate" in out.columns:
        if year != "All":
            out = out[out["MonthDate"].dt.year.astype(str) == year]
        if month != "All":
            target = parse_month(month)
            out = out[out["MonthDate"] == target]
    if office != "All Offices" and "Office" in out.columns:
        out = out[out["Office"] == office]
    return out


def filter_office_only(df: pd.DataFrame, office: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    if office != "All Offices" and "Office" in out.columns:
        out = out[out["Office"] == office]
    return out
