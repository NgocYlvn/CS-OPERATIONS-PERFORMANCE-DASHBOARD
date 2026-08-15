from __future__ import annotations

import streamlit as st

# Keep Streamlit page configuration identical to the baseline.
st.set_page_config(
    page_title="CS OPERATIONS PERFORMANCE DASHBOARD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importing styles applies the exact original CSS cascade before main() executes.
from dashboard import styles as _styles  # noqa: F401,E402
from dashboard.main_logic import main  # noqa: E402

if __name__ == "__main__":
    main()
