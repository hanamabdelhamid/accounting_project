import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.components import page_header, section_header
from logic.reports_logic import get_balance_sheet


def render():
    page_header("Balance Sheet", "Assets = Liabilities + Owner's Equity — auto-populated from the Trial Balance.")

    data = get_balance_sheet()

    assets_df = data.get("assets",             pd.DataFrame())
    le_df     = data.get("liabilities_equity", pd.DataFrame())
    tot_assets = data.get("total_assets",           0)
    tot_le     = data.get("total_liabilities_equity", 0)
    net_income = data.get("net_income",              0)

    # Balance check
    diff = tot_assets - tot_le
    balanced = abs(diff) < 0.01

    # KPI row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Assets",               f"{tot_assets:,.2f}")
    c2.metric("Total Liabilities & Equity", f"{tot_le:,.2f}")
    c3.metric("Difference (should be 0)",   f"{diff:,.2f}",
              delta="Balanced ✅" if balanced else "Not Balanced ❌",
              delta_color="off")

    if balanced:
        st.success("✅ Balance Sheet is balanced — Assets equal Liabilities + Equity.")
    else:
        st.error(f"❌ Balance Sheet is NOT balanced. Difference: {diff:,.2f}")

    st.divider()

    col_a, col_le = st.columns(2)

    def _table(df, total, label, grad_from, grad_to, text_color, border_color):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{grad_from},{grad_to});
                    border-radius:12px;padding:14px 18px;margin-bottom:12px;">
          <span style="font-size:1.1rem;font-weight:800;color:{text_color};">{label}</span>
        </div>
        """, unsafe_allow_html=True)
        if df.empty:
            st.info("No accounts with balances.")
        else:
            df_disp = df.copy()
            df_disp["amount"] = df_disp["amount"].apply(
                lambda x: f"{x:,.2f}" if x != 0 else "-")
            st.dataframe(df_disp[["code","account_name","amount"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "code": st.column_config.TextColumn("Code", width="small"),
                    "account_name": st.column_config.TextColumn("Account Name"),
                    "amount": st.column_config.TextColumn("Amount", width="medium"),
                })
        st.markdown(f"""
        <div style="text-align:right;font-weight:800;font-size:1rem;
                    color:{text_color};padding:6px 0;border-top:2px solid {border_color};">
          {label.split()[-1]} Total: {total:,.2f}
        </div>
        """, unsafe_allow_html=True)

    with col_a:
        _table(assets_df, tot_assets,
               "🏦 Assets",
               "#EFF6FF", "#DBEAFE", "#1E40AF", "#3B82F6")

    with col_le:
        _table(le_df, tot_le,
               "🏛️ Liabilities & Equity",
               "#F5F3FF", "#EDE9FE", "#5B21B6", "#8B5CF6")

        # Net income line inside L&E
        if net_income != 0:
            ni_color = "#166534" if net_income >= 0 else "#991B1B"
            ni_label = "Net Profit" if net_income >= 0 else "Net Loss"
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;
                        padding:10px 14px;margin-top:6px;display:flex;justify-content:space-between;">
              <span style="font-weight:700;color:{ni_color};">+ {ni_label} (from Income Statement)</span>
              <span style="font-weight:800;color:{ni_color};">{net_income:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Summary equation
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F8FAFC,#E2E8F0);
                border-radius:14px;padding:18px 24px;text-align:center;">
      <div style="font-size:.85rem;color:#64748B;margin-bottom:6px;font-weight:600;">
        ACCOUNTING EQUATION
      </div>
      <div style="font-size:1.4rem;font-weight:900;color:#1E3A5F;">
        Assets <span style="color:#3B82F6">{tot_assets:,.2f}</span>
        &nbsp;=&nbsp;
        Liabilities + Equity <span style="color:#8B5CF6">{tot_le:,.2f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
