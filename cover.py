from __future__ import annotations

import streamlit as st

def render_cover_page() -> None:
    """Render the approved corporate cover page."""

    cover_css = """
<style>
section[data-testid="stSidebar"]{display:none!important}
[data-testid="stSidebarCollapsedControl"]{display:none!important}
header[data-testid="stHeader"]{display:none!important;height:0!important}
[data-testid="stToolbar"]{display:none!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stStatusWidget"]{display:none!important}
#MainMenu{visibility:hidden!important}
[data-testid="stAppViewContainer"]{height:100dvh!important;overflow:hidden!important;padding:0!important;margin:0!important}
[data-testid="stAppViewBlockContainer"]{height:100dvh!important;overflow:hidden!important;padding:0!important;margin:0!important}
.main{height:100dvh!important;overflow:hidden!important;padding:0!important;margin:0!important}
footer{display:none!important}
.block-container{max-width:none!important;width:100%!important;padding:0!important;margin:0!important}
.stApp{background:#06183F!important;height:100dvh!important;min-height:0!important;overflow:hidden!important}

.cover-stage{
    position:fixed;
    inset:0;
    width:100vw;
    height:100dvh;
    min-height:0;
    overflow:hidden;
    z-index:999;
    background:linear-gradient(135deg,#031532 0%,#06183F 48%,#082759 100%);
    font-family:Inter,"Segoe UI",Arial,sans-serif;
}

.cover-panel{
    position:absolute;
    top:10px;
    bottom:14px;
    left:1.2vw;
    width:74vw;
    max-width:none;
    min-width:760px;
    height:auto;
    min-height:0;
    box-sizing:border-box;
    padding:22px 44px 24px;
    border-radius:24px;
    background:linear-gradient(145deg,#FFFFFF 0%,#FCFDFE 100%);
    border:1px solid rgba(255,255,255,.72);
    box-shadow:0 18px 42px rgba(0,0,0,.18);
    z-index:10;
}

.cover-logo-real{
    width:192px;
    height:auto;
    display:block;
    margin:0 0 clamp(12px,1.7vh,20px) 0;
}

.cover-title{
    margin:0;
    max-width:650px;
    color:#06183F;
    font-size:clamp(46px,3.65vw,66px);
    line-height:.98;
    letter-spacing:-.035em;
    font-weight:850;
    text-transform:uppercase;
}

.cover-title-accent{
    width:100%;
    max-width:100%;
    height:5px;
    border-radius:999px;
    background:#E6761B;
    margin:clamp(14px,2.2vh,22px) 0 clamp(10px,1.6vh,16px) 2px;
}

.cover-subtitle{
    color:#4F5B6A;
    font-size:clamp(18px,1.45vw,23px);
    line-height:1.24;
    font-weight:500;
    max-width:440px;
    margin-bottom:clamp(12px,1.8vh,20px);
}

.cover-separator{
    height:1px;
    background:#D8E1EA;
    margin:0 0 clamp(12px,1.8vh,18px);
}

.cover-pillars{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:0;
    margin-top:38px;
    padding:10px 12px 0;
}

.cover-pillar{
    position:relative;
    text-align:center;
    padding:0 22px;
}

.cover-pillar:not(:last-child)::after{
    content:"";
    position:absolute;
    right:0;
    top:48px;
    width:1px;
    height:92px;
    background:#DDE5EC;
}

.cover-icon{
    width:72px;
    height:72px;
    margin:0 auto 12px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#fff;
    box-shadow:0 5px 14px rgba(0,0,0,.10);
}

.cover-icon svg{
    width:39px;
    height:39px;
    stroke:currentColor;
    fill:none;
    stroke-width:1.9;
    stroke-linecap:round;
    stroke-linejoin:round;
}

.icon-capacity{background:#06183F}
.icon-workload{background:#0DBAEE}
.icon-productivity{background:#F57C00}
.icon-insights{background:#45B84A}

.cover-pillar-title{
    color:#06183F;
    font-size:16px;
    font-weight:800;
    line-height:1.18;
    text-transform:uppercase;
    margin-bottom:9px;
}

.cover-pillar-note{
    color:#4F5B6A;
    font-size:14px;
    line-height:1.40;
    font-weight:500;
}

.cover-cta{
    position:absolute;
    left:36px;
    bottom:32px;
    display:inline-flex;
    align-items:center;
    justify-content:space-between;
    gap:18px;
    min-width:300px;
    height:52px;
    padding:0 20px;
    box-sizing:border-box;
    border-radius:9px;
    background:linear-gradient(180deg,#FF7F0A 0%,#EE6500 100%);
    color:#fff!important;
    text-decoration:none!important;
    font-size:20px;
    font-weight:800;
    box-shadow:0 8px 18px rgba(230,118,27,.28);
}

.cover-cta-icon{
    width:30px;
    height:30px;
    border:2px solid rgba(255,255,255,.9);
    border-radius:4px;
    display:flex;
    align-items:center;
    justify-content:center;
    flex:0 0 30px;
}

.cover-cta-arrow{
    font-size:34px;
    line-height:1;
    margin-left:auto;
    font-weight:300;
}

/* SVG arc field based on the approved reference */
.cover-arc-svg{
    position:absolute;
    right:0;
    top:0;
    width:55vw;
    height:100dvh;
    z-index:2;
    pointer-events:none;
    overflow:visible;
}

.cover-right-footer{
    position:absolute;
    right:28px;
    bottom:24px;
    display:flex;
    align-items:center;
    gap:11px;
    color:#06183F;
    font-size:13px;
    font-weight:700;
    z-index:12;
    white-space:nowrap;
}

.cover-headset{
    width:30px;
    height:30px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#06183F;
}

.cover-headset svg{
    width:28px;
    height:28px;
    stroke:currentColor;
    fill:none;
    stroke-width:1.8;
}

.footer-divider{
    width:1.5px;
    height:22px;
    background:#E6761B;
}

.cover-wave-1,.cover-wave-2,.cover-wave-3{
    position:absolute;
    left:-5%;
    width:112%;
    border-radius:50%;
    pointer-events:none;
}

.cover-wave-1{
    height:90px;
    bottom:-58px;
    border-top:9px solid #0DBAEE;
    transform:rotate(-1.5deg);
    opacity:.96;
}

.cover-wave-2{
    height:125px;
    bottom:-88px;
    border-top:7px solid #E6761B;
    transform:rotate(1.7deg);
    opacity:.98;
}

.cover-wave-3{
    height:155px;
    bottom:-113px;
    border-top:8px solid #005BAC;
    transform:rotate(-.2deg);
    opacity:.86;
}


@media(max-height:820px) and (min-width:901px){
    .cover-panel{top:8px;bottom:10px;padding:18px 40px 18px;width:74vw;min-width:760px}
    .cover-logo-real{width:176px;margin-bottom:11px}
    .cover-title{font-size:clamp(44px,3.3vw,60px)}
    .cover-title-accent{margin:14px 0 11px 2px}
    .cover-subtitle{font-size:19px;margin-bottom:12px}
    .cover-separator{margin-bottom:12px}
    .cover-icon{width:64px;height:64px}
    .cover-icon svg{width:35px;height:35px}
    .cover-pillar-title{font-size:14px;margin-bottom:7px}
    .cover-pillar-note{font-size:12.5px;line-height:1.38}
    .cover-pillars{margin-top:30px;padding:8px 8px 0}
    .cover-pillar{padding:0 16px}
    .cover-pillar:not(:last-child)::after{top:42px;height:84px}
    .cover-cta{bottom:26px;height:50px;min-width:300px;font-size:19px}
    .cover-right-footer{right:24px;bottom:26px;font-size:12px}
}

@media(max-width:900px){
    .cover-stage{min-height:920px}
    .cover-panel{
        position:relative;
        top:auto;
        left:auto;
        width:calc(100% - 28px);
        min-width:0;
        height:auto;
        min-height:830px;
        margin:14px;
        padding:28px 24px 110px;
    }
    .cover-title{font-size:46px}
    .cover-pillars{grid-template-columns:repeat(2,1fr);row-gap:20px}
    .cover-pillar:nth-child(2)::after{display:none}
    .cover-cta{left:24px;right:24px;width:auto;bottom:28px}
    .cover-arc-svg,.cover-wave-1,.cover-wave-2,.cover-wave-3{display:none}.cover-right-footer{right:20px;bottom:18px;font-size:11px;gap:8px}
}

    /* ===== FINAL OVERRIDE: FTE WORKLOAD STATUS ===== */
    .workload-status-text,
    .status-badge {
        font-size: 28px !important;
        line-height: 1.05 !important;
        font-weight: 800 !important;
        min-height: 44px !important;
        padding: 6px 20px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        border-radius: 999px !important;
        letter-spacing: 0 !important;
    }

    @media (max-width: 1366px) {
        .workload-status-text,
        .status-badge {
            font-size: 26px !important;
            min-height: 42px !important;
            padding: 5px 18px !important;
        }
    }

</style>
"""

    cover_html = """<div class="cover-stage">
<svg class="cover-arc-svg" viewBox="0 0 900 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <path d="M560 -60 C690 120 700 300 610 470 C550 585 445 675 330 735" fill="none" stroke="#F58220" stroke-width="2.2"/>
  <path d="M640 -45 C760 130 770 320 685 495 C625 620 525 710 415 775" fill="none" stroke="#F58220" stroke-width="2.2"/>
  <path d="M715 -28 C825 145 838 345 758 525 C700 655 610 752 500 820" fill="none" stroke="#F58220" stroke-width="2.2"/>
  <path d="M785 -10 C885 165 900 375 825 555 C772 685 690 785 585 855" fill="none" stroke="#F58220" stroke-width="2.2"/>
  <path d="M850 12 C940 190 958 405 890 585 C842 710 765 815 670 885" fill="none" stroke="#F58220" stroke-width="2.2"/>
  <circle cx="603" cy="160" r="7" fill="#F58220"/>
  <circle cx="690" cy="235" r="7" fill="#F58220"/>
  <circle cx="752" cy="340" r="7" fill="#F58220"/>
  <circle cx="636" cy="510" r="7" fill="#F58220"/>
  <circle cx="780" cy="625" r="7" fill="#F58220"/>
  <circle cx="700" cy="760" r="7" fill="#F58220"/>
</svg>
<div class="cover-wave-1"></div><div class="cover-wave-2"></div><div class="cover-wave-3"></div>
<div class="cover-panel">
<img src="data:image/png;base64,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" class="cover-logo-real" alt="Yusen Logistics">
<h1 class="cover-title">CS OPERATIONS PERFORMANCE DASHBOARD</h1>
<div class="cover-title-accent"></div>
<div class="cover-subtitle">Capacity • Workload • Utilization • Performance</div>
<div class="cover-separator"></div>
<div class="cover-pillars">
<div class="cover-pillar"><div class="cover-icon icon-capacity"><svg viewBox="0 0 32 32"><circle cx="16" cy="9" r="4"></circle><circle cx="7" cy="12" r="3"></circle><circle cx="25" cy="12" r="3"></circle><path d="M9 25v-3c0-4 3-7 7-7s7 3 7 7v3"></path><path d="M2 24v-2c0-3 2-5 5-5"></path><path d="M30 24v-2c0-3-2-5-5-5"></path></svg></div><div class="cover-pillar-title">Capacity</div><div class="cover-pillar-note">HC Capacity,<br>Requirement & Gap</div></div>
<div class="cover-pillar"><div class="cover-icon icon-workload"><svg viewBox="0 0 32 32"><rect x="7" y="6" width="18" height="22" rx="2"></rect><path d="M12 6V4h8v2"></path><path d="M11 12h10"></path><path d="M11 17h10"></path><path d="M11 22h7"></path></svg></div><div class="cover-pillar-title">Workload</div><div class="cover-pillar-note">Customer, Volume,<br>Segment & Activity</div></div>
<div class="cover-pillar"><div class="cover-icon icon-productivity"><svg viewBox="0 0 32 32"><path d="M5 25h22"></path><rect x="7" y="17" width="4" height="8"></rect><rect x="14" y="12" width="4" height="13"></rect><rect x="21" y="7" width="4" height="18"></rect><path d="M6 13l6-5 5 2 8-7"></path><path d="M22 3h4v4"></path></svg></div><div class="cover-pillar-title">UTILIZATION</div><div class="cover-pillar-note">Office Workload,<br>CS Allocation</div></div>
<div class="cover-pillar"><div class="cover-icon icon-insights"><svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="10"></circle><circle cx="16" cy="16" r="5"></circle><path d="M16 16l8-8"></path><path d="M22 8h4v4"></path></svg></div><div class="cover-pillar-title">PERFORMANCE</div><div class="cover-pillar-note">CS Resolution,<br>YVF Booking Adoption</div></div>
</div>
<a href="?enter=1" target="_self" class="cover-cta"><span class="cover-cta-icon">↗</span><span>VIEW DASHBOARD</span><span class="cover-cta-arrow">→</span></a>
<div class="cover-right-footer"><span class="cover-headset"><svg viewBox="0 0 32 32"><path d="M5 17v-2a11 11 0 0 1 22 0v2"></path><rect x="3" y="16" width="5" height="9" rx="2"></rect><rect x="24" y="16" width="5" height="9" rx="2"></rect><path d="M24 26c-2 3-5 3-8 3"></path></svg></span><span class="footer-divider"></span><span>CS DIVISION</span><span class="footer-divider"></span><span>FY2026</span></div>
</div>

</div>"""

    st.markdown(cover_css.strip(), unsafe_allow_html=True)
    st.markdown(cover_html.strip(), unsafe_allow_html=True)



def render_cover_gate() -> None:
    """Stop on the cover until the user selects VIEW DASHBOARD."""
    if "dashboard_entered" not in st.session_state:
        st.session_state["dashboard_entered"] = False

    # The cover CTA is a styled HTML link to ?enter=1.
    # This allows the button to remain visually inside the white cover panel.
    try:
        enter_param = st.query_params.get("enter")
    except Exception:
        enter_param = None

    if isinstance(enter_param, list):
        enter_param = enter_param[0] if enter_param else None

    if str(enter_param) == "1":
        st.session_state["dashboard_entered"] = True
        try:
            st.query_params.clear()
        except Exception:
            pass

    if not st.session_state["dashboard_entered"]:
        render_cover_page()
        st.stop()
