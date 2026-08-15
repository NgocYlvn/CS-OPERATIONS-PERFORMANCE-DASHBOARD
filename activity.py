from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from .config import *
from .common import *

def workload_breakdown_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Section 5 summary:
    Segment | Core Service (min) | Ancillary Service (min) |
    Supporting Activity (min) | Exception Handling (min) |
    Total Workload (min) | Ratio
    """
    cols = [
        "Segment",
        "Core Service (min)",
        "Ancillary Service (min)",
        "Supporting Activity (min)",
        "Exception Handling (min)",
        "Total Workload (min)",
        "Ratio",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=cols)

    d = df.copy()
    for c in [
        "Core Workload (min)",
        "Ancillary Workload (min)",
        "Supporting Workload (min)",
        "Exception Workload (min)",
        "Total Workload (min)",
    ]:
        if c not in d.columns:
            d[c] = 0.0
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)

    agg = (
        d.groupby("Segment", as_index=False)
        .agg({
            "Core Workload (min)": "sum",
            "Ancillary Workload (min)": "sum",
            "Supporting Workload (min)": "sum",
            "Exception Workload (min)": "sum",
            "Total Workload (min)": "sum",
        })
    )

    # Ensure standard business order.
    agg = (
        pd.DataFrame({"Segment": SERVICE_ORDER})
        .merge(agg, on="Segment", how="left")
        .fillna(0)
    )

    # Recalculate Total from C+A+S+E if source Total is blank/zero.
    component_total = (
        agg["Core Workload (min)"]
        + agg["Ancillary Workload (min)"]
        + agg["Supporting Workload (min)"]
        + agg["Exception Workload (min)"]
    )
    agg["Total Workload (min)"] = np.where(
        agg["Total Workload (min)"] > 0,
        agg["Total Workload (min)"],
        component_total,
    )

    grand_total = float(agg["Total Workload (min)"].sum())
    agg["Ratio"] = np.where(
        grand_total > 0,
        agg["Total Workload (min)"] / grand_total,
        0.0,
    )

    agg = agg.rename(columns={
        "Core Workload (min)": "Core Service (min)",
        "Ancillary Workload (min)": "Ancillary Service (min)",
        "Supporting Workload (min)": "Supporting Activity (min)",
        "Exception Workload (min)": "Exception Handling (min)",
    })

    return agg[cols]



def render_case_office_cards(
    core_df: pd.DataFrame,
    ancillary_df: pd.DataFrame,
    supporting_df: pd.DataFrame,
    exception_df: pd.DataFrame,
):
    """
    Section 5 executive cards by Office.

    IMPORTANT:
    - Cards use the four original C/A/S/E detail sources, not the summarized
      Workload-by-Activity table.
    - "Volume" in each detail source is summed by Office, therefore each office
      shows its own C / A / S / E quantity and does not repeat the network total.
    - HPH is displayed as HLC to follow the dashboard's standard office naming.
    """

    activity_sources = {
        "C": core_df,
        "A": ancillary_df,
        "S": supporting_df,
        "E": exception_df,
    }

    frames = []
    for activity, source in activity_sources.items():
        if source is None or source.empty:
            continue
        if "Office" not in source.columns or "Volume" not in source.columns:
            continue

        d = source[["Office", "Volume"]].copy()
        d["Office"] = d["Office"].astype(str).str.strip().str.upper()
        d["Office"] = d["Office"].replace({"HPH": "HLC"})
        d["Volume"] = pd.to_numeric(d["Volume"], errors="coerce").fillna(0.0)
        d = d[(d["Office"] != "") & (d["Volume"] > 0)]

        if d.empty:
            continue

        g = d.groupby("Office", as_index=False)["Volume"].sum()
        g["Activity"] = activity
        frames.append(g)

    if not frames:
        return

    long_summary = pd.concat(frames, ignore_index=True)

    summary = (
        long_summary.pivot_table(
            index="Office",
            columns="Activity",
            values="Volume",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    for activity in ["C", "A", "S", "E"]:
        if activity not in summary.columns:
            summary[activity] = 0.0

    summary["Total"] = summary[["C", "A", "S", "E"]].sum(axis=1)

    present = summary["Office"].astype(str).tolist()
    offices = [o for o in STANDARD_OFFICES if o in present]
    offices += sorted([o for o in present if o not in offices])

    if not offices:
        return

    st.markdown(
        f"""
        <div style="
            color:{COLORS['navy']};
            font-size:{UI['chart_title_size']}px;
            font-weight:700;
            margin:4px 0 10px 2px;">
            C / A / S / E Activity by Office
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Keep Office cards compact when filters return fewer than 4 offices.
    # All Offices: 4 cards fill the row as before.
    # Single Office: card uses only 1/4 row width instead of stretching full width.
    slot_count = max(4, len(offices))
    card_cols = st.columns(slot_count, gap="medium")[:len(offices)]

    activity_meta = {
        "C": ("Core", COLORS["blue"]),
        "A": ("Ancillary", COLORS["green"]),
        "S": ("Supporting", COLORS["amber"]),
        "E": ("Exception", COLORS["red"]),
    }

    for card_col, office in zip(card_cols, offices):
        row = summary.loc[summary["Office"] == office].iloc[0]

        vals = {
            activity: float(pd.to_numeric(row.get(activity, 0), errors="coerce") or 0)
            for activity in ["C", "A", "S", "E"]
        }
        total = float(sum(vals.values()))

        with card_col:
            card_html = f"""
                <div style="
                    background:#FFFFFF;
                    border:1px solid {COLORS['border']};
                    border-top:4px solid {COLORS['navy']};
                    border-radius:12px;
                    padding:14px 16px 13px;
                    min-height:168px;
                    box-sizing:border-box;
                    box-shadow:0 2px 7px rgba(0,59,112,0.045);">

                  <div style="
                      display:flex;
                      justify-content:space-between;
                      align-items:flex-start;
                      gap:10px;
                      margin-bottom:10px;">
                    <div style="
                        color:{COLORS['navy']};
                        font-size:18px;
                        font-weight:800;">
                      {html.escape(office)}
                    </div>

                    <div style="text-align:right;">
                      <div style="
                          color:#667085;
                          font-size:10.5px;
                          font-weight:600;">
                        TOTAL ACTIVITY
                      </div>
                      <div style="
                          color:{COLORS['navy']};
                          font-size:20px;
                          font-weight:800;
                          margin-top:2px;">
                        {total:,.0f}
                      </div>
                    </div>
                  </div>

                  <div style="
                      display:grid;
                      grid-template-columns:repeat(4,minmax(0,1fr));
                      border-top:1px solid #E7ECF1;
                      padding-top:11px;">
                    <div style="text-align:center;border-right:1px solid #E7ECF1;">
                      <div style="color:{activity_meta['C'][1]};font-size:14px;font-weight:800;">C</div>
                      <div style="color:{COLORS['navy']};font-size:16px;font-weight:750;margin-top:4px;">{vals['C']:,.0f}</div>
                    </div>
                    <div style="text-align:center;border-right:1px solid #E7ECF1;">
                      <div style="color:{activity_meta['A'][1]};font-size:14px;font-weight:800;">A</div>
                      <div style="color:{COLORS['navy']};font-size:16px;font-weight:750;margin-top:4px;">{vals['A']:,.0f}</div>
                    </div>
                    <div style="text-align:center;border-right:1px solid #E7ECF1;">
                      <div style="color:{activity_meta['S'][1]};font-size:14px;font-weight:800;">S</div>
                      <div style="color:{COLORS['navy']};font-size:16px;font-weight:750;margin-top:4px;">{vals['S']:,.0f}</div>
                    </div>
                    <div style="text-align:center;">
                      <div style="color:{activity_meta['E'][1]};font-size:14px;font-weight:800;">E</div>
                      <div style="color:{COLORS['navy']};font-size:16px;font-weight:750;margin-top:4px;">{vals['E']:,.0f}</div>
                    </div>
                  </div>

                  <div style="
                      display:grid;
                      grid-template-columns:repeat(4,minmax(0,1fr));
                      margin-top:4px;
                      color:#667085;
                      font-size:9.5px;
                      text-align:center;">
                    <div>Core</div>
                    <div>Ancillary</div>
                    <div>Supporting</div>
                    <div>Exception</div>
                  </div>
                </div>
                """
            card_html = "\n".join(line.lstrip() for line in card_html.splitlines())
            st.markdown(card_html, unsafe_allow_html=True)



