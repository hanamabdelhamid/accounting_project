import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.components import page_header, section_header, fmt_number
from logic.reports_logic import get_income_statement


def render():
    page_header("Income Statement", "Automatically generated from Entry — Revenues minus Expenses.")

    data = get_income_statement()

    rev_df  = data.get("revenues",  pd.DataFrame())
    exp_df  = data.get("expenses",  pd.DataFrame())
    tot_rev = data.get("total_revenues", 0)
    tot_exp = data.get("total_expenses", 0)
    net     = data.get("net_income", 0)

    # Top KPI cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenues",  f"{tot_rev:,.2f}", delta_color="off")
    c2.metric("Total Expenses",  f"{tot_exp:,.2f}", delta_color="off")

    net_label = "Net Profit" if net >= 0 else "Net Loss"
    net_delta = f"{'▲' if net >= 0 else '▼'} {abs(net):,.2f}"
    c3.metric(net_label, f"{net:,.2f}", delta=net_delta,
              delta_color="normal" if net >= 0 else "inverse")

    st.divider()

    col_rev, col_exp = st.columns(2)

    # ── REVENUES ──────────────────────────────────────────────────────────────
    with col_rev:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#DCFCE7,#BBF7D0);
                    border-radius:12px; padding:14px 18px; margin-bottom:12px;">
          <span style="font-size:1.15rem;font-weight:800;color:#166534;">💰 Revenues</span>
        </div>
        """, unsafe_allow_html=True)

        if rev_df.empty:
            st.info("No revenue accounts with activity.")
        else:
            df_disp = rev_df.copy()
            df_disp["amount"] = df_disp["amount"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(df_disp[["code","account_name","amount"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "code": st.column_config.TextColumn("Code", width="small"),
                    "account_name": st.column_config.TextColumn("Account Name"),
                    "amount": st.column_config.TextColumn("Amount", width="medium"),
                })
            st.markdown(f"""
            <div style="text-align:right; font-weight:800; font-size:1rem;
                        color:#166534; padding:6px 0; border-top:2px solid #166534;">
              Total Revenues: {tot_rev:,.2f}
            </div>
            """, unsafe_allow_html=True)

    # ── EXPENSES ──────────────────────────────────────────────────────────────
    with col_exp:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FEE2E2,#FECACA);
                    border-radius:12px; padding:14px 18px; margin-bottom:12px;">
          <span style="font-size:1.15rem;font-weight:800;color:#991B1B;">📤 Expenses</span>
        </div>
        """, unsafe_allow_html=True)

        if exp_df.empty:
            st.info("No expense accounts with activity.")
        else:
            df_disp = exp_df.copy()
            df_disp["amount"] = df_disp["amount"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(df_disp[["code","account_name","amount"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "code": st.column_config.TextColumn("Code", width="small"),
                    "account_name": st.column_config.TextColumn("Account Name"),
                    "amount": st.column_config.TextColumn("Amount", width="medium"),
                })
            st.markdown(f"""
            <div style="text-align:right; font-weight:800; font-size:1rem;
                        color:#991B1B; padding:6px 0; border-top:2px solid #991B1B;">
              Total Expenses: {tot_exp:,.2f}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── NET INCOME BOX ────────────────────────────────────────────────────────
    if net >= 0:
        bg   = "linear-gradient(135deg,#EFF6FF,#DBEAFE)"
        fc   = "#1E40AF"
        icon = "✅"
        label = "Net Profit"
    else:
        bg   = "linear-gradient(135deg,#FEF2F2,#FEE2E2)"
        fc   = "#991B1B"
        icon = "⚠️"
        label = "Net Loss"

    st.markdown(f"""
    <div style="background:{bg}; border-radius:14px; padding:20px 28px; text-align:center; margin-top:10px;">
      <div style="font-size:1rem; color:{fc}; font-weight:600;">{icon} {label}</div>
      <div style="font-size:2.2rem; font-weight:900; color:{fc}; margin-top:6px;">
        {net:,.2f}
      </div>
      <div style="font-size:.85rem; color:#64748B; margin-top:4px;">
        Revenues {tot_rev:,.2f} − Expenses {tot_exp:,.2f}
      </div>
    </div>
    """, unsafe_allow_html=True)
