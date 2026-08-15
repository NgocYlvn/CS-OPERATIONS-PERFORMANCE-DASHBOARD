from __future__ import annotations

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from .config import *
from .common import *
from .data import *
from .activity import *
from .metrics import *
from .charts import *
from .cover import *

def main():
    # Cover page is displayed before any Excel loading/filtering.
    render_cover_gate()

    # Load default workbook first. Upload remains below Month / Office filters.
    file_path = Path(DEFAULT_FILE)
    cache_token = ""

    # If an uploaded workbook was already saved in this session, reuse the saved file.
    uploaded_path_cached = st.session_state.get("dashboard_uploaded_path")
    uploaded_sig_cached = st.session_state.get("dashboard_uploaded_sig")

    if uploaded_path_cached and Path(uploaded_path_cached).exists():
        file_path = Path(uploaded_path_cached)
        cache_token = uploaded_sig_cached or ""
    elif file_path.exists():
        stat = file_path.stat()
        cache_token = f"{stat.st_mtime_ns}_{stat.st_size}"

    if not file_path.exists():
        st.error(
            f"Không tìm thấy file dữ liệu: {file_path}. "
            "Vui lòng đặt file Excel cùng thư mục app.py hoặc upload file ở Sidebar."
        )
        st.stop()

    with st.spinner("Loading and validating Excel data..."):
        raw = load_data(str(file_path), cache_token)
        hc = prepare_hc(raw["hc"])
        workload = prepare_workload(raw["workload"])
        fte = prepare_fte(raw["fte"])
        shipment, shipment_mode = prepare_shipment(raw["shipment"])

        # New MASTER DATA SOURCE stores shipment-by-segment volume in
        # "4. Workload by Activity" (C Volume), while the old workbook stored
        # transportation-mode columns inside "Shipment volume".
        # Build the same canonical Mode/Volume table only when direct mode data is absent.
        if shipment_mode.empty and not workload.empty and "Core Volume" in workload.columns:
            _mode = workload[["Office", "MonthDate", "Segment", "Core Volume"]].copy()
            _mode["Volume"] = pd.to_numeric(_mode["Core Volume"], errors="coerce").fillna(0)
            _mode = _mode[_mode["Volume"] > 0]
            shipment_mode = _mode.rename(columns={"Segment": "Mode"})[
                ["Office", "MonthDate", "Mode", "Volume"]
            ].reset_index(drop=True)

        customer = prepare_customer(raw)
        # Section 2 customer ranking/detail uses the mapped customer-volume source: 11. Vol. by Customer.
        customer_ns = customer_wide_to_long(raw["customer_ns"])
        resolution = prepare_resolution(raw["resolution"])
        yvf = prepare_yvf(raw["yvf"])

        # Section 5 detail sources (C / A / S / E)
        core_detail = prepare_case_detail(raw["core"], "Core Service")
        ancillary_detail = prepare_case_detail(raw["ancillary"], "Ancillary Service")
        supporting_detail = prepare_case_detail(raw["supporting"], "Supporting Activity")
        exception_detail = prepare_case_detail(raw["exception"], "Exception Handling")

        # Code description lookup from sheet "Ghi chú".
        code_note_map = prepare_code_note_map(raw["notes"])

        # Add one consistent "Code Description" field to all C/A/S/E sources.
        core_detail = add_code_description(core_detail, "Core Service", code_note_map)
        ancillary_detail = add_code_description(ancillary_detail, "Ancillary Service", code_note_map)
        supporting_detail = add_code_description(supporting_detail, "Supporting Activity", code_note_map)
        exception_detail = add_code_description(exception_detail, "Exception Handling", code_note_map)

    periods = all_periods(hc, workload, fte, shipment, customer, customer_ns, resolution)
    month_options = ["All"] + [format_month(p) for p in periods]

    offices_from_data = sorted(set(
        list(hc.get("Office", pd.Series(dtype=str)).dropna().unique())
        + list(workload.get("Office", pd.Series(dtype=str)).dropna().unique())
        + list(fte.get("Office", pd.Series(dtype=str)).dropna().unique())
        + list(shipment.get("Office", pd.Series(dtype=str)).dropna().unique())
        + list(customer.get("Office", pd.Series(dtype=str)).dropna().unique())
        + list(customer_ns.get("Office", pd.Series(dtype=str)).dropna().unique())
    ))
    office_options = ["All Offices"] + sorted(set(STANDARD_OFFICES + [o for o in offices_from_data if o]))

    # Sidebar order: Month -> Office -> Upload file. No Year and no Reset button.
    # UI only: styled to match the approved Yusen executive HOME format.
    with st.sidebar:
        if st.button("HOME", icon=":material/home:", use_container_width=True, key="back_to_cover_btn"):
            st.session_state["dashboard_entered"] = False
            st.rerun()
        st.markdown('<div class="sidebar-filter-title">FILTERS</div><div class="sidebar-filter-spacer"></div>', unsafe_allow_html=True)
        month = st.selectbox("MONTH", month_options, key="month_filter")
        office = st.selectbox("OFFICE", office_options, key="office_filter")
        st.markdown('<div class="sidebar-bottom-anchor"></div>', unsafe_allow_html=True)
        st.markdown("---")
        uploaded = st.file_uploader(
            "UPLOAD EXCEL FILE",
            type=["xlsx", "xlsm", "xls"],
            help="Nếu không upload, Dashboard sẽ đọc file mặc định trong cùng thư mục app.py.",
            key="excel_uploader",
        )
        if uploaded is not None:
            new_bytes = uploaded.getvalue()
            new_sig = hashlib.md5(new_bytes).hexdigest()

            if st.session_state.get("dashboard_uploaded_sig") != new_sig:
                tmp_path = Path("_uploaded_dashboard_data.xlsx")
                tmp_path.write_bytes(new_bytes)

                st.session_state["dashboard_uploaded_sig"] = new_sig
                st.session_state["dashboard_uploaded_path"] = str(tmp_path)
                st.rerun()

        st.markdown(
            """
            <div class="sidebar-footer">
                <span>Version 1.0</span>
                <span class="footer-sep">|</span>
                <span>© 2026 CS Division</span>
                <span class="footer-sep">|</span>
                <span>🔒 Internal Use Only</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Year is intentionally not exposed as a filter.
    year = "All"

    # Apply filters
    f_hc = apply_filters(hc, year, month, office)
    f_workload = apply_filters(workload, year, month, office)
    f_fte = apply_filters(fte, year, month, office)
    f_shipment = apply_filters(shipment, year, month, office)
    f_mode = apply_filters(shipment_mode, year, month, office)
    f_customer = apply_filters(customer, year, month, office)
    f_customer_ns = apply_filters(customer_ns, year, month, office)
    f_resolution = apply_filters(resolution, year, month, office)
    # YVF follows Month/Year filters only when the source sheet contains Month.
    # Current office-only source remains valid without inventing a time dimension.
    if (
        yvf is not None
        and not yvf.empty
        and "MonthDate" in yvf.columns
        and yvf["MonthDate"].notna().any()
    ):
        f_yvf = apply_filters(yvf, year, month, office)
    else:
        f_yvf = filter_office_only(yvf, office)

    f_core_detail = apply_filters(core_detail, year, month, office)
    f_ancillary_detail = apply_filters(ancillary_detail, year, month, office)
    f_supporting_detail = apply_filters(supporting_detail, year, month, office)
    f_exception_detail = apply_filters(exception_detail, year, month, office)

    st.markdown(
        f"""
        <div class="main-header">
            <div class="main-title">{APP_TITLE}</div>
            <div class="subtitle">{APP_SUBTITLE}</div>
            <div class="filter-summary-card">
                <div class="filter-summary-item">
                    <div class="filter-summary-icon">
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                            <rect x="3" y="5" width="18" height="16" rx="2"></rect>
                            <path d="M8 3v4M16 3v4M3 10h18"></path>
                        </svg>
                    </div>
                    <div class="filter-summary-label">Selected Month</div>
                    <div class="filter-summary-value">{month}</div>
                </div>
                <div class="filter-summary-item">
                    <div class="filter-summary-icon">
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M4 21V7l8-4 8 4v14"></path>
                            <path d="M8 21v-6h8v6M8 9h2M14 9h2M8 12h2M14 12h2"></path>
                        </svg>
                    </div>
                    <div class="filter-summary-label">Selected Office</div>
                    <div class="filter-summary-value">{office}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if workload.empty or fte.empty:
        st.markdown(
            """
            <div class="warning-box">
            WARNING: Một số dữ liệu workload hoặc CS FTE có thể chưa đầy đủ. Dashboard vẫn chạy dynamic và sẽ tự cập nhật khi bổ sung dữ liệu vào file nguồn.
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("1. Workload & Capacity Utilization")

    # Section 1 uses the HC sheet as the single source of truth.
    approved_hc = weighted_period_avg(f_hc, "Total Approved HC") if not f_hc.empty else 0.0
    approved_mng = weighted_period_avg(f_hc, "Approved HC MNG") if not f_hc.empty else 0.0
    approved_pic = weighted_period_avg(f_hc, "Approved HC PIC") if not f_hc.empty else 0.0

    actual_hc = weighted_period_avg(f_hc, "Total Actual HC") if not f_hc.empty else 0.0
    actual_mng = weighted_period_avg(f_hc, "Actual HC MNG") if not f_hc.empty else 0.0
    actual_pic = weighted_period_avg(f_hc, "Actual HC PIC") if not f_hc.empty else 0.0

    required_hc = weighted_period_avg(f_hc, "Total Required HC") if not f_hc.empty else 0.0
    required_mng = weighted_period_avg(f_hc, "Required HC MNG") if not f_hc.empty else 0.0
    required_pic = weighted_period_avg(f_hc, "Required HC PIC") if not f_hc.empty else 0.0

    hc_variance = required_hc - actual_hc
    
    if hc_variance > 0:
        variance_status = ("OVERLOAD", COLORS["red"], "#FEE2E2")
    elif hc_variance < 0:
        variance_status = ("REDUNDANT", COLORS["green"], "#DCFCE7")
    else:
        variance_status = ("BALANCED", COLORS["blue"], "#E0F2FE")

    hc1, hc2, hc3, hc4 = st.columns(4, gap="medium")

    with hc1:
        hc_detail_card(
            "Approved HC",
            approved_hc,
            approved_mng,
            approved_pic,
        )

    with hc2:
        hc_detail_card(
            "Actual HC",
            actual_hc,
            actual_mng,
            actual_pic,
        )

    with hc3:
        hc_detail_card(
            "Required HC",
            required_hc,
            required_mng,
            required_pic,
        )

    with hc4:
        hc_variance_card(
            "HC Gap",
            hc_variance,
            "Required HC − Actual HC",
            variance_status[0],
            variance_status[1],
            variance_status[2],
        )

    if office == "All Offices":
        render_hc_office_comparison(f_hc)

    # KPI cards follow Month + Office filters.
    # The line chart keeps all available months so management can see the HC trend.
    hc_trend_data = filter_office_only(hc, office)
    st.markdown('<div class="chart-box" style="margin-top:12px;">', unsafe_allow_html=True)
    chart_office_capacity_trend(hc_trend_data)

    section_title("2. Shipment Volume")

    # Source for both KPIs: Shipment volume sheet
    shipment_total = (
        float(f_shipment["Total Shipment"].sum())
        if not f_shipment.empty and "Total Shipment" in f_shipment.columns
        else 0.0
    )
    active_customers = calculate_active_customers(f_shipment)

    # KPI order requested:
    # 1) Active Customers
    # 2) Total Shipment Volume
    # Keep 2 empty columns so KPI widths remain consistent with Section 1.
    sk1, sk2, sk3, sk4 = st.columns(4, gap="medium")
    with sk1:
        shipment_kpi_card(
            "ACTIVE CUSTOMERS",
            fmt_int(active_customers),
            "",
        )
    with sk2:
        shipment_kpi_card(
            "TOTAL SHIPMENT VOLUME",
            fmt_int(shipment_total),
            "",
        )
    with sk3:
        st.empty()
    with sk4:
        st.empty()

    # Customer shipment analysis:
    # Remove Transportation Mode chart/detail from the dashboard.
    # Show Top 15 Customers chart and Customer Volume Detail on the same row.
    customer_chart_col, customer_detail_col = st.columns([0.58, 0.42], gap="medium")

    with customer_chart_col:
        chart_top_customers(f_customer_ns)

    with customer_detail_col:
        customer_detail_volume_table(f_customer_ns)


    section_title("3. Workload per FTE")

    # KPI source: sheet "2. FTE Workload".
    # Single source of truth for Section 3:
    #   (i)  Total Available Time
    #   (ii) Total Actual Working Time
    #        FTE Workload = ii / i
    #        FTE Workload Status
    #
    # Month = All:
    #   Calculate monthly office/PIC totals first, then show the average
    #   monthly Total Available Time and Total Actual Working Time.
    # Selected month:
    #   Show the actual total of that selected month.

    if f_fte is not None and not f_fte.empty:
        fte_kpi = f_fte.copy()

        fte_kpi["Available Time"] = pd.to_numeric(
            fte_kpi["Available Time"], errors="coerce"
        )
        fte_kpi["Actual Working Time"] = pd.to_numeric(
            fte_kpi["Actual Working Time"], errors="coerce"
        )

        monthly_fte = (
            fte_kpi.dropna(
                subset=["MonthDate", "Available Time", "Actual Working Time"]
            )
            .groupby("MonthDate", as_index=False)
            .agg(
                Total_Available_Time=("Available Time", "sum"),
                Total_Actual_Working_Time=("Actual Working Time", "sum"),
            )
        )

        if not monthly_fte.empty:
            if str(month).strip().lower() == "all":
                total_available = float(
                    monthly_fte["Total_Available_Time"].mean()
                )
                total_actual_working = float(
                    monthly_fte["Total_Actual_Working_Time"].mean()
                )
            else:
                selected_month_row = monthly_fte.sort_values(
                    "MonthDate"
                ).iloc[-1]
                total_available = float(
                    selected_month_row["Total_Available_Time"]
                )
                total_actual_working = float(
                    selected_month_row["Total_Actual_Working_Time"]
                )

            fte_workload = safe_div(
                total_actual_working,
                total_available,
            )
            fte_status = status_from_util(fte_workload)
        else:
            total_available = float("nan")
            total_actual_working = float("nan")
            fte_workload = float("nan")
            fte_status = ("NO DATA", COLORS["muted"], COLORS["light_blue"])
    else:
        total_available = float("nan")
        total_actual_working = float("nan")
        fte_workload = float("nan")
        fte_status = ("NO DATA", COLORS["muted"], COLORS["light_blue"])

    # Four management KPIs in one row.
    p1, p2, p3, p4 = st.columns(4, gap="medium")

    def section3_kpi_card(label: str, value: str, note: str = ""):
        note_html = (
            f'<div class="pic-kpi-note">{note}</div>'
            if note else ""
        )
        st.markdown(
            f"""
            <div class="pic-kpi-card">
                <div class="pic-kpi-label">{label}</div>
                <div class="pic-kpi-value">{value}</div>
                {note_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p1:
        section3_kpi_card(
            "Total Available Time",
            fmt_num(total_available, 1)
            if not pd.isna(total_available) else "N/A",
            "95% × 8 × 22 × PIC (hour)",
        )

    with p2:
        section3_kpi_card(
            "Total Actual Working Time",
            fmt_num(total_actual_working, 1)
            if not pd.isna(total_actual_working) else "N/A",
            "C + A + S + E (hour)",
        )

    with p3:
        fte_value = (
            f"{fte_workload * 100:,.1f}%"
            if not pd.isna(fte_workload) else "N/A"
        )
        st.markdown(
            f"""
            <div class="pic-kpi-card">
                <div class="pic-kpi-label">FTE Workload</div>
                <div class="pic-kpi-value" style="
                    font-size:38px !important;
                    font-weight:800 !important;
                    line-height:1.05 !important;
                ">
                    {fte_value}
                </div>
                <div class="pic-kpi-note">Actual Time vs Available Time</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p4:
        status_text, status_color, status_bg = fte_status
        st.markdown(
            f"""
            <div class="pic-kpi-card">
                <div class="pic-kpi-label">FTE Workload Status</div>
                <div style="
                    margin-top:0;
                    min-height:52px;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                ">
            <span class="status-badge"
                style="
                    color:{status_color};
                    background:{status_bg};
                    font-size:30px !important;
                    line-height:1.05 !important;
                    font-weight:800 !important;
                    padding:10px 32px !important;
                    min-width:220px;
                    min-height:44px;
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                    border-radius:999px;
                ">
                {status_text}
            </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if office == "All Offices":
        render_fte_office_comparison(f_fte, month)

    # Chart source: 2. FTE Workload
    # PIC Workload = FTE Workload factor × Available Time / PIC.
    # Available Standard Time / PIC = 95% × 8 × 22 = 167.2 hours.
    # Therefore: PIC Workload = CS FTE coefficient × 167.2 hours.
    # When All Offices is selected, only overloaded PICs/offices are displayed.
    st.markdown('<div class="chart-box" style="margin-top:8px;">', unsafe_allow_html=True)
    chart_workload_by_pic(f_fte, office)

    section_title("4. Workload Distribution by Segment")

    segment_summary = build_segment_workload(f_workload, f_mode)
    segment_total_hours = (
        float(segment_summary["Allocation Time (h)"].sum())
        if not segment_summary.empty
        else 0.0
    )

    # Executive one-row layout:
    # Left = compact Segment Summary panel
    # Right = Workload by Segment chart
    # Detail table remains full width below.
    if not segment_summary.empty:
        _seg_rank = segment_summary.sort_values(
            "Workload Share", ascending=False
        ).reset_index(drop=True)
        top_segment = str(_seg_rank.iloc[0]["Segment"])
        top_share = float(_seg_rank.iloc[0]["Workload Share"])
    else:
        top_segment = "N/A"
        top_share = 0.0

    seg_summary_col, seg_chart_col = st.columns([0.32, 0.68], gap="medium")

    with seg_summary_col:
        summary_html = f"""
<div style="height:340px;min-height:340px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;background:#FFFFFF;border:1px solid #D8E1EA;border-radius:12px;box-shadow:0 1px 4px rgba(16,24,40,0.045);padding:24px 26px;">
    <div style="color:#667085;font-size:12px;line-height:1.25;font-weight:600;letter-spacing:0.025em;text-transform:uppercase;">Total Workload Hours</div>
  <div style="color:#003B70;font-size:34px;line-height:1.05;font-weight:700;letter-spacing:-0.02em;margin-top:8px;">{fmt_num(segment_total_hours, 1)}</div>
  <div style="color:#667085;font-size:11px;margin-top:6px;"></div>
  <div style="height:1px;background:#E6ECF2;margin:24px 0 18px 0;"></div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
    <span style="color:#667085;font-size:12px;">Leading</span>
    <span style="color:#003B70;font-size:14px;font-weight:700;">{top_segment}</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="color:#667085;font-size:12px;"> Workload Share</span>
    <span style="color:#003B70;font-size:14px;font-weight:700;">{top_share:.1%}</span>
  </div>
  </div>
"""
        st.markdown(summary_html.strip(), unsafe_allow_html=True)

    with seg_chart_col:
        chart_service_matrix(f_workload, f_mode)

    # Full-width detail table below the executive row.
    segment_workload_table(f_workload, f_mode)

    
    section_title("5. Workload Breakdown by Activity & Segment")

    st.markdown(
        """
        <div style="
            color:#667085;
            font-size:12px;
            line-height:1.5;
            margin:0 0 10px 2px;">
            Workload composition: Core Service (C), Ancillary Service (A),
            Supporting Activity (S) and Exception Handling (E).
        </div>
        """,
        unsafe_allow_html=True,
    )

    # C/A/S/E summary cards by Office — same executive idea as the HC office cards.
    render_case_office_cards(
        f_core_detail,
        f_ancillary_detail,
        f_supporting_detail,
        f_exception_detail,
    )

    # Summary table + C/A/S/E allocation chart
    wb_chart, wb_table = st.columns([0.43, 0.57], gap="medium")
    with wb_chart:
        chart_case_allocation(f_workload)
    with wb_table:
        render_workload_breakdown_table(f_workload)

    # Four source-detail tables
    st.markdown(
        f"""
        <div style="
            color:{COLORS['navy']};
            font-size:{UI['chart_title_size']}px;
            font-weight:700;
            margin:14px 0 8px 2px;">
            C / A / S / E Details
        </div>
        """,
        unsafe_allow_html=True,
    )

    casetab_c, casetab_a, casetab_s, casetab_e = st.tabs([
        "C · Core Service",
        "A · Ancillary Service",
        "S · Supporting Activity",
        "E · Exception Handling",
    ])
    with casetab_c:
        render_activity_detail_table(f_core_detail, "Core Service")
    with casetab_a:
        render_activity_detail_table(f_ancillary_detail, "Ancillary Service")
    with casetab_s:
        render_activity_detail_table(f_supporting_detail, "Supporting Activity")
    with casetab_e:
        render_activity_detail_table(f_exception_detail, "Exception Handling")

    section_title("6. CS Resolution Rate")

    # Executive KPIs sourced from sheet "CS Resolutions Rate".
    if not f_resolution.empty:
        total_abn = float(f_resolution["Total Abnormality"].sum())
        resolved = float(f_resolution["Resolved"].sum())
        rate = safe_div(resolved, total_abn)

        cs1, cs2, cs3 = st.columns(3, gap="medium")
        with cs1:
            kpi_card(
                "Total Exception Case",
                fmt_int(total_abn),
                "",
            )
        with cs2:
            kpi_card(
                "Resolved by CS",
                fmt_int(resolved),
                "",
            )
        with cs3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">CS Resolution Rate</div>
                    <div class="kpi-value" style="
                        font-size:38px !important;
                        font-weight:800 !important;
                        line-height:1.05 !important;
                    ">
                        {fmt_pct(rate)}
                    </div>
                    <div class="kpi-note">
                        {fmt_int(resolved)} / {fmt_int(total_abn)} cases
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    cs_chart, cs_table = st.columns([0.55, 0.45], gap="medium")
    with cs_chart:
        chart_resolution(f_resolution)
    with cs_table:
        render_cs_solution_table(f_resolution)

    section_title("7. YVF Promotion Effectiveness")

    # Show only one common message when no YVF data is available.
    # Chart and detail table are rendered only when filtered YVF data exists.
    if f_yvf.empty:
        st.info("No YVF data available for selected filters.")
    else:
        yvf_booking = float(f_yvf["YVF Booking"].sum())
        iff = float(f_yvf["IFF Shipment"].sum())
        yvf_rate = safe_div(yvf_booking, iff)

        y1, y2, y3 = st.columns(3, gap="medium")
        with y1:
            kpi_card(
                "Total YVF Bookings",
                fmt_int(yvf_booking),
                "",
            )
        with y2:
            kpi_card(
                "Total IFF Bookings",
                fmt_int(iff),
                "",
            )
        with y3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">YVF Booking Ratio</div>
                    <div class="kpi-value" style="
                        font-size:38px !important;
                        font-weight:800 !important;
                        line-height:1.05 !important;
                    ">
                        {fmt_pct(yvf_rate)}
                    </div>
                    <div class="kpi-note">
                        {fmt_int(yvf_booking)} / {fmt_int(iff)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        yvf_chart_col, yvf_table_col = st.columns([0.52, 0.48], gap="medium")
        with yvf_chart_col:
            chart_yvf(f_yvf)
        with yvf_table_col:
            render_yvf_table(f_yvf)
