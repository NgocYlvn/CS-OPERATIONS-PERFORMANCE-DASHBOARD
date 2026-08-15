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

def chart_office_capacity_trend(df: pd.DataFrame):
    """3-line HC trend from sheet HC with shaded gap between Approved HC and Actual HC."""
    if df.empty:
        st.info("No HC trend data available for selected filters.")
        return

    required_cols = ["MonthDate", "Total Approved HC", "Total Actual HC", "Total Required HC"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.info("HC trend cannot be displayed because required HC columns are missing.")
        return

    trend_source = df[
        ["MonthDate", "Total Approved HC", "Total Actual HC", "Total Required HC"]
    ].copy()

    for col in ["Total Approved HC", "Total Actual HC", "Total Required HC"]:
        trend_source[col] = pd.to_numeric(trend_source[col], errors="coerce")

    # Exclude months where all three HC values are blank.
    trend_source = trend_source.dropna(
        subset=["Total Approved HC", "Total Actual HC", "Total Required HC"],
        how="all",
    )

    if trend_source.empty:
        st.info("No HC trend data available for selected filters.")
        return

    trend = (
        trend_source.groupby("MonthDate", as_index=False)[
            ["Total Approved HC", "Total Actual HC", "Total Required HC"]
        ]
        .sum(min_count=1)
        .sort_values("MonthDate")
    )
    trend["Month"] = trend["MonthDate"].dt.strftime("%b-%y")

    # Use one canonical series variable for Required HC so the line and
    # its visible labels can never reference different column names.
    if "Total Required HC" in trend.columns:
        required_values = trend["Total Required HC"]
    elif "Required" in trend.columns:
        required_values = trend["Required"]
    elif "Required HC" in trend.columns:
        required_values = trend["Required HC"]
    else:
        st.info("HC trend cannot be displayed because Required HC data is missing.")
        return

    fig = go.Figure()

    # Approved HC line
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=trend["Total Approved HC"],
            mode="lines+markers",
            name="Approved HC",
            line=dict(color=BUSINESS_COLORS["approved"], width=3),
            marker=dict(size=7),
            hovertemplate="%{x}<br>Approved HC: %{y:,.1f}<extra></extra>",
        )
    )

    # Actual HC line — baseline for the shaded Actual vs Required gap.
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=trend["Total Actual HC"],
            mode="lines+markers",
            name="Actual HC",
            line=dict(color=BUSINESS_COLORS["actual"], width=3),
            marker=dict(size=7),
            hovertemplate="%{x}<br>Actual HC: %{y:,.1f}<extra></extra>",
        )
    )

    # Required HC line + shaded gap to Actual HC.
    # The fill is intentionally between Actual HC and Required HC.
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=required_values,
            mode="lines+markers",
            name="Required HC",
            line=dict(color=BUSINESS_COLORS["required"], width=3, dash="solid"),
            marker=dict(size=7),
            fill="tonexty",
            fillcolor="rgba(245, 158, 11, 0.14)",
            hovertemplate="%{x}<br>Required HC: %{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="HC Capacity Trend",
        yaxis_title="HC",
        hovermode="x unified",
    )
    fig = plotly_layout(fig, UI["chart_height"], show_legend=True, legend_position="top", margin_left=56, margin_right=42, margin_top=76, margin_bottom=46)

    # Keep the HC chart proportional: Y-axis always starts from zero.
    fig.update_yaxes(rangemode="tozero")

    fig.update_xaxes(type="category", categoryorder="array", categoryarray=trend["Month"].tolist())
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})



