import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logic.reports_logic import (
    get_trial_balance, update_beginning_balance, 
    delete_beginning_balance, clear_all_balances
)
from logic.accounts_logic import get_all_accounts, get_account_type_map
from data.db import load_balances

def format_currency(val: float) -> str:
    if val == 0:
        return "-"
    elif val < 0:
        return f"({abs(val):,.2f})"
    return f"{val:,.2f}"

def render():
    st.markdown("""
    <div class='main-header'>
      <h1>Trial Balance</h1>
      <p>View hierarchical balances for all accounts across different periods</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='border-left: 5px solid #2563eb; padding-left: 20px; margin-top: 10px; margin-bottom: 20px;'>
            <h3 style='margin: 0;'>Manage Opening Balances</h3>
            <p style='margin: 0; opacity: 0.8;'>Update, delete, or completely reset all starting balances from the background database.</p>
        </div>
        """, unsafe_allow_html=True)

    accounts_df = get_all_accounts()
    
    leaf_accounts = accounts_df[accounts_df["code"].astype(str).str.strip().str.len() == 9]
    options = {f"{str(row['code']).strip()} - {row['account_name']}": str(row['code']).strip() for _, row in leaf_accounts.iterrows()}

    bdf = load_balances()
    bal_map = {}
    if not bdf.empty:
        bdf["code"] = bdf["code"].astype(str).str.strip()
        for _, r in bdf.iterrows():
            code = str(r['code'])
            if code not in bal_map:
                bal_map[code] = {"dr": 0.0, "cr": 0.0}
            bal_map[code]["dr"] += float(r.get("beginning_dr") or 0)
            bal_map[code]["cr"] += float(r.get("beginning_cr") or 0)

    with st.container():
        c1, c_cat, c2, c3 = st.columns([3, 3, 2, 2])
        
        safe_options = list(options.keys()) if options else ["No Sub-accounts available"]
        selected_label = c1.selectbox("Choose Account", safe_options)
        selected_code = options.get(selected_label, "")

        acc_type_map = get_account_type_map()
        account_category = acc_type_map.get(selected_code, "")
        c_cat.text_input("Category", value=account_category, disabled=True)

        current_ob = bal_map.get(selected_code, {"dr": 0.0, "cr": 0.0})

        dr_input = c2.number_input("Debit Amount", min_value=0.0, value=float(current_ob["dr"]), step=100.0)
        cr_input = c3.number_input("Credit Amount", min_value=0.0, value=float(current_ob["cr"]), step=100.0)

        ac1, ac2, ac3 = st.columns([3, 3, 4])
        
        if ac1.button("💾 Save Balance", use_container_width=True, type="primary"):
            if selected_code:
                update_beginning_balance(selected_code, dr_input, cr_input)
                st.success(f"Balance for {selected_code} saved successfully.")
                st.rerun()
                
        if ac2.button("🗑️ Delete This Balance", use_container_width=True):
            if selected_code:
                delete_beginning_balance(selected_code)
                st.success(f"Balance for {selected_code} completely removed.")
                st.rerun()
                
        if ac3.button("⚠️ Wipe ALL Opening Balances", use_container_width=False):
            clear_all_balances()
            st.success("All Opening Balances have been wiped clean from the system.")
            st.rerun()

    st.markdown("---")

    tb = get_trial_balance()

    if tb.empty:
        st.info("No data to display. Please add journal entries or opening balances first.")
        return

    codes = tb["Code"].astype(str).tolist()
    leaf_mask = tb["Code"].astype(str).apply(lambda c: not any(other != c and other.startswith(c) for other in codes))
    leaf_tb = tb[leaf_mask]

    tot_beg_dr = leaf_tb["Opening Balance - Debit"].sum()
    tot_beg_cr = leaf_tb["Opening Balance - Credit"].sum()
    
    tot_mov_dr = leaf_tb["Movement - Debit"].sum()
    tot_mov_cr = leaf_tb["Movement - Credit"].sum()
    
    tot_bal_dr = leaf_tb["bal_dr"].sum()
    tot_bal_cr = leaf_tb["bal_cr"].sum()
    
    diff = tot_bal_dr - tot_bal_cr

    st.markdown("### 📈 Trial Balance Summary")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Debits (Ending)", format_currency(tot_bal_dr))
    m2.metric("Total Credits (Ending)", format_currency(tot_bal_cr))
    m3.metric("Difference", format_currency(abs(diff)))
    m4.metric("Active Sub-accounts", len(leaf_tb))

    if abs(diff) < 0.01:
        st.success("✅ The Trial Balance is perfectly balanced.")
    else:
        st.error(f"❌ The Trial Balance is out of balance by {format_currency(abs(diff))}.")

    with st.expander("Show Breakdown of Totals (Beginning & Movements)"):
        sc1, sc2 = st.columns(2)
        sc1.info(f"**Beginning Balances:** DR {format_currency(tot_beg_dr)} | CR {format_currency(tot_beg_cr)}")
        sc2.info(f"**Period Movement:** DR {format_currency(tot_mov_dr)} | CR {format_currency(tot_mov_cr)}")
        
    st.markdown("---")

    st.markdown("### 📊 Interactive Trial Balance")

    filtered_tb = tb.copy()

    hide_cols = {col: None for col in ["Level", "beg_dr", "beg_cr", "mov_dr", "mov_cr", "tot_dr", "tot_cr", "bal_dr", "bal_cr", "account_type", "code", "account_name"]}

    edited_tb = st.data_editor(
        filtered_tb,
        column_config={
            "Code": st.column_config.TextColumn("Code", disabled=True),
            "Account Name": st.column_config.TextColumn("Account Name", disabled=True),
            "Account Type": st.column_config.TextColumn("Type", disabled=True),
            
            "Opening Balance - Debit": st.column_config.NumberColumn(
                "Opening Balance ➡️ Debit", min_value=0.0, format="%.2f", help="Editable for detailed accounts"
            ),
            "Opening Balance - Credit": st.column_config.NumberColumn(
                "Opening Balance ➡️ Credit", min_value=0.0, format="%.2f", help="Editable for detailed accounts"
            ),
            
            "Movement - Debit": st.column_config.NumberColumn("Movement ➡️ Debit", disabled=True, format="%.2f"),
            "Movement - Credit": st.column_config.NumberColumn("Movement ➡️ Credit", disabled=True, format="%.2f"),
            "Total - Debit": st.column_config.NumberColumn("Total ➡️ Debit", disabled=True, format="%.2f"),
            "Total - Credit": st.column_config.NumberColumn("Total ➡️ Credit", disabled=True, format="%.2f"),
            "Balance": st.column_config.NumberColumn("Net Balance", disabled=True, format="%.2f"),
            "Balance Type": st.column_config.TextColumn("Side", disabled=True),
            **hide_cols
        },
        use_container_width=True,
        hide_index=True,
        key="tb_inline_editor",
    )

    if st.button("💾 Save Table Modifications", type="primary"):
        has_changes = False

        for _, row in edited_tb.iterrows():
            code = str(row["Code"]).strip()

            if len(code) == 9:
                raw_dr = row["Opening Balance - Debit"]
                raw_cr = row["Opening Balance - Credit"]

                new_dr = float(raw_dr) if (pd.notnull(raw_dr) and raw_dr != "") else 0.0
                new_cr = float(raw_cr) if (pd.notnull(raw_cr) and raw_cr != "") else 0.0

                current_ob = bal_map.get(code, {"dr": 0.0, "cr": 0.0})
                if current_ob["dr"] != new_dr or current_ob["cr"] != new_cr:
                    update_beginning_balance(code, new_dr, new_cr)
                    has_changes = True

        if has_changes:
            st.success("Your modifications have been saved and the totals updated.")
            st.rerun()
        else:
            st.info("No changes were detected in the detailed accounts.")