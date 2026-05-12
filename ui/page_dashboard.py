import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.components import page_header, section_header, TYPE_COLORS
from logic.accounts_logic import get_all_accounts
from logic.entries_logic import get_journal_summary, get_all_entries
from logic.reports_logic import get_income_statement, get_balance_sheet, get_trial_balance


def render():
    page_header("Dashboard", "Overview of your accounting system at a glance.")

    accounts_df = get_all_accounts()
    entries_df  = get_all_entries()
    summary_df  = get_journal_summary()
    is_data     = get_income_statement()
    bs_data     = get_balance_sheet()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Total Accounts",   len(accounts_df))
    c2.metric("📒 Entry",  len(summary_df))
    c3.metric("💰 Net Income",       f"{is_data.get('net_income',0):,.2f}")
    c4.metric("🏦 Total Assets",     f"{bs_data.get('total_assets',0):,.2f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("Account Types")
        if not accounts_df.empty:
            type_counts = accounts_df["account_type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            for _, row in type_counts.iterrows():
                color = TYPE_COLORS.get(row["Type"], "#64748B")
                pct = row["Count"] / len(accounts_df) * 100
                st.markdown(f"""
                <div style="margin:6px 0;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
                    <span style="font-weight:600;color:{color};">{row['Type']}</span>
                    <span style="color:#64748B;">{row['Count']} accounts ({pct:.0f}%)</span>
                  </div>
                  <div style="background:#E2E8F0;border-radius:99px;height:8px;">
                    <div style="background:{color};width:{pct}%;height:8px;border-radius:99px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        section_header("Recent Entry")
        if summary_df.empty:
            st.info("No Entry recorded yet.")
        else:
            recent = summary_df.tail(5).sort_values("journal_no", ascending=False)
            recent_disp = recent.copy()
            recent_disp["date"] = pd.to_datetime(recent_disp["date"]).dt.strftime("%Y-%m-%d")
            recent_disp["total_dr"] = recent_disp["total_dr"].apply(lambda x: f"{x:,.2f}")
            recent_disp["balanced"] = recent_disp["balanced"].apply(lambda x: "✅" if x else "❌")
            st.dataframe(recent_disp[["journal_no","date","lines","total_dr","balanced"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "journal_no": "Journal #", "date": "Date",
                    "lines": "Lines", "total_dr": "Amount", "balanced": "OK"
                })

    st.divider()

    section_header("Trial Balance Health")
    tb = get_trial_balance()
    if tb.empty:
        st.info("No trial balance data yet.")
    else:
        tot_dr = tb["bal_dr"].sum()
        tot_cr = tb["bal_cr"].sum()
        diff = tot_dr - tot_cr
        balanced = abs(diff) < 0.01

        hc1, hc2, hc3 = st.columns(3)
        hc1.metric("Debit Balances",  f"{tot_dr:,.2f}")
        hc2.metric("Credit Balances", f"{tot_cr:,.2f}")
        hc3.metric("Status", "✅ Balanced" if balanced else "❌ Unbalanced")

    st.divider()

    section_header("Income Statement Summary")
    c_r, c_e, c_n = st.columns(3)

    tot_rev = is_data.get("total_revenues", 0)
    tot_exp = is_data.get("total_expenses", 0)
    net     = is_data.get("net_income", 0)

    c_r.metric("Total Revenues", f"{tot_rev:,.2f}")
    c_e.metric("Total Expenses", f"{tot_exp:,.2f}")
    c_n.metric("Net Income" if net >= 0 else "Net Loss",
               f"{net:,.2f}", delta_color="normal" if net >= 0 else "inverse")