def chart_workload_by_pic(fte_df: pd.DataFrame, selected_office: str):
    """
    PIC Workload.

    Business display rule:
    - PIC Workload (hrs) = CS FTE Factor × Available Standard Time / PIC.
    - Available Standard Time / PIC = 167.2 hrs/month.
    - Utilization = PIC Workload / 167.2 = CS FTE Factor.

    Display logic:
    - Specific Office: show all PICs with data in that office.
    - All Offices: show Top 10 PICs by Utilization across all offices.
    - Colors:
        >100%      = Red (Overload)
        >95%–100%  = Orange (High Load)
        90%–95%    = Blue (Balanced)
        <90%       = Green (Less Load)
    """
    if fte_df is None or fte_df.empty:
        st.info("No CS FTE data available for selected filters.")
        return

    d = fte_df.copy()
    d["Actual FTE"] = pd.to_numeric(d["Actual FTE"], errors="coerce")
    d = d.dropna(subset=["Office", "CS PIC", "Actual FTE"])
    d = d[(d["Office"] != "") & (d["CS PIC"] != "")]

    if d.empty:
        st.info("No CS FTE data available for selected filters.")
        return

    pic_data = (
        d.groupby(["Office", "CS PIC"], as_index=False)["Actual FTE"]
        .mean()
    )
    pic_data["Avaiable time Hours"] = CAPACITY_HOURS_PER_FTE
    pic_data["Actual Workload Hours"] = pic_data["Actual FTE"] * CAPACITY_HOURS_PER_FTE
    pic_data["Utilization"] = pic_data["Actual FTE"]

    def _status(util):
        # Standard workload color rule:
        # >100% = Overload / Red
        # >95%–100% = High Load / Orange
        # 90%–95% = Balanced / Blue
        # <90% = Less Load / Green
        if util > 1.00:
            return "Overload", COLORS["red"]
        if util > 0.95:
            return "High Load", COLORS["amber"]
        if util >= 0.90:
            return "Balanced", COLORS["blue"]
        return "Less Load", COLORS["green"]

    mapped = pic_data["Utilization"].apply(_status)
    pic_data["Status"] = mapped.map(lambda x: x[0])
    pic_data["Bar Color"] = mapped.map(lambda x: x[1])

    total_pic = int(len(pic_data))
    overloaded_pic = int((pic_data["Utilization"] > 1.0).sum())

    if selected_office == "All Offices":
        display = (
            pic_data.sort_values(
                ["Utilization", "Actual Workload Hours"],
                ascending=[False, False],
            )
            .head(10)
            .copy()
        )
        display["PIC Label"] = display.apply(
            lambda r: f"{r['Office']} | {r['CS PIC']}",
            axis=1,
        )
        subtitle = "Top 10 PICs by Capacity Utilization – All Offices"
    else:
        display = (
            pic_data[pic_data["Office"] == selected_office]
            .sort_values(
                ["Utilization", "Actual Workload Hours"],
                ascending=[False, False],
            )
            .copy()
        )
        display["PIC Label"] = display["CS PIC"].astype(str)
        subtitle = f"All PICs – {selected_office}"

    if display.empty:
        st.info("No PIC workload data available for selected filters.")
        return

    display = display.sort_values(
        ["Utilization", "Actual Workload Hours"],
        ascending=[True, True],
    )

    display["Label"] = display.apply(
        lambda r: f"{r['Actual Workload Hours']:,.1f} | {r['Utilization']*100:.0f}%",
        axis=1,
    )

    chart_height = max(360, min(650, 43 * len(display) + 150))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=display["Actual Workload Hours"],
            y=display["PIC Label"],
            orientation="h",
            name="PIC Workload",
            marker_color=display["Bar Color"],
            text=display["Label"],
            textposition="outside",
            cliponaxis=False,
            customdata=np.column_stack([
                display["Office"],
                display["Actual FTE"],
                display["Utilization"],
                display["Status"],
            ]),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Office: %{customdata[0]}<br>"
                "PIC Workload: %{x:,.1f} hrs<br>"
                "CS FTE Factor: %{customdata[1]:.2f}<br>"
                "Utilization: %{customdata[2]:.1%}<br>"
                "Status: %{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=CAPACITY_HOURS_PER_FTE,
        line_width=2.5,
        line_dash="dash",
        line_color=COLORS["navy"],
        annotation_text="Avaiable time 167.2 hour",
        annotation_position="top",
        annotation_font_color=COLORS["navy"],
    )

    max_actual = float(display["Actual Workload Hours"].max())
    x_max = max(max_actual * 1.15, CAPACITY_HOURS_PER_FTE * 1.25)

    fig.update_layout(
        title=dict(
            text=(
                "PIC Workload"
                f"<br><span style='font-size:11px;color:#667085;font-weight:400'>{subtitle}</span>"
            ),
            x=0.0,
            xanchor="left",
            y=0.98,
            yanchor="top",
            font=dict(size=UI["chart_title_size"], color=COLORS["navy"]),
        ),
        height=chart_height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color=COLORS["text"]),
        margin=dict(l=125, r=80, t=76, b=48),
        bargap=0.24,
        showlegend=False,
    )

    # Keep only one compact management summary in the upper-right.
    existing_annotations = list(fig.layout.annotations) if fig.layout.annotations else []
    existing_annotations.append(
        dict(
            text=f"Overloaded PICs: <b>{overloaded_pic}</b> / Total PICs: <b>{total_pic}</b>",
            x=1,
            y=1.075,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            font=dict(size=UI["note_size"], color=COLORS["muted"]),
        )
    )
    fig.update_layout(annotations=existing_annotations)

    fig.update_xaxes(
        title_text="Workload Hours",
        range=[0, x_max],
        gridcolor=COLORS["grid"],
        zeroline=False,
        automargin=True,
        tickfont=dict(size=UI["axis_size"]),
        title_font=dict(size=UI["axis_size"], color=COLORS["gray_dark"]),
    )
    fig.update_yaxes(
        title_text="",
        gridcolor="rgba(0,0,0,0)",
        automargin=True,
        tickfont=dict(size=UI["axis_size"]),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            align-items:center;
            gap:18px;
            margin-top:4px;
            margin-bottom:2px;
            color:#667085;
            font-size:11px;
            line-height:1.2;
            white-space:normal;
            flex-wrap:wrap;">
            <span><span style="display:inline-block;width:9px;height:9px;background:{COLORS['red']};margin-right:5px;border-radius:2px;"></span>Overload &gt;100%</span>
            <span><span style="display:inline-block;width:9px;height:9px;background:{COLORS['amber']};margin-right:5px;border-radius:2px;"></span>High Load &gt;95–100%</span>
            <span><span style="display:inline-block;width:9px;height:9px;background:{COLORS['blue']};margin-right:5px;border-radius:2px;"></span>Balanced 90–95%</span>
            <span><span style="display:inline-block;width:9px;height:9px;background:{COLORS['green']};margin-right:5px;border-radius:2px;"></span>Less Load &lt;90%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )



