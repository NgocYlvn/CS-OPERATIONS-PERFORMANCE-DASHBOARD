from __future__ import annotations

import streamlit as st
from .config import *

# IMPORTANT: CSS blocks below are preserved verbatim and in the same cascade order
# as the baseline so the rendered interface remains unchanged.

# ============================================================
# STYLE
# ============================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {COLORS['bg']};
        color: {COLORS['text']};
    }}

/* Reduce top whitespace and move dashboard content upward */
[data-testid="stMainBlockContainer"],
.block-container {{
    padding-top: 0rem !important;
    margin-top: -3.5rem !important;
}}

.main-header {{
    margin-top: 0 !important;
}}
    section[data-testid="stSidebar"] {{
        background: {COLORS['navy']};
    }}
    /* Sidebar: high-contrast labels, captions and controls */
    section[data-testid="stSidebar"] {{
        background: {COLORS['navy']};
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: #FFFFFF !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        border-color: #D9E2EC !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
        color: {COLORS['navy']} !important;
        fill: {COLORS['navy']} !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
        background: #FFFFFF !important;
        border-color: #D9E2EC !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section * {{
        color: {COLORS['navy']} !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
        background: #FFFFFF !important;
        color: {COLORS['navy']} !important;
        border: 1px solid #B8C7D6 !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button * {{
        color: {COLORS['navy']} !important;
        opacity: 1 !important;
    }}
    .main-header {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['border']};
        border-left: 7px solid {COLORS['blue']};
        border-radius: 14px;
        padding: 10px 16px;
        margin-bottom: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}
    .main-title {{
        color: {COLORS['navy']};
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .subtitle {{
        color: {COLORS['muted']};
        font-size: 14px;
        margin-top: 4px;
    }}
    .section-title {{
        color: {COLORS['navy']};
        font-size: 18px;
        font-weight: 800;
        margin: 22px 0 8px 0;
        border-left: 5px solid {COLORS['amber']};
        padding-left: 10px;
    }}
    .kpi-card {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 16px 14px;
        min-height: 110px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
    }}

    .hc-kpi-card {{
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 16px 16px 14px 16px;
        min-height: 190px;
        height: 190px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: center;
    }}

    .hc-kpi-card .kpi-label {{
        text-align: center;
        width: 100%;
    }}

    .hc-kpi-total {{
        color: #003B70;
        font-size: 32px;
        line-height: 1.05;
        font-weight: 850;
        margin-top: 12px;
        margin-bottom: 8px;
        text-align: center;
        width: 100%;
    }}

    .hc-detail-row {{
        display: grid;
        grid-template-columns: 1fr 1px 1fr;
        align-items: stretch;
        gap: 12px;
        margin-top: auto;
        padding-top: 12px;
        border-top: 1px solid #E5E7EB;
    }}

    .hc-detail-divider {{
        background: #E5E7EB;
        width: 1px;
    }}

    .hc-detail-item {{
        text-align: center;
    }}

    .hc-detail-label {{
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }}

    .hc-detail-value {{
        color: #003B70;
        font-size: 20px;
        line-height: 1.2;
        font-weight: 800;
        margin-top: 3px;
    }}

    .hc-variance-card {{
        justify-content: flex-start;
    }}

    .hc-variance-formula {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        margin-top: 12px;
        margin-bottom: 10px;
        text-align: center;
        width: 100%;
    }}

    .hc-variance-status {{
        display: block;
        width: 100%;
        box-sizing: border-box;
        text-align: center;
        margin-top: 0 !important;
    }}


    /* Section 2 - Shipment KPI cards */
    .shipment-kpi-card {{
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 18px 18px;
        min-height: 148px;
        height: 148px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    .shipment-kpi-label {{
        color: #64748B;
        font-size: 12px;
        font-weight: 700;
        text-transform: none;
        letter-spacing: 0.04em;
        margin-bottom: 14px;
    }}

    .shipment-kpi-value {{
        color: #003B70;
        font-size: 36px;
        line-height: 1.05;
        font-weight: 850;
    }}

    .shipment-kpi-note {{
        color: #64748B;
        font-size: 11px;
        margin-top: 10px;
    }}


    /* Section 3 - Workload by PIC */
    .pic-kpi-card {{
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 14px 14px;
        min-height: 142px;
        height: 142px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }}

    .pic-kpi-label {{
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
        text-transform: none;
        letter-spacing: 0.035em;
        line-height: 1.25;
        min-height: 30px;
    }}

    .pic-kpi-unit {{
        color: #7A8699;
        font-size: 10px;
        line-height: 1.2;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
        text-align: center;
        letter-spacing: 0.02em;
    }}

    .pic-kpi-value {{
        color: #003B70;
        font-size: 27px;
        line-height: 1.05;
        font-weight: 850;
        margin-top: 8px;
    }}

    .pic-kpi-note {{
        color: #64748B;
        font-size: 10.5px;
        margin-top: 7px;
        line-height: 1.25;
    }}

    .pic-status-card {{
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 110px;
        height: 110px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }}

    .pic-status-left {{
        min-width: 180px;
    }}

    .pic-status-title {{
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
        text-transform: none;
        letter-spacing: 0.035em;
    }}

    .pic-status-value {{
        color: #003B70;
        font-size: 30px;
        font-weight: 850;
        margin-top: 4px;
    }}

    .pic-progress-track {{
        flex: 1;
        height: 10px;
        background: #EAF3F8;
        border-radius: 999px;
        overflow: hidden;
    }}

    .pic-progress-fill {{
        height: 100%;
        border-radius: 999px;
    }}

    .workload-status-panel {{
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 110px;
        height: 110px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }}

    .workload-status-text {{
        font-size:30px ;
        font-weight: 850;
        margin-top: 8px;
    }}
    .kpi-label {{
        color: {COLORS['muted']};
        font-size: 12px;
        font-weight: 700;
        text-transform: none;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        color: {COLORS['navy']};
        font-size: 26px;
        line-height: 1.05;
        font-weight: 850;
        margin-bottom: 4px;
    }}
    .kpi-note {{
        color: {COLORS['muted']};
        font-size: 11px;
    }}
    .status-badge {{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        margin-top: 8px;
    }}
    .chart-box {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }}
    .warning-box {{
        background: #FFF7ED;
        color: #92400E;
        border: 1px solid #FED7AA;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 10px;
        font-size: 13px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['white']};
        border-radius: 10px 10px 0 0;
        border: 1px solid {COLORS['border']};
        padding: 8px 16px;
    }}
    
    /* Section 3 compact executive layout */
    .compact-workload-kpi {{
        min-height: 138px !important;
        height: 138px !important;
        padding: 16px 18px 14px 18px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}
    .compact-workload-kpi .kpi-label {{
        margin-bottom: 8px !important;
        line-height: 1.15 !important;
    }}
    .compact-workload-kpi .kpi-value {{
        margin: 2px 0 6px 0 !important;
        line-height: 1.05 !important;
    }}
    .compact-workload-kpi .kpi-note {{
        margin-top: 4px !important;
        line-height: 1.15 !important;
    }}
    .workload-util-card, .workload-status-card {{
        min-height: 94px !important;
        height: 94px !important;
        padding: 13px 16px !important;
    }}
    .workload-util-card {{
        display: grid !important;
        grid-template-columns: 175px minmax(0, 1fr) !important;
        align-items: center !important;
        column-gap: 18px !important;
    }}
    .workload-status-card {{
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}
    @media (max-width: 1100px) {{
        .workload-util-card {{
            grid-template-columns: 155px minmax(0, 1fr) !important;
            column-gap: 12px !important;
        }}
    }}

</style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# EXECUTIVE / CORPORATE UI OVERRIDES
# Shared styling layer only — business logic remains unchanged
# ============================================================

st.markdown(
    f"""
    <style>
    :root {{
        --font-main: {UI['font_family']};
        --navy: {COLORS['navy']};
        --blue: {COLORS['blue']};
        --orange: {COLORS['amber']};
        --green: {COLORS['green']};
        --red: {COLORS['red']};
        --text: {COLORS['text']};
        --muted: #667085;
        --border: #D8E1EA;
        --surface: #FFFFFF;
        --background: #F6F8FA;
        --radius: {UI['radius']}px;
    }}

    html, body, [class*="css"], .stApp,
    button, input, textarea, select {{
        font-family: var(--font-main) !important;
    }}

    .stApp {{
        background: var(--background);
        color: var(--text);
    }}

    .block-container {{
        max-width: 1680px;
        padding-top: 1.35rem !important;
        padding-left: 1.45rem !important;
        padding-right: 1.45rem !important;
        padding-bottom: 2rem !important;
    }}

    /* Header */
    .main-header {{
        border-radius: var(--radius);
        padding: 16px 20px;
        margin: 0 0 14px 0 !important;
        border: 1px solid var(--border);
        border-left: 5px solid var(--blue);
        box-shadow: 0 1px 4px rgba(16, 24, 40, 0.05);
    }}

    .main-title {{
        font-size: {UI['title_size']}px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em !important;
        color: var(--navy) !important;
    }}

    .subtitle {{
        font-size: {UI['body_size']}px !important;
        line-height: 1.45 !important;
        color: var(--muted) !important;
        margin-top: 3px !important;
    }}

    /* Section titles */
    .section-title {{
        font-size: {UI['section_title_size']}px !important;
        line-height: 1.25 !important;
        font-weight: 700 !important;
        color: var(--navy) !important;
        margin: 20px 0 10px 0 !important;
        padding: 0 0 0 10px !important;
        border-left: 4px solid var(--orange) !important;
    }}

    /* Shared card language */
    .kpi-card,
    .hc-kpi-card,
    .shipment-kpi-card,
    .pic-kpi-card,
    .pic-status-card,
    .workload-status-panel,
    .chart-box {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: 0 1px 4px rgba(16, 24, 40, 0.045) !important;
        box-sizing: border-box !important;
    }}

    .kpi-card,
    .hc-kpi-card,
    .shipment-kpi-card,
    .pic-kpi-card {{
        padding: {UI['card_padding']}px !important;
    }}

    /* KPI labels */
    .kpi-label,
    .shipment-kpi-label,
    .pic-kpi-label {{
        color: #5F6B7A !important;
        font-size: {UI['kpi_label_size']}px !important;
        line-height: 1.25 !important;
        font-weight: 600 !important;
        letter-spacing: 0.025em !important;
        text-transform: none !important;
        margin-bottom: 7px !important;
    }}

    /* KPI values */
    .kpi-value,
    .hc-kpi-total,
    .shipment-kpi-value,
    .pic-kpi-value,
    .pic-status-value {{
        color: var(--navy) !important;
        font-size: {UI['kpi_value_size']}px !important;
        line-height: 1.05 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}

    /* Notes / formulas / sources */
    .kpi-note,
    .shipment-kpi-note,
    .pic-kpi-note,
    .hc-variance-formula,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: var(--muted) !important;
        font-size: {UI['note_size']}px !important;
        line-height: 1.4 !important;
        font-weight: 400 !important;
    }}

    /* HC cards — equal structure */
    .hc-kpi-card {{
        height: 184px !important;
        min-height: 184px !important;
    }}

    .hc-detail-row {{
        margin-top: auto !important;
        padding-top: 11px !important;
        gap: 10px !important;
        border-top: 1px solid #E7ECF1 !important;
    }}

    .hc-detail-label {{
        color: var(--muted) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }}

    .hc-detail-value {{
        color: var(--navy) !important;
        font-size: 19px !important;
        font-weight: 700 !important;
    }}

    /* Office Capacity Snapshot — semantic color hierarchy */
    .hc-total-approved {{
        color: var(--navy) !important;
    }}
    .hc-total-actual {{
        color: var(--blue) !important;
    }}
    .hc-total-required {{
        color: var(--orange) !important;
    }}

    /* Shipment KPI cards */
    .shipment-kpi-card {{
        height: 132px !important;
        min-height: 132px !important;
    }}

    /* PIC KPI cards */
    .pic-kpi-card {{
        height: 140px !important;
        min-height: 140px !important;
    }}

    .pic-status-card,
    .workload-status-panel {{
        height: 104px !important;
        min-height: 104px !important;
        padding: 14px 16px !important;
    }}

    .pic-status-title {{
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--muted) !important;
        letter-spacing: 0.025em !important;
    }}

    /* Chart wrappers */
    .chart-box {{
        padding: 12px 14px 10px 14px !important;
        overflow: visible !important;
        min-width: 0 !important;
    }}

    .chart-box [data-testid="stPlotlyChart"] {{
        margin: 0 !important;
    }}

    .chart-box .js-plotly-plot,
    .chart-box .plot-container,
    .chart-box .svg-container {{
        width: 100% !important;
    }}

    /* Status */
    .status-badge {{
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 4px 9px !important;
    }}

    /* Streamlit dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }}

    /* Vertical spacing between Streamlit blocks */
    div[data-testid="stVerticalBlock"] > div {{
        gap: 0.35rem;
    }}

    /* Sidebar remains high contrast */
    section[data-testid="stSidebar"] {{
        background: var(--navy) !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: #FFFFFF !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
        background: #FFFFFF !important;
        border: 1px solid #C9D5E1 !important;
        border-radius: 8px !important;
    }}

    /* Laptop responsive behavior */
    @media (max-width: 1200px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}

        .main-title {{
            font-size: 28px !important;
        }}

        .kpi-value,
        .hc-kpi-total,
        .shipment-kpi-value,
        .pic-kpi-value,
        .pic-status-value {{
            font-size: 28px !important;
        }}

        .kpi-label,
        .shipment-kpi-label,
        .pic-kpi-label {{
            font-size: 12px !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FINAL UI/UX QUALITY OVERRIDES
# UI only — no business logic / calculation changes
# ============================================================

st.markdown(
    f"""
    <style>
    /* Management-first density and consistent vertical rhythm */
    .block-container {{
        max-width: 1680px !important;
        padding-top: 1.10rem !important;
        padding-bottom: 1.75rem !important;
    }}

    .section-title {{
        margin-top: 22px !important;
        margin-bottom: 12px !important;
    }}

    /* Standard Streamlit charts as real cards.
       Avoid raw HTML wrappers around Streamlit widgets. */
    [data-testid="stPlotlyChart"] {{
        background: #FFFFFF;
        border: 1px solid {COLORS['border']};
        border-radius: {UI['radius']}px;
        box-shadow: 0 1px 4px rgba(16, 24, 40, 0.045);
        padding: 8px 10px 4px 10px;
        box-sizing: border-box;
    }}

    [data-testid="stDataFrame"] {{
        background: #FFFFFF;
        border: 1px solid {COLORS['border']} !important;
        border-radius: {UI['radius']}px !important;
        box-shadow: 0 1px 4px rgba(16, 24, 40, 0.035);
    }}

    /* Equal KPI-card language */
    .kpi-card {{
        min-height: 124px !important;
        height: 124px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }}

    .kpi-card .kpi-label,
    .kpi-card .kpi-value,
    .kpi-card .kpi-note {{
        width: 100% !important;
        text-align: center !important;
    }}

    .kpi-label {{
        min-height: 18px;
    }}

    /* Make notes subordinate to management metrics */
    .kpi-note {{
        margin-top: 5px !important;
        line-height: 1.35 !important;
    }}

    /* Paired chart + detail-table layout */
    .paired-detail-card {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: 0 1px 4px rgba(16, 24, 40, 0.045);
        padding: 12px 12px 10px 12px;
        box-sizing: border-box;
        width: 100%;
        margin-top: 12px;
        overflow: hidden;
    }}

    .paired-detail-title {{
        color: var(--navy);
        font-size: 15px;
        line-height: 1.25;
        font-weight: 700;
        margin: 1px 0 10px 2px;
    }}

    .paired-detail-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        table-layout: fixed;
        font-family: var(--font-main);
        font-size: 11px;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
    }}

    .paired-detail-table thead th {{
        background: #F8FAFC;
        color: var(--navy);
        font-weight: 700;
        padding: 7px 7px;
        border-bottom: 1px solid #D8E1EA;
        text-align: left;
        line-height: 1.15;
    }}

    .paired-detail-table tbody td {{
        padding: 6px 7px;
        border-bottom: 1px solid #EDF1F5;
        color: var(--text);
        line-height: 1.15;
        vertical-align: middle;
        background: #FFFFFF;
    }}

    .paired-detail-table tbody tr:nth-child(even) td {{
        background: #FBFCFD;
    }}

    .paired-detail-table tbody tr:last-child td {{
        border-bottom: 0;
    }}

    .paired-detail-table .pair-rank {{
        text-align: center;
        color: #667085;
        font-variant-numeric: tabular-nums;
    }}

    .paired-detail-table .pair-number,
    .paired-detail-table .pair-share {{
        text-align: right;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }}

    .paired-detail-table td.pair-number {{
        color: var(--navy);
        font-weight: 600;
    }}

    .paired-detail-table .pair-name {{
        text-align: left;
        overflow-wrap: anywhere;
    }}

    .customer-name-cell {{
        font-size: 10.5px;
    }}

    .paired-detail-foot {{
        color: var(--muted);
        font-size: 10.5px;
        line-height: 1.3;
        margin: 7px 2px 0 2px;
    }}

    /* Compact tabs and avoid visual competition */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px !important;
        border-bottom: 1px solid {COLORS['grid']} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        padding: 7px 10px !important;
        font-size: 12px !important;
    }}

    /* Responsive laptop refinements */
    @media (max-width: 1366px) {{
        .block-container {{
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }}
        .main-title {{
            font-size: 28px !important;
        }}
        .section-title {{
            font-size: 18px !important;
        }}
        .kpi-value,
        .hc-kpi-total,
        .shipment-kpi-value,
        .pic-kpi-value,
        .pic-status-value {{
            font-size: 28px !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# YUSEN 3C-INSPIRED FINAL UI LAYER
# UI-only overrides — business logic/data/calculations unchanged.
# ============================================================

st.markdown(
    f"""
    <style>
    :root {{
        --y-primary: {YUSEN_THEME['primary']};
        --y-primary-dark: {YUSEN_THEME['primary_dark']};
        --y-secondary: {YUSEN_THEME['secondary']};
        --y-secondary-mid: {YUSEN_THEME['secondary_mid']};
        --y-secondary-light: {YUSEN_THEME['secondary_light']};
        --y-accent: {YUSEN_THEME['accent']};
        --y-bg: {YUSEN_THEME['background']};
        --y-surface: {YUSEN_THEME['surface']};
        --y-text: {YUSEN_THEME['text_primary']};
        --y-muted: {YUSEN_THEME['text_secondary']};
        --y-border: {YUSEN_THEME['border']};
        --y-grid: {YUSEN_THEME['grid']};
    }}

    html, body, .stApp, [class*="css"],
    button, input, textarea, select {{
        font-family: {UI['font_family']} !important;
    }}

    .stApp {{
        background: var(--y-bg) !important;
        color: var(--y-text) !important;
    }}

    .block-container {{
        max-width: 1680px !important;
        padding-top: 1rem !important;
        padding-left: 1.35rem !important;
        padding-right: 1.35rem !important;
        padding-bottom: 1.8rem !important;
    }}

    /* Main header */
    .main-header {{
        background: var(--y-surface) !important;
        border: 1px solid var(--y-border) !important;
        border-left: 5px solid var(--y-secondary) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,59,112,0.055) !important;
        padding: 15px 19px !important;
        margin-bottom: 12px !important;
    }}
    .main-title {{
        color: var(--y-primary) !important;
        font-size: 30px !important;
        font-weight: 750 !important;
        line-height: 1.12 !important;
        letter-spacing: -0.02em !important;
    }}

    /* Section hierarchy */
    .section-title {{
        color: var(--y-primary) !important;
        font-size: 19px !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        border-left: 4px solid var(--y-accent) !important;
        padding-left: 10px !important;
        margin: 22px 0 11px 0 !important;
    }}

    /* Cards */
    .kpi-card,
    .hc-kpi-card,
    .shipment-kpi-card,
    .pic-kpi-card,
    .pic-status-card,
    .workload-status-panel,
    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"] {{
        background: var(--y-surface) !important;
        border: 1px solid var(--y-border) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 7px rgba(0,59,112,0.045) !important;
    }}

    .kpi-label,
    .shipment-kpi-label,
    .pic-kpi-label,
    .pic-status-title {{
        color: var(--y-muted) !important;
        font-weight: 650 !important;
        letter-spacing: 0.025em !important;
    }}

    .kpi-value,
    .hc-kpi-total,
    .shipment-kpi-value,
    .pic-kpi-value,
    .pic-status-value {{
        color: var(--y-primary) !important;
        font-weight: 750 !important;
    }}

    .hc-total-approved {{ color: var(--y-primary) !important; }}
    .hc-total-actual {{ color: var(--y-secondary) !important; }}
    .hc-total-required {{ color: var(--y-accent) !important; }}

    /* Plotly cards */
    [data-testid="stPlotlyChart"] {{
        padding: 7px 9px 3px 9px !important;
        overflow: visible !important;
    }}

    /* Dataframes */
    [data-testid="stDataFrame"] {{
        overflow: hidden !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background:
            linear-gradient(180deg, var(--y-primary-dark) 0%, var(--y-primary) 100%) !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: #FFFFFF !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
        background: #FFFFFF !important;
        color: var(--y-primary) !important;
        border: 1px solid #C9D6E1 !important;
        border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
        color: var(--y-primary) !important;
        fill: var(--y-primary) !important;
    }}

    /* HOME button — guarantee contrast */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
    section[data-testid="stSidebar"] .stButton > button {{
        background: #FFFFFF !important;
        color: var(--y-primary) !important;
        border: 1px solid #D2DEE8 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button *,
    section[data-testid="stSidebar"] .stButton > button * {{
        color: var(--y-primary) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background: {YUSEN_THEME['hover']} !important;
        border-color: var(--y-secondary-mid) !important;
    }}

    /* Primary action */
    div[data-testid="stButton"] > button[kind="primary"] {{
        background: var(--y-primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--y-primary) !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        box-shadow: 0 5px 14px rgba(0,59,112,0.14) !important;
    }}
    div[data-testid="stButton"] > button[kind="primary"]:hover {{
        background: var(--y-secondary) !important;
        border-color: var(--y-secondary) !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        color: var(--y-muted) !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--y-primary) !important;
    }}

    /* Notes/captions */
    .kpi-note,
    .shipment-kpi-note,
    .pic-kpi-note,
    .hc-variance-formula,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: var(--y-muted) !important;
    }}

    @media (max-width: 1366px) {{
        .block-container {{
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
        }}
        .main-title {{ font-size: 28px !important; }}
        .section-title {{ font-size: 18px !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FINAL VISUAL POLISH OVERRIDES
# ============================================================
st.markdown(
    f"""
    <style>
    .shipment-kpi-card {{
        height: 132px !important;
        min-height: 132px !important;
    }}

    [data-testid="stDataFrame"] {{
        font-size: 12px !important;
    }}

    [data-testid="stDataFrame"] [role="columnheader"] {{
        font-weight: 650 !important;
        color: {YUSEN_THEME['primary']} !important;
    }}

    .paired-detail-title {{
        font-size: 16px !important;
        color: {YUSEN_THEME['primary']} !important;
        font-weight: 700 !important;
    }}

    .pic-progress-track {{
        height: 10px !important;
    }}

    /* Section 3 KPI alignment: equal title area and value baseline */
    .pic-kpi-card {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: center !important;
        padding-top: 18px !important;
    }}

    .pic-kpi-label {{
        width: 100% !important;
        min-height: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        line-height: 1.25 !important;
        margin: 0 0 8px 0 !important;
    }}

    .pic-kpi-value {{
        margin-top: 0 !important;
    }}

    .pic-kpi-note {{
        margin-top: 8px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HOME / SIDEBAR / HEADER POLISH — YUSEN EXECUTIVE FORMAT
# Consolidated UI layer for Sidebar + Main Header + Filter Summary + KPI hierarchy
# UI only — business logic, calculations, filters and data mappings are unchanged
# ============================================================
st.markdown(
    f"""
    <style>
    header[data-testid="stHeader"] {{
        background:transparent !important;
        height:0.35rem !important;
        min-height:0.35rem !important;
    }}

    [data-testid="stToolbar"] {{
        top:0.15rem !important;
    }}

    /* ------------------------------------------------------------
       LAPTOP-FIRST MAIN CANVAS
       ------------------------------------------------------------ */
    .block-container {{
        max-width: 1680px !important;
        padding-top: 0.10rem !important;
        padding-left: 1.05rem !important;
        padding-right: 1.05rem !important;
        padding-bottom: 1.5rem !important;
    }}

    /* ------------------------------------------------------------
       SIDEBAR — 248px clean executive navigation / filter rail
       ------------------------------------------------------------ */
    section[data-testid="stSidebar"] {{
        width: 248px !important;
        min-width: 248px !important;
        max-width: 248px !important;
        background: linear-gradient(180deg, #041532 0%, #06183F 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.07) !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        width: 248px !important;
        padding-top: 0.25rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        padding-bottom: 0.65rem !important;
    }}

    .sidebar-brand {{
        display:flex;
        align-items:center;
        gap:0;
        min-height:10px;
        height:10px;
        color:#FFFFFF;
        margin:0 0 2px 1px;
    }}

    .sidebar-brand-compact {{
        width:100%;
        justify-content:flex-start;
    }}

    .sidebar-brand-mark {{
        width:0;
        height:0;
        display:none;
        position:relative;
        display:inline-block;
        flex:0 0 32px;
    }}

    .sidebar-brand-mark::before,
    .sidebar-brand-mark::after {{
        content:"";
        position:absolute;
        left:0;
        height:3px;
        border-radius:999px;
        background:#FFFFFF;
        transform:skewX(-28deg);
    }}
    .sidebar-brand-mark::before {{ width:33px; top:4px; }}
    .sidebar-brand-mark::after {{ width:26px; top:13px; left:6px; }}

    /* HOME */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        min-height:41px !important;
        height:41px !important;
        background:#FFFFFF !important;
        color:#06183F !important;
        border:1px solid #D5E1EA !important;
        border-radius:9px !important;
        font-size:13px !important;
        font-weight:700 !important;
        box-shadow:0 3px 10px rgba(0,0,0,0.09) !important;
        margin:0 0 10px 0 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button *,
    section[data-testid="stSidebar"] .stButton > button * {{
        color:#06183F !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        color:#E6761B !important;
        border-color:#E6761B !important;
        background:#FFFFFF !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover * {{
        color:#E6761B !important;
    }}

    /* FILTERS heading */
    .sidebar-filter-title {{
        display:flex;
        align-items:center;
        gap:7px;
        color:#FFFFFF;
        font-size:15px;
        line-height:1.2;
        font-weight:800;
        margin:3px 0 8px 0;
        letter-spacing:0.01em;
    }}

    .sidebar-filter-title::after {{
        content:"";
        width:20px;
        height:2px;
        border-radius:999px;
        background:#E6761B;
        display:block;
    }}

    .sidebar-filter-caption {{
        display:none !important;
        color:#D5EAF8;
        font-size:11.5px;
        line-height:1.3;
        font-weight:500;
        margin:0 0 11px 0;
    }}

    /* Field labels */
    section[data-testid="stSidebar"] label {{
        color:#FFFFFF !important;
        font-size:12.5px !important;
        line-height:1.25 !important;
        font-weight:700 !important;
        letter-spacing:0.015em !important;
        margin-bottom:5px !important;
    }}

    /* Select boxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        min-height:41px !important;
        height:41px !important;
        background:#FFFFFF !important;
        border:1px solid #D5E1EA !important;
        border-radius:9px !important;
        box-shadow:none !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        color:#06183F !important;
        font-size:13.5px !important;
        font-weight:500 !important;
        opacity:1 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
        color:#06183F !important;
        fill:#06183F !important;
        opacity:1 !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] {{
        margin-bottom:0.28rem !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border:0 !important;
        border-top:1px solid rgba(213,234,248,0.20) !important;
        margin:10px 0 9px 0 !important;
    }}

    /* Upload — compact white card */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        margin-top:1px !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
        min-height:78px !important;
        background:#FFFFFF !important;
        border:1px solid #D5E1EA !important;
        border-radius:9px !important;
        padding:6px 8px !important;
        box-shadow:0 2px 9px rgba(0,0,0,0.07) !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section * {{
        color:#06183F !important;
        opacity:1 !important;
        font-size:11.5px !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
        background:#FFFFFF !important;
        color:#06183F !important;
        border:1px solid #B9CAD8 !important;
        border-radius:8px !important;
        font-size:12px !important;
        font-weight:650 !important;
        min-height:34px !important;
    }}

    /* Sidebar footer — compact application metadata */
    .sidebar-footer {{
        margin-top:14px;
        padding-top:10px;
        border-top:1px solid rgba(255,255,255,0.16);
        display:flex;
        align-items:center;
        justify-content:center;
        gap:4px;
        white-space:nowrap;
        color:rgba(255,255,255,0.72);
        font-size:8.7px;
        line-height:1.25;
        font-weight:500;
        letter-spacing:-0.01em;
    }}
    .sidebar-footer .footer-sep {{
        color:#E6761B;
        opacity:0.95;
        font-weight:700;
    }}

    /* ------------------------------------------------------------
       MAIN HEADER — compact executive card
       ------------------------------------------------------------ */
    .main-header {{
        position:relative !important;
        overflow:hidden !important;
        background:rgba(255,255,255,0.985) !important;
        backdrop-filter:blur(8px);
        -webkit-backdrop-filter:blur(8px);
        border:1px solid #D5E1EA !important;
        border-left:5px solid #0DBAEE !important;
        border-radius:11px !important;
        padding:9px 14px 8px 14px !important;
        margin:0 !important;
        box-shadow:0 4px 14px rgba(6,24,63,0.08) !important;
    }}

    /* Make the Streamlit element wrapper sticky, not the inner HTML.
       This avoids clipping/stacking issues on Streamlit Cloud. */
    div[data-testid="stVerticalBlock"] > div:has(.main-header) {{
        position:sticky !important;
        top:0.10rem !important;
        z-index:1000 !important;
        background:{COLORS['bg']} !important;
        padding-top:0.15rem !important;
        padding-bottom:0.30rem !important;
    }}

    /* Remove the old decorative arrow to preserve laptop width. */
    .main-header::after {{
        content:none !important;
        display:none !important;
    }}

    .main-title {{
        color:#06183F !important;
        font-size:28px !important;
        line-height:1.06 !important;
        font-weight:800 !important;
        letter-spacing:-0.025em !important;
        padding-right:0 !important;
        margin:0 !important;
    }}

    .subtitle {{
        color:#5B6575 !important;
        font-size:12.5px !important;
        line-height:1.25 !important;
        font-weight:450 !important;
        margin-top:2px !important;
    }}

    /* ------------------------------------------------------------
       SELECTED FILTER SUMMARY
       ------------------------------------------------------------ */
    .filter-summary-card {{
        display:flex;
        align-items:center;
        min-height:40px;
        gap:0;
        background:#F8FBFE;
        border:1px solid #E0E7EE;
        border-radius:8px;
        box-shadow:none;
        margin:6px 0 0 0;
        padding:3px 9px;
    }}

    .filter-summary-item {{
        display:grid;
        grid-template-columns:30px minmax(0,1fr);
        grid-template-rows:auto auto;
        column-gap:8px;
        align-items:center;
        min-width:185px;
        padding:0 16px 0 0;
        margin-right:16px;
        border-right:1px solid #E4EBF1;
    }}

    .filter-summary-item:last-child {{
        border-right:0;
        margin-right:0;
    }}

    .filter-summary-icon {{
        grid-row:1 / span 2;
        width:25px;
        height:25px;
        border-radius:7px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#06183F;
        background:#EEF7FC;
        border:1px solid #D5EAF8;
    }}

    .filter-summary-icon svg {{
        width:16px;
        height:16px;
        fill:none;
        stroke:currentColor;
        stroke-width:1.8;
        stroke-linecap:round;
        stroke-linejoin:round;
    }}

    .filter-summary-label {{
        color:#5B6575;
        font-size:11.5px;
        line-height:1.2;
        font-weight:600;
        margin:0;
    }}

    .filter-summary-value {{
        color:#06183F;
        font-size:13.5px;
        line-height:1.2;
        font-weight:750;
        margin-top:1px;
    }}

    /* ------------------------------------------------------------
       SECTION HIERARCHY
       ------------------------------------------------------------ */
    .section-title {{
        color:#06183F !important;
        font-size:19px !important;
        line-height:1.22 !important;
        font-weight:800 !important;
        border-left:4px solid #E6761B !important;
        padding-left:9px !important;
        margin:18px 0 9px 0 !important;
    }}


    /* ------------------------------------------------------------
       KPI ICON SYSTEM — clean executive layout
       Icons are concentrated in HC KPI cards and filter summary
       ------------------------------------------------------------ */
    .kpi-icon-circle {{
        width:44px;
        height:44px;
        min-width:44px;
        border-radius:50%;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        flex:0 0 44px;
    }}

    .kpi-icon-circle svg {{
        width:23px;
        height:23px;
        fill:none;
        stroke:currentColor;
        stroke-width:1.8;
        stroke-linecap:round;
        stroke-linejoin:round;
    }}

    .hc-main-row {{
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        width:100%;
        margin:7px 0 5px 0;
    }}

    .hc-main-row .hc-kpi-total {{
        width:auto !important;
        margin:0 !important;
        text-align:left !important;
    }}



    /* ------------------------------------------------------------
       KPI / CARD HIERARCHY
       ------------------------------------------------------------ */
    .kpi-card,
    .hc-kpi-card,
    .shipment-kpi-card,
    .pic-kpi-card,
    .pic-status-card,
    .workload-status-panel,
    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"] {{
        background:#FFFFFF !important;
        border:1px solid #D5E1EA !important;
        border-radius:11px !important;
        box-shadow:0 2px 7px rgba(6,24,63,0.035) !important;
    }}

    .kpi-label,
    .shipment-kpi-label,
    .pic-kpi-label {{
        color:#5B6575 !important;
        font-size:13px !important;
        line-height:1.22 !important;
        font-weight:650 !important;
        letter-spacing:0.015em !important;
        text-transform:none !important;
    }}

    .kpi-value,
    .hc-kpi-total,
    .shipment-kpi-value,
    .pic-kpi-value,
    .pic-status-value {{
        font-size:32px !important;
        line-height:1.04 !important;
        font-weight:780 !important;
        letter-spacing:-0.02em !important;
    }}

    /* Section 1 HC cards — compact but fully readable */
    .hc-kpi-card {{
        height:158px !important;
        min-height:158px !important;
        padding:14px 14px 12px 14px !important;
    }}

    .hc-kpi-total {{
        margin-top:8px !important;
        margin-bottom:5px !important;
    }}

    .hc-detail-row {{
        padding-top:9px !important;
        gap:8px !important;
    }}

    .hc-detail-label {{
        font-size:11.5px !important;
        font-weight:650 !important;
    }}

    .hc-detail-value {{
        font-size:19px !important;
        font-weight:750 !important;
        margin-top:2px !important;
    }}

    .hc-variance-formula {{
        font-size:11.5px !important;
        line-height:1.25 !important;
        margin-top:7px !important;
        margin-bottom:6px !important;
    }}

    .status-badge {{
        font-size:11.5px !important;
        line-height:1.2 !important;
        font-weight:750 !important;
    }}

    /* Other KPI cards */
    .shipment-kpi-card {{
        height:124px !important;
        min-height:124px !important;
        padding:14px 14px !important;
    }}

    .pic-kpi-card {{
        height:136px !important;
        min-height:136px !important;
        padding:15px 14px 13px 14px !important;
    }}

    .pic-kpi-label {{
        min-height:34px !important;
        height:34px !important;
        font-size:13px !important;
        margin:0 0 6px 0 !important;
    }}

    .pic-kpi-note,
    .kpi-note,
    .shipment-kpi-note {{
        font-size:11px !important;
        line-height:1.3 !important;
    }}


    /* FTE Workload Status — align status text with adjacent KPI value */
    .workload-status-text {{
        font-size:32px !important;
        line-height:1.05 !important;
        font-weight:800 !important;
        padding:7px 18px !important;
        min-width:180px;
        text-align:center;
        margin-top:8px !important;
    }}

    @media (max-width:1366px) {{
        .workload-status-text {{
            font-size:28px !important;
            padding:6px 16px !important;
            min-width:165px;
        }}
    }}

    /* ------------------------------------------------------------
       TABLE READABILITY
       ------------------------------------------------------------ */
    .paired-detail-table {{
        font-size:12px !important;
    }}

    .paired-detail-table thead th {{
        font-size:12px !important;
        font-weight:700 !important;
        padding:7px 7px !important;
    }}

    .paired-detail-table tbody td {{
        font-size:12px !important;
        padding:6px 7px !important;
    }}

    .customer-name-cell {{
        font-size:11.5px !important;
    }}

    .paired-detail-foot {{
        font-size:11px !important;
    }}

    [data-testid="stDataFrame"] {{
        font-size:12px !important;
    }}

    /* ------------------------------------------------------------
       PLOTLY / CHART CARD DENSITY
       ------------------------------------------------------------ */
    [data-testid="stPlotlyChart"] {{
        padding:6px 8px 3px 8px !important;
    }}

    /* ------------------------------------------------------------
       LAPTOP 1366 × 768
       Reduce whitespace, not core readability.
       ------------------------------------------------------------ */
    @media (max-width:1366px) {{
        .kpi-icon-circle {{
            width:42px;
            height:42px;
            min-width:42px;
            flex-basis:42px;
        }}
        .kpi-icon-circle svg {{
            width:22px;
            height:22px;
        }}
        .hc-main-row {{
            gap:8px;
            margin:5px 0 4px 0;
        }}

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div:first-child {{
            width:260px !important;
            min-width:260px !important;
            max-width:260px !important;
        }}

        .block-container {{
            padding-top:0.25rem !important;
            padding-left:0.80rem !important;
            padding-right:0.80rem !important;
            padding-bottom:1.25rem !important;
        }}

        .main-header {{
            padding:8px 12px 7px 12px !important;
        }}
        div[data-testid="stVerticalBlock"] > div:has(.main-header) {{
            top:0.05rem !important;
        }}

        .main-title {{
            font-size:27px !important;
        }}

        .subtitle {{
            font-size:12px !important;
        }}

        .filter-summary-card {{
            min-height:50px !important;
            padding:6px 12px !important;
            margin-bottom:10px !important;
        }}

        .filter-summary-item {{
            min-width:185px !important;
            padding-right:18px !important;
            margin-right:18px !important;
        }}

        .section-title {{
            font-size:18px !important;
            margin-top:16px !important;
            margin-bottom:8px !important;
        }}

        .hc-kpi-card {{
            height:150px !important;
            min-height:150px !important;
            padding:12px 12px 10px 12px !important;
        }}

        .kpi-value,
        .hc-kpi-total,
        .shipment-kpi-value,
        .pic-kpi-value,
        .pic-status-value {{
            font-size:30px !important;
        }}

        .kpi-label,
        .shipment-kpi-label,
        .pic-kpi-label {{
            font-size:12.5px !important;
        }}

        .shipment-kpi-card {{
            height:118px !important;
            min-height:118px !important;
        }}

        .pic-kpi-card {{
            height:130px !important;
            min-height:130px !important;
        }}
    }}

    @media (max-width:1100px) {{
        .filter-summary-card {{
            flex-wrap:wrap;
            gap:7px 0;
        }}
        .filter-summary-item {{
            min-width:165px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# OFFICE COMPARISON UI — ALL OFFICES ONLY
# UI layer only; KPI formulas / filters / business logic unchanged
# ============================================================
st.markdown(
    f"""
    <style>
    .office-comparison-heading {{
        display:flex; align-items:center; gap:8px; color:#06183F;
        font-size:15px; line-height:1.2; font-weight:750;
        margin:10px 0 8px 1px;
    }}
    .office-comparison-heading::before {{
        content:""; width:22px; height:3px; border-radius:999px;
        background:#E6761B; display:inline-block;
    }}
    .office-compare-card {{
        --office-status:#3F5B81; --office-status-bg:#EEF3F8;
        position:relative; background:#FFFFFF; border:1px solid #D5E1EA;
        border-top:4px solid var(--office-status); border-radius:11px;
        min-height:154px; padding:11px 12px 10px 12px; box-sizing:border-box;
        box-shadow:0 2px 7px rgba(6,24,63,0.035); overflow:hidden;
    }}
    .office-compare-top {{
        display:flex; align-items:center; justify-content:space-between;
        gap:8px; margin-bottom:9px;
    }}
    .office-compare-name {{
        color:#06183F; font-size:18px; line-height:1; font-weight:800;
    }}
    .office-compare-status {{
        display:inline-flex; align-items:center; justify-content:center;
        max-width:125px; min-height:24px; padding:3px 9px; border-radius:999px;
        background:var(--office-status-bg); color:var(--office-status);
        font-size:10.5px; line-height:1.1; font-weight:800; white-space:nowrap;
    }}
    .office-compare-primary {{
        display:flex; align-items:baseline; justify-content:space-between;
        gap:10px; padding-bottom:8px; margin-bottom:7px;
        border-bottom:1px solid #E8EEF3;
    }}
    .office-compare-primary-label {{
        color:#667085; font-size:10.5px; line-height:1.15; font-weight:600;
    }}
    .office-compare-primary-value {{
        color:#06183F; font-size:24px; line-height:1; font-weight:800;
        letter-spacing:-0.02em; white-space:nowrap;
    }}
    .office-compare-grid {{
        display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px 10px;
    }}
    .office-compare-metric {{ min-width:0; }}
    .office-compare-metric-label {{
        color:#7A8699; font-size:9.8px; line-height:1.15; font-weight:600;
        margin-bottom:2px; white-space:nowrap;
    }}
    .office-compare-metric-value {{
        color:#06183F; font-size:14px; line-height:1.15; font-weight:750;
        font-variant-numeric:tabular-nums; white-space:nowrap;
    }}
    .office-compare-metric-value.negative {{ color:#D92D20; }}
    .office-compare-metric-value.positive {{ color:#6EA52B; }}
    @media (max-width:1366px) {{
        .office-compare-card {{ min-height:146px; padding:10px 10px 9px 10px; }}
        .office-compare-name {{ font-size:17px; }}
        .office-compare-primary-value {{ font-size:22px; }}
        .office-compare-status {{ font-size:9.8px; padding:3px 7px; }}
        .office-compare-metric-label {{ font-size:9.3px; }}
        .office-compare-metric-value {{ font-size:13px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS



# ============================================================
# SIDEBAR MICRO-POLISH FINAL
# UI ONLY — no changes to filters, upload logic, session state,
# calculations, charts, or main dashboard layout.
# ============================================================
st.markdown(
    """
    <style>
    /* Sidebar only */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.35rem !important;
        padding-left: 0.90rem !important;
        padding-right: 0.90rem !important;
        padding-bottom: 0.80rem !important;
    }

    /* HOME: lower height and tighter spacing */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        min-height: 41px !important;
        height: 41px !important;
        margin: 0 0 9px 0 !important;
        border-radius: 8px !important;
        font-size: 12.5px !important;
    }

    /* FILTERS block */
    .sidebar-filter-title {
        margin: 3px 0 1px 0 !important;
        font-size: 16px !important;
        gap: 7px !important;
    }

    .sidebar-filter-title::after {
        width: 20px !important;
        height: 2px !important;
    }

    .sidebar-filter-caption {
        display: none !important;
    }

    /* Labels */
    section[data-testid="stSidebar"] label {
        font-size: 12px !important;
        margin-bottom: 4px !important;
    }

    /* Select boxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        min-height: 41px !important;
        height: 41px !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin-bottom: 0.20rem !important;
    }

    /* Divider */
    section[data-testid="stSidebar"] hr {
        margin: 9px 0 9px 0 !important;
    }

    /* Upload title */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        margin-top: 0 !important;
    }

    /* Compact upload card */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        min-height: 78px !important;
        padding: 7px 8px !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section * {
        font-size: 10.8px !important;
        line-height: 1.25 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        min-height: 32px !important;
        height: 32px !important;
        padding: 0 12px !important;
        border-radius: 7px !important;
        font-size: 11.5px !important;
    }

    /* Remove visual clutter from uploader help icon where possible */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stTooltipIcon"] {
        opacity: 0.55 !important;
        transform: scale(0.88);
    }

    /* Footer */
    .sidebar-footer {
        margin-top: 12px !important;
        padding-top: 10px !important;
        font-size: 10px !important;
        line-height: 1.25 !important;
        gap: 4px !important;
    }

    /* Laptop */
    @media (max-width:1366px) {
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0.28rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            min-height: 40px !important;
            height: 40px !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            min-height: 40px !important;
            height: 40px !important;
        }

        .sidebar-footer {
            font-size: 9.8px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR POSITIONING FINAL — UI ONLY
# HOME icon / filter breathing room / lower upload & footer
# ============================================================
st.markdown(
    """
    <style>
    /* Give FILTERS a little more breathing room before MONTH */
    .sidebar-filter-spacer {
        height: 14px !important;
        min-height: 14px !important;
    }

    /* Push Upload + Version area lower on normal laptop screens.
       This is visual spacing only; upload/filter logic is unchanged. */
    .sidebar-bottom-anchor {
        height: clamp(150px, 28vh, 360px) !important;
        min-height: 150px !important;
    }

    /* Keep the lower block visually compact once it reaches the bottom area */
    section[data-testid="stSidebar"] hr {
        margin-top: 8px !important;
        margin-bottom: 12px !important;
    }

    .sidebar-footer {
        margin-top: 26px !important;
        padding-top: 12px !important;
    }

    /* On shorter screens, reduce the spacer automatically to avoid clipping */
    @media (max-height: 760px) {
        .sidebar-bottom-anchor {
            height: 95px !important;
            min-height: 95px !important;
        }
        .sidebar-footer {
            margin-top: 20px !important;
        }
    }

    @media (max-height: 650px) {
        .sidebar-bottom-anchor {
            height: 48px !important;
            min-height: 48px !important;
        }
        .sidebar-footer {
            margin-top: 14px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
