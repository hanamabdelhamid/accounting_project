import streamlit as st

PRIMARY   = "#4F6AF5"   # indigo-blue
SUCCESS   = "#22C55E"   # green
DANGER    = "#EF4444"   # red
WARNING   = "#F59E0B"   # amber
INFO      = "#06B6D4"   # cyan
LIGHT_BG  = "#F8FAFC"
CARD_BG   = "#FFFFFF"
BORDER    = "#E2E8F0"

TYPE_COLORS = {
    "Asset":            "#3B82F6",
    "Liability/Equity": "#8B5CF6",
    "Expense":          "#EF4444",
    "Revenue":          "#22C55E",
}

GLOBAL_CSS = f"""
<style>
  /* App background */
  .stApp {{ background-color: {LIGHT_BG}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
      background: linear-gradient(160deg, #1E3A5F 0%, #2D5B8E 100%);
  }}
  [data-testid="stSidebar"] * {{ color: #E0EAFF !important; }}
  [data-testid="stSidebar"] .stRadio label {{ color: #CBD5E1 !important; font-size: 0.9rem; }}

  /* Metric cards */
  [data-testid="metric-container"] {{
      background: {CARD_BG};
      border: 1px solid {BORDER};
      border-radius: 12px;
      padding: 12px 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}

  /* Dataframes */
  .stDataFrame {{ border-radius: 8px; overflow: hidden; }}

  /* Buttons */
  .stButton > button {{
      border-radius: 8px;
      font-weight: 600;
      transition: all .15s;
  }}
  .stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79,106,245,0.25); }}

  /* Success/Error banners */
  .success-banner {{
      background: #DCFCE7; color: #166534;
      border: 1px solid #BBF7D0; border-radius: 8px;
      padding: 10px 14px; margin: 8px 0; font-weight: 600;
  }}
  .error-banner {{
      background: #FEE2E2; color: #991B1B;
      border: 1px solid #FECACA; border-radius: 8px;
      padding: 10px 14px; margin: 8px 0; font-weight: 600;
  }}

  /* Section header */
  .section-header {{
      border-left: 4px solid {PRIMARY};
      padding-left: 10px; margin: 18px 0 10px;
      font-size: 1.1rem; font-weight: 700; color: #1E3A5F;
  }}

  /* Type badge */
  .badge {{
      display: inline-block; padding: 2px 10px; border-radius: 99px;
      font-size: 0.78rem; font-weight: 700; letter-spacing: .04em;
  }}

  /* Table totals row */
  .total-row {{ font-weight: 800; background: #EFF6FF; }}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1.2rem;">
      <h2 style="margin:0;color:#1E3A5F;font-weight:800;">{title}</h2>
      {"<p style='margin:2px 0 0;color:#64748B;font-size:.92rem;'>"+subtitle+"</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def section_header(label: str):
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)


def success_msg(msg: str):
    st.markdown(f'<div class="success-banner">✅ {msg}</div>', unsafe_allow_html=True)


def error_msg(msg: str):
    st.markdown(f'<div class="error-banner">❌ {msg}</div>', unsafe_allow_html=True)


def type_badge(atype: str) -> str:
    color = TYPE_COLORS.get(atype, "#64748B")
    return f'<span class="badge" style="background:{color}22;color:{color};">{atype}</span>'


def fmt_number(val) -> str:
    try:
        v = float(val)
        if v == 0:
            return "-"
        return f"{v:,.2f}"
    except Exception:
        return str(val)