def chart_case_allocation(df: pd.DataFrame):
    """C/A/S/E workload composition by Segment, displayed in hours."""
    summary = workload_breakdown_table(df)
    if summary.empty or float(summary["Total Workload (min)"].sum()) <= 0:
        st.info("No C/A/S/E workload data available for selected filters.")
        return

    pair_panel_title("Workload Composition by Activity")

    plot_df = (
        summary[summary["Total Workload (min)"] > 0]
        .copy()
        .sort_values("Total Workload (min)", ascending=True)
    )

    # Display layer only: convert minutes to hours.
    for _col in [
        "Core Service (min)",
        "Ancillary Service (min)",
        "Supporting Activity (min)",
        "Exception Handling (min)",
        "Total Workload (min)",
    ]:
        plot_df[_col] = pd.to_numeric(
            plot_df[_col], errors="coerce"
        ).fillna(0) / 60

    components = [
        ("Core Service (min)", "Core Service", COLORS["blue"]),
        ("Ancillary Service (min)", "Ancillary Service", COLORS["green"]),
        ("Supporting Activity (min)", "Supporting Activity", COLORS["amber"]),
        ("Exception Handling (min)", "Exception Handling", COLORS["red"]),
    ]

    fig = go.Figure()

    for col, label, color in components:
        fig.add_trace(
            go.Bar(
                y=plot_df["Segment"],
                x=plot_df[col],
                name=label,
                orientation="h",
                marker_color=color,
                customdata=np.column_stack(
                    [
                        plot_df["Total Workload (min)"],
                        plot_df["Ratio"],
                    ]
                ),
                hovertemplate=(
                    f"<b>{label}</b>"
                    "<br>Segment: %{y}"
                    "<br>Workload: %{x:,.1f} hrs"
                    "<br>Segment Total: %{customdata[0]:,.1f} hrs"
                    "<br>Share of Total: %{customdata[1]:.1%}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="stack",
        title=dict(text=""),
        xaxis_title="Workload (Hours)",
        yaxis_title="",
    )

    fig = plotly_layout(
        fig,
        350,
        show_legend=True,
        legend_position="top",
        margin_left=50,
        margin_right=35,
        margin_top=38,
        margin_bottom=40,
    )

    fig.update_xaxes(rangemode="tozero")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )



def render_workload_breakdown_table(df: pd.DataFrame):
    """C/A/S/E workload detail in hours; no TOTAL row and no Ratio column."""
    summary = workload_breakdown_table(df)
    if summary.empty:
        st.info("No workload breakdown data available for selected filters.")
        return

    pair_panel_title("Activity Breakdown")

    display = summary.copy()

    # Display layer only: convert minutes to hours.
    display["Core Service (Hours)"] = pd.to_numeric(
        display["Core Service (min)"], errors="coerce"
    ).fillna(0) / 60
    display["Ancillary Service (Hours)"] = pd.to_numeric(
        display["Ancillary Service (min)"], errors="coerce"
    ).fillna(0) / 60
    display["Supporting Activity (Hours)"] = pd.to_numeric(
        display["Supporting Activity (min)"], errors="coerce"
    ).fillna(0) / 60
    display["Exception Handling (Hours)"] = pd.to_numeric(
        display["Exception Handling (min)"], errors="coerce"
    ).fillna(0) / 60
    display["Total Workload (Hours)"] = pd.to_numeric(
        display["Total Workload (min)"], errors="coerce"
    ).fillna(0) / 60

    display = display[
        [
            "Segment",
            "Core Service (Hours)",
            "Ancillary Service (Hours)",
            "Supporting Activity (Hours)",
            "Exception Handling (Hours)",
            "Total Workload (Hours)",
        ]
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=350,
        column_config={
            "Segment": st.column_config.TextColumn(
                "Segment",
                width=70,
            ),
            "Core Service (Hours)": st.column_config.NumberColumn(
                "Core Service (Hours)",
                format="%,.1f",
                width=125,
            ),
            "Ancillary Service (Hours)": st.column_config.NumberColumn(
                "Ancillary Service (Hours)",
                format="%,.1f",
                width=140,
            ),
            "Supporting Activity (Hours)": st.column_config.NumberColumn(
                "Supporting Activity (Hours)",
                format="%,.1f",
                width=150,
            ),
            "Exception Handling (Hours)": st.column_config.NumberColumn(
                "Exception Handling (Hours)",
                format="%,.1f",
                width=150,
            ),
            "Total Workload (Hours)": st.column_config.NumberColumn(
                "Total Workload (Hours)",
                format="%,.1f",
                width=135,
            ),
        },
    )



def render_activity_detail_table(
    df: pd.DataFrame,
    activity_type: str,
):
    """Detail table for one C/A/S/E source sheet."""
    if df is None or df.empty:
        st.info(f"No {activity_type} detail data available for selected filters.")
        return

    d = df.copy()

    # Defensive filter: detail table only shows months/rows with actual data.
    d["Volume"] = pd.to_numeric(d["Volume"], errors="coerce")
    d = d[d["Volume"].fillna(0) > 0].copy()

    if d.empty:
        st.info(f"No {activity_type} detail data available for selected filters.")
        return

    d["Month"] = d["MonthDate"].dt.strftime("%b-%y")

    # Consistent business order requested for all C / A / S / E tabs:
    # Office → Month → Code → Code Description → Volume
    preferred = ["Office", "Month", "Code", "Code Description", "Volume"]
    cols = [c for c in preferred if c in d.columns]

    # Drop descriptive columns that are completely blank.
    cols = [
        c for c in cols
        if c in ["Office", "Month", "Volume"]
        or d[c].astype(str).str.strip().replace("nan", "").ne("").any()
    ]

    # Capture months before removing MonthDate from the visible table.
    months_with_data = (
        d["MonthDate"].dropna().drop_duplicates().sort_values()
        .dt.strftime("%b-%y").tolist()
    )

    sort_source = d.copy()
    sort_cols = [c for c in ["Office", "Code", "MonthDate"] if c in sort_source.columns]
    if sort_cols:
        sort_source = sort_source.sort_values(sort_cols)

    d = sort_source[cols].copy()
    if "Volume" in d.columns:
        d["Volume"] = pd.to_numeric(d["Volume"], errors="coerce").fillna(0)

    if months_with_data:
        st.caption("Months with data: " + ", ".join(months_with_data))

    # Activity Detail table:
    # No fixed width is applied. Streamlit determines each column width from content.
    auto_fit_config = {
        "Office": st.column_config.TextColumn("Office"),
        "Month": st.column_config.TextColumn("Month"),
        "Code": st.column_config.TextColumn("Code"),
        "Code Description": st.column_config.TextColumn("Code Description"),
        "Volume": st.column_config.NumberColumn(
            "Volume", format="%,.0f"
        ),
    }

    st.dataframe(
        d,
        use_container_width=False,
        hide_index=True,
        height=min(420, max(160, 38 + len(d) * 34)),
        column_config={c: auto_fit_config[c] for c in d.columns if c in auto_fit_config},
    )
