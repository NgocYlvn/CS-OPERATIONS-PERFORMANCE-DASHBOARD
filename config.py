from __future__ import annotations

# Centralized configuration only. Values are preserved from the baseline.

APP_TITLE = "CS OPERATIONS PERFORMANCE DASHBOARD"
APP_SUBTITLE = "Capacity • Workload • Utilization • Performance"
DEFAULT_FILE = "(Not for Office Input) MASTER DATA SOURCE.xlsm"
CAPACITY_HOURS_PER_FTE = 8 * 0.95 * 22  # 167.2 hours/FTE/month
STANDARD_OFFICES = ["HAN", "HAD", "HLC", "HCM"]
SERVICE_ORDER = ["AE", "AI", "OE", "OI", "CC", "TR", "WH"]
SERVICE_LABELS = {
    "AE": "Air Export",
    "AI": "Air Import",
    "OE": "Ocean Export",
    "OI": "Ocean Import",
    "CC": "Customs Clearance",
    "TR": "Trucking",
    "WH": "Warehouse",
}

# ============================================================
# YUSEN 3C-INSPIRED CORPORATE COLOR SYSTEM
# Visual reference: Yusen Logistics corporate web presence.
# These HEX values are used as a consistent dashboard design system and
# are NOT asserted here as official corporate-brand specifications.
# ============================================================
YUSEN_THEME = {
    "primary": "#06183F",          # Yusen Navy - primary
    "primary_dark": "#041532",     # deeper navy for sidebar gradient
    "secondary": "#0DBAEE",        # Yusen Cyan - supporting/data series
    "secondary_mid": "#3F5B81",    # Mid Blue
    "secondary_light": "#D5EAF8",  # Light Blue
    "secondary_pale": "#EEF7FC",
    "accent": "#E6761B",           # Yusen Orange - accent/attention
    "accent_pale": "#FFF2E8",
    "background": "#F6F8FB",
    "surface": "#FFFFFF",
    "text_primary": "#06183F",
    "text_secondary": "#5B6575",
    "border": "#D5E1EA",
    "grid": "#E8EEF3",
    "hover": "#F3F7FA",
}

COLORS = {
    "navy": YUSEN_THEME["primary"],
    "blue": YUSEN_THEME["secondary"],
    "light_blue": YUSEN_THEME["secondary_pale"],
    "red": "#D92D20",
    "green": "#95C947",
    "amber": YUSEN_THEME["accent"],
    "gray": "#98A2B3",
    "gray_dark": YUSEN_THEME["text_secondary"],
    "grid": YUSEN_THEME["grid"],
    "bg": YUSEN_THEME["background"],
    "white": YUSEN_THEME["surface"],
    "text": YUSEN_THEME["text_primary"],
    "muted": YUSEN_THEME["text_secondary"],
    "border": YUSEN_THEME["border"],
}

# Business-meaning color map.
# UI only: Same Business Meaning = Same Color Everywhere.
BUSINESS_COLORS = {
    "actual": COLORS["blue"],
    "approved": COLORS["navy"],
    "required": COLORS["amber"],
    "positive": COLORS["green"],
    "negative": COLORS["red"],
    "critical": COLORS["red"],
    "supporting": YUSEN_THEME["secondary_light"],
}


# ============================================================
# SHARED EXECUTIVE UI CONSTANTS
# UI only — no business logic / calculation changes
# ============================================================

UI = {
    "font_family": "Inter, 'Segoe UI', Arial, sans-serif",
    "title_size": 30,
    "section_title_size": 19,
    "chart_title_size": 17,
    "kpi_value_size": 32,
    "kpi_label_size": 13,
    "body_size": 12,
    "axis_size": 11,
    "note_size": 11,
    "radius": 12,
    "card_padding": 16,
    "section_gap": 18,
    "chart_height": 380,
    "chart_height_tall": 520,
}

# Shared height for Shipment Volume chart/detail pairs
SHIPMENT_PAIR_HEIGHT = 500

CORPORATE_PALETTE = [
    YUSEN_THEME["secondary"],
    YUSEN_THEME["primary"],
    "#2E73AA",
    "#5D91BC",
    "#8EB7D8",
    "#B7D0E3",
    YUSEN_THEME["accent"],
]

SHEET_NAMES = {
    "hc": " 1.  Office Cap. & Workload",
    "resolution": "9. CS Resolutions Rate",
    "workload": "4. Workload by Activity",
    "yvf": "10. YVF",
    "shipment": "3. Active Cus - Vol.",
    "customer_ns": "11. Vol. by Customer",

    # The new master workbook no longer keeps separate office-specific customer sheets.
    # Keep these aliases intentionally unmatched so prepare_customer() falls back to
    # the combined Customer Volume-N&S sheet without changing downstream logic.
    "customer_had": "__NOT_USED_CUSTOMER_HAD__",
    "customer_han": "__NOT_USED_CUSTOMER_HAN__",
    "customer_hlc": "__NOT_USED_CUSTOMER_HLC__",
    "customer_hcm": "__NOT_USED_CUSTOMER_HCM__",

    "fte": " 2. FTE Workload",
    "core": "5. C Vol.",
    "ancillary": "6. A Vol.",
    "supporting": "7. S Vol.",
    "exception": "8. E Vol.",

    # The new master workbook does not contain the former "Ghi chú" sheet.
    # Existing downstream fallback behavior is retained.
    "notes": "__NOT_USED_NOTES__",
}