def chart_workload_by_service(df: pd.DataFrame):
    if df.empty:
        st.info("No workload data available for selected filters.")
        return
    agg = df.groupby(["Segment", "Service Label"], as_index=False)["Workload Hours"].sum()
    total = agg["Workload Hours"].sum()
    agg["% of Total"] = agg["Workload Hours"].apply(lambda x: safe_div(x, total))
    agg["Label"] = agg.apply(lambda r: f"{r['Workload Hours']:,.1f} | {r['% of Total']*100:.1f}%", axis=1)
    agg["SortOrder"] = agg["Segment"].apply(lambda x: SERVICE_ORDER.index(x) if x in SERVICE_ORDER else 999)
    agg = agg.sort_values(["Workload Hours"], ascending=True)
    fig = px.bar(
        agg,
        x="Workload Hours",
        y="Service Label",
        orientation="h",
        text="Label",
        color_discrete_sequence=[COLORS["blue"]],
        title="Workload Breakdown by Service Type",
    )
    fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>%{x:,.1f} hours<extra></extra>")
    fig = plotly_layout(fig, UI["chart_height"], show_legend=False, margin_left=110, margin_right=70, margin_top=64, margin_bottom=44)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def chart_workload_composition(df: pd.DataFrame):
    if df.empty:
        st.info("No workload composition data available.")
        return
    comp = pd.DataFrame({
        "Activity": ["Core", "Ancillary", "Supporting", "Exception"],
        "Hours": [df["Core Hours"].sum(), df["Ancillary Hours"].sum(), df["Supporting Hours"].sum(), df["Exception Hours"].sum()],
    })
    total = comp["Hours"].sum()
    comp["Share"] = comp["Hours"].apply(lambda x: safe_div(x, total))
    fig = go.Figure()
    color_map = [COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["red"]]
    for _, row in comp.iterrows():
        color = color_map[comp.index[comp["Activity"] == row["Activity"]][0]]
        fig.add_trace(go.Bar(
            y=["Total Workload"],
            x=[row["Share"]],
            name=row["Activity"],
            orientation="h",
            marker_color=color,
            text=[f"{row['Activity']}<br>{row['Share']*100:.1f}%" if row["Share"] > 0.06 else ""],
            hovertemplate=f"{row['Activity']}: {row['Hours']:,.1f} hrs ({row['Share']*100:.1f}%)<extra></extra>",
        ))
    fig.update_layout(barmode="stack", xaxis_tickformat=".0%", title="Workload Composition – C/A/S/E")
    fig = plotly_layout(fig, 320, show_legend=True, legend_position="top", margin_left=52, margin_right=40, margin_top=66, margin_bottom=44)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def chart_workload_trend(df: pd.DataFrame):
    if df.empty:
        st.info("No trend data available.")
        return
    agg = df.groupby(["MonthDate", "Office"], as_index=False)["Workload Hours"].sum().sort_values("MonthDate")
    agg["Month"] = agg["MonthDate"].dt.strftime("%b-%y")
    fig = px.line(
        agg,
        x="Month",
        y="Workload Hours",
        color="Office",
        markers=True,
        color_discrete_sequence=[COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["red"]],
        title="Monthly Workload Trend",
    )
    fig.update_traces(hovertemplate="%{fullData.name}<br>%{x}: %{y:,.1f} hrs<extra></extra>")
    fig.update_xaxes(categoryorder="array", categoryarray=agg["Month"].drop_duplicates().tolist())
    fig = plotly_layout(fig, UI["chart_height"], show_legend=True, legend_position="top", margin_left=56, margin_right=40, margin_top=66, margin_bottom=48)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def chart_capacity_trend(workload: pd.DataFrame, fte: pd.DataFrame):
    if workload.empty and fte.empty:
        st.info("No capacity data available.")
        return
    wl = workload.groupby("MonthDate", as_index=False)["Workload Hours"].sum() if not workload.empty else pd.DataFrame(columns=["MonthDate", "Workload Hours"])
    ft = fte.groupby("MonthDate", as_index=False)["Actual FTE"].sum() if not fte.empty else pd.DataFrame(columns=["MonthDate", "Actual FTE"])
    cap = pd.merge(wl, ft, on="MonthDate", how="outer").fillna(0)
    cap["Capacity Hours"] = cap["Actual FTE"] * CAPACITY_HOURS_PER_FTE
    cap["Month"] = cap["MonthDate"].dt.strftime("%b-%y")
    cap = cap.sort_values("MonthDate")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cap["Month"], y=cap["Capacity Hours"], name="Capacity Hours", marker_color=COLORS["light_blue"]))
    fig.add_trace(go.Scatter(x=cap["Month"], y=cap["Workload Hours"], name="Workload Hours", mode="lines+markers", line=dict(color=COLORS["red"], width=3)))
    fig.update_layout(title="Workload vs Capacity Trend", yaxis_title="Hours")
    fig.update_xaxes(categoryorder="array", categoryarray=cap["Month"].tolist())
    fig = plotly_layout(fig, UI["chart_height"], show_legend=True, legend_position="top", margin_left=58, margin_right=40, margin_top=66, margin_bottom=48)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def build_segment_workload(
    df: pd.DataFrame,
    mode_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Section 4 source table — Workload by Segment.

    Business fields:
    - Allocation Time (h): total workload hours from BU allocation.
    - Workload Share (%): Segment workload / total workload.
    - Required FTE:
        Prefer source field "Office HC Allocation Ratio" when available.
        For multiple months, calculate monthly Segment FTE and average across
        valid months because Required FTE is a monthly capacity requirement,
        not a cumulative-period quantity.
        Fallback = monthly Workload Hours / 167.2 hours/FTE.
    - Shipment Volume: Shipment volume sheet, mapped to AE/AI/OE/OI/CC/TR/WH.
    """
    base_cols = [
        "Segment", "Allocation Time (h)", "Workload Share",
        "Required FTE", "Shipment Volume"
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=base_cols)

    d = df.copy()
    if "Segment" not in d.columns or "Workload Hours" not in d.columns:
        return pd.DataFrame(columns=base_cols)

    d["Segment"] = d["Segment"].astype(str).str.strip().str.upper()
    d["Workload Hours"] = pd.to_numeric(d["Workload Hours"], errors="coerce").fillna(0)
    d = d[d["Segment"].isin(SERVICE_ORDER)].copy()

    if d.empty:
        return pd.DataFrame(columns=base_cols)

    seg = (
        d.groupby("Segment", as_index=False)["Workload Hours"]
        .sum()
        .rename(columns={"Workload Hours": "Allocation Time (h)"})
    )

    seg = (
        pd.DataFrame({"Segment": SERVICE_ORDER})
        .merge(seg, on="Segment", how="left")
        .fillna({"Allocation Time (h)": 0.0})
    )

    total_hours = float(seg["Allocation Time (h)"].sum())
    seg["Workload Share"] = np.where(
        total_hours > 0,
        seg["Allocation Time (h)"] / total_hours,
        0.0,
    )

    fte_by_segment = pd.DataFrame({"Segment": SERVICE_ORDER, "Required FTE": 0.0})

    if "MonthDate" in d.columns and d["MonthDate"].notna().any():
        monthly = d.copy()

        use_source_fte = (
            "Office HC Allocation Ratio" in monthly.columns
            and pd.to_numeric(
                monthly["Office HC Allocation Ratio"], errors="coerce"
            ).fillna(0).abs().sum() > 0
        )

        if use_source_fte:
            monthly["Required FTE Source"] = pd.to_numeric(
                monthly["Office HC Allocation Ratio"], errors="coerce"
            )
            monthly_fte = (
                monthly.dropna(subset=["MonthDate"])
                .groupby(["MonthDate", "Segment"], as_index=False)["Required FTE Source"]
                .sum(min_count=1)
                .rename(columns={"Required FTE Source": "Required FTE"})
            )
        else:
            monthly_hours = (
                monthly.dropna(subset=["MonthDate"])
                .groupby(["MonthDate", "Segment"], as_index=False)["Workload Hours"]
                .sum()
            )
            monthly_hours["Required FTE"] = (
                monthly_hours["Workload Hours"] / CAPACITY_HOURS_PER_FTE
            )
            monthly_fte = monthly_hours[["MonthDate", "Segment", "Required FTE"]]

        if not monthly_fte.empty:
            fte_by_segment = (
                monthly_fte.groupby("Segment", as_index=False)["Required FTE"]
                .mean()
            )
            fte_by_segment = (
                pd.DataFrame({"Segment": SERVICE_ORDER})
                .merge(fte_by_segment, on="Segment", how="left")
                .fillna({"Required FTE": 0.0})
            )
    else:
        fte_by_segment = seg[["Segment", "Allocation Time (h)"]].copy()
        fte_by_segment["Required FTE"] = (
            fte_by_segment["Allocation Time (h)"] / CAPACITY_HOURS_PER_FTE
        )
        fte_by_segment = fte_by_segment[["Segment", "Required FTE"]]

    seg = seg.merge(fte_by_segment, on="Segment", how="left")
    seg["Required FTE"] = pd.to_numeric(
        seg["Required FTE"], errors="coerce"
    ).fillna(0)

    seg["Shipment Volume"] = 0.0
    if (
        mode_df is not None
        and not mode_df.empty
        and {"Mode", "Volume"}.issubset(mode_df.columns)
    ):
        vol = mode_df.copy()
        vol["Mode"] = vol["Mode"].astype(str).str.strip().str.upper()
        vol["Volume"] = pd.to_numeric(vol["Volume"], errors="coerce").fillna(0)

        volume_segment_map = {
            "AE": "AE", "AI": "AI", "OE": "OE", "OI": "OI",
            "OEFCL": "OE", "OELCL": "OE", "OIFCL": "OI", "OILCL": "OI",
            "CC": "CC", "CE": "CC", "CI": "CC",
            "TR": "TR", "DM": "TR", "DE": "TR", "DI": "TR",
            "WH": "WH", "HE": "WH", "HI": "WH",
        }
        vol["Segment"] = vol["Mode"].map(volume_segment_map)

        volume_by_segment = (
            vol.dropna(subset=["Segment"])
            .groupby("Segment", as_index=False)["Volume"]
            .sum()
            .rename(columns={"Volume": "Shipment Volume Source"})
        )
        seg = seg.merge(volume_by_segment, on="Segment", how="left")
        seg["Shipment Volume"] = pd.to_numeric(
            seg["Shipment Volume Source"], errors="coerce"
        ).fillna(0)
        seg = seg.drop(columns=["Shipment Volume Source"])

    seg["Segment"] = pd.Categorical(
        seg["Segment"], categories=SERVICE_ORDER, ordered=True
    )
    seg = seg.sort_values("Segment").reset_index(drop=True)
    seg["Segment"] = seg["Segment"].astype(str)

    return seg[
        ["Segment", "Allocation Time (h)", "Workload Share", "Required FTE", "Shipment Volume"]
    ]


def chart_service_matrix(
    df: pd.DataFrame,
    mode_df: Optional[pd.DataFrame] = None,
):
    """Workload by Segment — flower-style packed bubble chart."""
    seg = build_segment_workload(df, mode_df)
    if seg.empty or float(seg["Allocation Time (h)"].sum()) <= 0:
        st.info("No segment workload data available for selected filters.")
        return


    plot_df = seg[seg["Allocation Time (h)"] > 0].copy()
    plot_df = plot_df.sort_values("Workload Share", ascending=False).reset_index(drop=True)
    # Ordered overlapping bubble cluster.
    # plot_df is already sorted by Workload Share descending.
    # Rank 1 = center; remaining ranks are arranged around it in visual order.
    # Compact overlapping bubble cluster.
    # plot_df is sorted by Workload Share descending:
    # 1 center, 2 left, 3 right, 4 upper-left, 5 upper-right,
    # 6 lower-right, 7 lower-left/bottom.
    # Coordinates are intentionally close so bubbles overlap visibly.
    # Dynamic ranked overlapping bubble cluster.
    # IMPORTANT: positions are assigned by CURRENT RANK, not by Segment name.
    # Therefore the layout automatically changes with Office / Month / filters.
    #
    # plot_df is already sorted by Workload Share descending:
    # Rank 1 -> center
    # Rank 2 -> left
    # Rank 3 -> upper-left
    # Rank 4 -> top
    # Rank 5 -> upper-right
    # Rank 6 -> lower-right
    # Rank 7 -> lower-left
    rank_positions = [
        (0.00, 0.00),     # Rank 1
        (-0.58, 0.00),    # Rank 2
        (-0.38, 0.52),    # Rank 3
        (0.05, 0.66),     # Rank 4
        (0.50, 0.42),     # Rank 5
        (0.50, -0.38),    # Rank 6
        (-0.22, -0.58),   # Rank 7
        (-0.64, -0.34),   # fallback Rank 8
        (0.00, -0.72),    # fallback Rank 9
        (0.72, 0.00),     # fallback Rank 10
    ]

    plot_df["Rank"] = np.arange(1, len(plot_df) + 1)
    plot_df["x"] = [rank_positions[i][0] for i in range(len(plot_df))]
    plot_df["y"] = [rank_positions[i][1] for i in range(len(plot_df))]
    max_share = float(plot_df["Workload Share"].max())
    plot_df["Bubble Size"] = 74 + (plot_df["Workload Share"] / max_share) * 100 if max_share > 0 else 88
    segment_color_map = {svc: CORPORATE_PALETTE[i % len(CORPORATE_PALETTE)] for i, svc in enumerate(SERVICE_ORDER)}

    fig = go.Figure()
    for _, r in plot_df.iterrows():
        svc = r["Segment"]
        fig.add_trace(go.Scatter(
            x=[r["x"]], y=[r["y"]], mode="markers+text", name=svc,
            text=[f"<b>{svc}</b><br>{r['Workload Share']:.1%}"],
            textposition="middle center",
            textfont=dict(family=UI["font_family"], size=11, color="#FFFFFF" if r["Workload Share"] >= 0.06 else COLORS["navy"]),
            marker=dict(size=[r["Bubble Size"]], color=segment_color_map.get(svc, COLORS["blue"]), opacity=0.94, line=dict(color="#FFFFFF", width=2.0)),
            customdata=[[r["Shipment Volume"], r["Allocation Time (h)"], r["Required FTE"], r["Workload Share"]]],
            hovertemplate=(f"<b>{svc}</b><br>Shipment Volume: %{{customdata[0]:,.0f}}<br>Allocation Time: %{{customdata[1]:,.1f}} hrs<br>Required FTE: %{{customdata[2]:,.2f}}<br>Workload Share: %{{customdata[3]:.1%}}<extra></extra>"),
            showlegend=False,
        ))

    fig = plotly_layout(fig, 340, show_legend=False, margin_left=24, margin_right=24, margin_top=8, margin_bottom=8)
    fig.update_layout(title=dict(text=""))
    fig.update_xaxes(
        visible=False, showgrid=False, zeroline=False, showticklabels=False,
        title_text="", range=[-1.12, 1.12], fixedrange=True
    )
    fig.update_yaxes(
        visible=False, showgrid=False, zeroline=False, showticklabels=False,
        title_text="", range=[-1.00, 1.00], scaleanchor="x", scaleratio=1, fixedrange=True
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def segment_workload_table(df: pd.DataFrame, mode_df: pd.DataFrame):
    """Executive summary table for Section 4; no TOTAL row in detail tables."""
    seg = build_segment_workload(df, mode_df)
    if seg.empty:
        st.info("No segment workload data available for selected filters.")
        return

    pair_panel_title("Segment Workload Breakdown")
    display = (
        seg.copy()
        .sort_values("Workload Share", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"Workload Share": "Workload Share (%)"})
    )
    display["Workload Share (%)"] = pd.to_numeric(display["Workload Share (%)"], errors="coerce").fillna(0) * 100
    display = display[["Segment", "Shipment Volume", "Allocation Time (h)", "Required FTE", "Workload Share (%)"]]

    st.dataframe(
        display, use_container_width=True, hide_index=True, height=390,
        column_config={
            "Segment": st.column_config.TextColumn("Segment", width=70),
            "Shipment Volume": st.column_config.NumberColumn("Volume", width="medium", format="%,.0f"),
            "Allocation Time (h)": st.column_config.NumberColumn("Actual Working Time (Hours)", width="medium", format="%,.1f"),
            "Required FTE": st.column_config.NumberColumn("Required FTE", width="small", format="%.2f"),
            "Workload Share (%)": st.column_config.NumberColumn("Workload Share (%)", width="medium", format="%.1f%%"),
        },
    )

def chart_shipment_modes(mode_df: pd.DataFrame):
    """Horizontal bar chart showing shipment volume and share by transportation mode."""
    if mode_df.empty:
        st.info("No shipment mode data available for selected filters.")
        return
    agg = mode_df.groupby("Mode", as_index=False)["Volume"].sum().sort_values("Volume", ascending=False).reset_index(drop=True)
    total = float(agg["Volume"].sum())
    if total <= 0:
        st.info("No shipment mode data available for selected filters.")
        return

    pair_panel_title("Shipment Volume by Transportation Mode")
    agg["Share"] = agg["Volume"] / total
    plot_df = agg.sort_values("Volume", ascending=True).copy()
    plot_df["Display Label"] = plot_df.apply(lambda r: f"{r['Volume']:,.0f} ({r['Share']:.1%})", axis=1)
    fig = go.Figure(go.Bar(
        x=plot_df["Volume"], y=plot_df["Mode"], orientation="h",
        marker=dict(color=COLORS["blue"]), text=plot_df["Display Label"], textposition="outside",
        textfont=dict(size=UI["axis_size"], color=COLORS["navy"]), cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Shipment Volume: %{x:,.0f}<br>Share: %{customdata:.1%}<extra></extra>",
        customdata=plot_df["Share"],
    ))
    fig.update_layout(title_text="", xaxis_title=None, yaxis_title="", bargap=0.26)
    fig.update_yaxes(categoryorder="array", categoryarray=plot_df["Mode"].tolist(), automargin=True, tickfont=dict(size=UI["axis_size"]))
    fig.update_xaxes(automargin=True, rangemode="tozero", tickformat=",.0f")
    fig = plotly_layout(fig, 460, show_legend=False, margin_left=58, margin_right=105, margin_top=12, margin_bottom=40)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def mode_detail_table(mode_df: pd.DataFrame):
    """Detail table paired with the transportation-mode chart; no TOTAL row."""
    if mode_df is None or mode_df.empty:
        st.info("No shipment mode detail available for selected filters.")
        return
    detail = mode_df.groupby("Mode", as_index=False)["Volume"].sum().sort_values("Volume", ascending=False).reset_index(drop=True)
    total = float(detail["Volume"].sum())
    if total <= 0:
        st.info("No shipment mode detail available for selected filters.")
        return
    pair_panel_title("Transportation Mode Detail")
    detail["Rank"] = np.arange(1, len(detail) + 1)
    detail["Share"] = detail["Volume"] / total
    display = detail.rename(columns={"Volume": "Shipment Volume"})[["Rank", "Mode", "Shipment Volume", "Share"]].copy()

    # Compact height: only show the rows that actually exist instead of
    # reserving the full chart height and leaving blank rows underneath.
    mode_table_height = min(SHIPMENT_PAIR_HEIGHT, 38 + 35 * len(display))

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=mode_table_height,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small", format="%d"),
            "Mode": st.column_config.TextColumn("Mode", width="small"),
            "Shipment Volume": st.column_config.NumberColumn("Shipment Volume", width="large", format="%,.0f"),
            "Share": st.column_config.NumberColumn("Share", width="small", format="percent"),
        },
    )

def build_customer_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate and rank all customers by shipment volume for current filters."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["Rank", "Customer", "Shipment Volume"])

    ranking = (
        df.groupby("Customer", as_index=False)["Volume"]
        .sum()
        .sort_values("Volume", ascending=False)
        .reset_index(drop=True)
    )
    ranking["Rank"] = np.arange(1, len(ranking) + 1)
    ranking = ranking.rename(columns={"Volume": "Shipment Volume"})
    return ranking[["Rank", "Customer", "Shipment Volume"]]


def chart_top_customers(df: pd.DataFrame):
    if df.empty:
        st.info("No customer volume data available for selected filters.")
        return
    ranking = build_customer_ranking(df)
    top = ranking.head(15).sort_values("Shipment Volume", ascending=True)
    pair_panel_title("Top 15 Customers by Shipment Volume")
    fig = px.bar(top, x="Shipment Volume", y="Customer", orientation="h", text="Shipment Volume", color_discrete_sequence=[COLORS["blue"]])
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>Shipment Volume: %{x:,.0f}<extra></extra>")
    fig.update_layout(title_text="", yaxis_title="", xaxis_title=None, bargap=0.18)
    fig.update_yaxes(automargin=True, tickfont=dict(size=UI["axis_size"]))
    fig.update_xaxes(automargin=True)
    fig = plotly_layout(fig, 460, show_legend=False, margin_left=155, margin_right=60, margin_top=22, margin_bottom=40)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def customer_detail_volume_table(df: pd.DataFrame):
    """Full customer ranking paired with the Top 15 chart; scrollable and no TOTAL row."""
    ranking = build_customer_ranking(df)
    if ranking.empty:
        st.info("No customer detail data available for selected filters.")
        return

    pair_panel_title("Customer Volume Detail")
    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True,
        height=SHIPMENT_PAIR_HEIGHT,  # keep full-height scrollable detail for all customers
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small", format="%d"),
            "Customer": st.column_config.TextColumn("Customer", width="large"),
            "Shipment Volume": st.column_config.NumberColumn("Shipment Volume", width="medium", format="%,.0f"),
        },
    )


def chart_resolution(df: pd.DataFrame):
    """CS Solution performance chart."""
    if df is None or df.empty:
        st.info("No CS Resolution data available for selected filters.")
        return
    pair_panel_title("CS Resolution Trend")
    agg = df.groupby("MonthDate", as_index=False).agg(**{"Total Abnormality": ("Total Abnormality", "sum"), "Resolved": ("Resolved", "sum")}).sort_values("MonthDate")
    agg["Resolution Rate"] = np.where(agg["Total Abnormality"] > 0, agg["Resolved"] / agg["Total Abnormality"], np.nan)
    agg["Month"] = agg["MonthDate"].dt.strftime("%b-%y")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=agg["Month"], y=agg["Total Abnormality"], name="Total Exception Case", marker_color=BUSINESS_COLORS["supporting"], text=agg["Total Abnormality"], texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False))
    fig.add_trace(go.Bar(x=agg["Month"], y=agg["Resolved"], name="Resolved by CS", marker_color=BUSINESS_COLORS["actual"], text=agg["Resolved"], texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False))
    fig.add_trace(go.Scatter(x=agg["Month"], y=agg["Resolution Rate"], name="CS Resolution Rate", mode="lines+markers+text", line=dict(color=COLORS["green"], width=3), marker=dict(size=7), text=agg["Resolution Rate"], texttemplate="%{text:.1%}", textposition="top center", yaxis="y2"))
    fig.update_layout(title_text="", barmode="group", yaxis=dict(title="Cases", rangemode="tozero"), yaxis2=dict(title="Resolution Rate", overlaying="y", side="right", tickformat=".0%", range=[0, 1.20], showgrid=False))
    fig = plotly_layout(fig, 390, show_legend=True, legend_position="top", margin_left=58, margin_right=68, margin_top=38, margin_bottom=44)
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=agg["Month"].tolist())
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_cs_solution_table(df: pd.DataFrame):
    """CS Resolution detail table; no TOTAL row."""
    if df is None or df.empty:
        st.info("No CS Resolution data available for selected filters.")
        return
    pair_panel_title("CS Resolution by Office")
    d = df.copy().sort_values(["Office", "MonthDate"])
    d["Month"] = d["MonthDate"].dt.strftime("%b-%y")
    display = d[["Office", "Month", "Total Abnormality", "Resolved", "Resolution Rate"]].copy()
    display["Resolution Rate (%)"] = (
        pd.to_numeric(display["Resolution Rate"], errors="coerce") * 100
    )
    display = display.drop(columns=["Resolution Rate"])

    resolution_table_height = min(
        390,
        max(160, 38 + len(display) * 34),
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=resolution_table_height,
        column_config={
            "Office": st.column_config.TextColumn("Office", width=70),
            "Month": st.column_config.TextColumn("Month", width=80),
            "Total Abnormality": st.column_config.NumberColumn(
                "Total Exception Case", width=135, format="%,.0f"
            ),
            "Resolved": st.column_config.NumberColumn(
                "Resolved by CS", width=120, format="%,.0f"
            ),
            "Resolution Rate (%)": st.column_config.NumberColumn(
                "CS Resolution Rate", width=115, format="%.2f%%"
            ),
        },
    )

def chart_yvf(df: pd.DataFrame):
    """YVF booking share of Total IFF Bookings."""
    if df is None or df.empty:
        st.info("No YVF data available for selected filters.")
        return
    d = df.copy()
    d["YVF Booking"] = pd.to_numeric(d["YVF Booking"], errors="coerce").fillna(0)
    d["IFF Shipment"] = pd.to_numeric(d["IFF Shipment"], errors="coerce").fillna(0)
    d = d[(d["YVF Booking"] != 0) | (d["IFF Shipment"] != 0)].copy()
    if d.empty:
        st.info("No YVF data available for selected filters.")
        return
    pair_panel_title("YVF Booking Adoption")
    total_yvf = float(d["YVF Booking"].sum()); total_iff = float(d["IFF Shipment"].sum())
    remaining_iff = max(total_iff - total_yvf, 0.0); ratio = safe_div(total_yvf, total_iff)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["YVF Bookings", "IFF Bookings"],
                values=[total_yvf, remaining_iff],
                hole=0.58,
                sort=False,
                direction="clockwise",
                marker=dict(
                    colors=[BUSINESS_COLORS["actual"], COLORS["grid"]],
                    line=dict(color="white", width=2),
                ),
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b>"
                    "<br>Shipments: %{value:,.0f}"
                    "<br>Share: %{percent:.1%}"
                    "<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(title_text="", annotations=[dict(text=f"<b>{ratio:.1%}</b><br><span style='font-size:12px'>YVF Adoption</span><br><span style='font-size:11px'>{total_yvf:,.0f} / {total_iff:,.0f}</span>", x=0.5, y=0.5, font=dict(size=22, color=COLORS["navy"], family=UI["font_family"]), showarrow=False, align="center")])
    fig = plotly_layout(fig, 340, show_legend=True, legend_position="top", margin_left=44, margin_right=44, margin_top=34, margin_bottom=24)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_yvf_table(df: pd.DataFrame):
    """YVF detail table; no TOTAL row."""
    if df is None or df.empty:
        st.info("No YVF data available for selected filters.")
        return
    d = df.copy()
    d = d[(pd.to_numeric(d["YVF Booking"], errors="coerce").fillna(0) != 0) | (pd.to_numeric(d["IFF Shipment"], errors="coerce").fillna(0) != 0)].copy()
    if d.empty:
        st.info("No YVF data available for selected filters.")
        return
    pair_panel_title("YVF Performance by Office")
    has_month = "MonthDate" in d.columns and d["MonthDate"].notna().any()
    if has_month:
        d = d.sort_values(["MonthDate", "Office"]).copy(); d["Month"] = d["MonthDate"].dt.strftime("%b-%y")
        display = d[["Office", "Month", "YVF Booking", "IFF Shipment", "YVF Booking Ratio"]].copy()
    else:
        display = d[["Office", "YVF Booking", "IFF Shipment", "YVF Booking Ratio"]].copy().sort_values(["Office"])
    column_cfg = {
        "Office": st.column_config.TextColumn("Office", width=70),
        "YVF Booking": st.column_config.NumberColumn("Total YVF Bookings", width="medium", format="%,.0f"),
        "IFF Shipment": st.column_config.NumberColumn("Total IFF Bookings", width="medium", format="%,.0f"),
        "YVF Booking Ratio": st.column_config.NumberColumn("YVF Booking Ratio", width=110, format="%.1f%%"),
    }
    if has_month:
        column_cfg["Month"] = st.column_config.TextColumn("Month", width="small")
    display["YVF Booking Ratio"] = pd.to_numeric(
        display["YVF Booking Ratio"], errors="coerce"
    ) * 100

    yvf_table_height = min(
        390,
        max(160, 38 + len(display) * 34),
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=yvf_table_height,
        column_config=column_cfg,
    )
