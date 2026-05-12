import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.components import page_header, section_header, success_msg, error_msg, fmt_number
from logic.entries_logic import (
    get_all_entries, get_journal_entries, get_next_journal_no,
    save_journal, delete_journal, get_journal_summary, validate_journal
)
from logic.accounts_logic import get_all_accounts, get_account_code_name_map, get_account_type_map


def render():
    page_header("Entry", "Record financial transactions. Debits must equal Credits per journal entry.")

    tab_new, tab_view, tab_manage = st.tabs(["✏️ New Entry", "📋 View All Entries", "🗂️ Manage Journals"])

    accounts_df = get_all_accounts()
    
    sub_accounts_df = accounts_df[accounts_df["code"].astype(str).str.strip().str.len() == 9]
    acc_options = ["— Select Account —"] + [f"{r['code']} — {r['account_name']}" for _, r in sub_accounts_df.iterrows()]
    
    code_name   = get_account_code_name_map()
    code_type   = get_account_type_map()

    if "form_key" not in st.session_state:
        st.session_state.form_key = 0
    fk = st.session_state.form_key

    # ── NEW ENTRY ─────────────────────────────────────────────────────────────
    with tab_new:
        next_jno = get_next_journal_no()
        section_header(f"Journal Entry  #{next_jno}")

        col_date, col_exp, col_cc, col_hana = st.columns([2, 3, 2, 2])
        with col_date:
            # Change the default value to today's date instead of None
            entry_date = st.date_input("Date", value=date.today(), key=f"entry_date_input_{fk}")
        with col_exp:
            explanation = st.text_input("Explanation (optional)", key=f"explanation_input_{fk}")
        with col_cc:
            cost_center = st.text_input("Cost Center (optional)", key=f"cost_center_input_{fk}")
        with col_hana:
            cost_hana = st.text_input("Numerical (optional)", key=f"numerical_input_{fk}")

        st.divider()
        section_header("Entry Lines")

        if "entry_lines" not in st.session_state:
            st.session_state.entry_lines = [
                {"code": "", "dr": 0.0, "cr": 0.0},
                {"code": "", "dr": 0.0, "cr": 0.0},
            ]

        lines = st.session_state.entry_lines
        updated_lines = []

        for i, line in enumerate(lines):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            with c1:
                current_code = line.get("code", "")
                current_idx = 0
                if current_code:
                    for j, opt in enumerate(acc_options):
                        if opt.startswith(current_code):
                            current_idx = j
                            break
                            
                chosen = st.selectbox(f"Account #{i+1}", acc_options, index=current_idx, key=f"acc_{i}_{fk}")
                chosen_code = chosen.split(" — ")[0] if chosen != "— Select Account —" else ""
            with c2:
                dr_val = st.number_input("Debit", min_value=0.0, value=float(line.get("dr") or 0), step=100.0, key=f"dr_{i}_{fk}", format="%.2f")
            with c3:
                cr_val = st.number_input("Credit", min_value=0.0, value=float(line.get("cr") or 0), step=100.0, key=f"cr_{i}_{fk}", format="%.2f")
            with c4:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"del_line_{i}_{fk}", help="Remove this line") and len(lines) > 2:
                    continue 
            updated_lines.append({"code": chosen_code, "dr": dr_val, "cr": cr_val})

        st.session_state.entry_lines = updated_lines

        if st.button("➕ Add Line"):
            st.session_state.entry_lines.append({"code": "", "dr": 0.0, "cr": 0.0})
            st.rerun()

        total_dr = sum(float(l.get("dr") or 0) for l in st.session_state.entry_lines)
        total_cr = sum(float(l.get("cr") or 0) for l in st.session_state.entry_lines)
        diff     = total_dr - total_cr
        balanced = abs(diff) < 0.01

        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Total Debit",  f"{total_dr:,.2f}")
        col_t2.metric("Total Credit", f"{total_cr:,.2f}")
        col_t3.metric("Difference",   f"{diff:,.2f}", delta_color="off")

        if not balanced:
            error_msg(f"Entry is not balanced — difference is {diff:,.2f}")
        else:
            st.success("✅ Entry is balanced and ready to save.")

        c_save, c_clear = st.columns(2)
        with c_save:
            if st.button("💾 Save Journal Entry", type="primary", use_container_width=True):
                errors = []
                if not entry_date:
                    errors.append("Date is required.")
                    
                for idx, l in enumerate(st.session_state.entry_lines):
                    if not l["code"]:
                        errors.append(f"Line {idx+1}: Account must be selected.")
                    
                    d = float(l.get("dr") or 0)
                    c = float(l.get("cr") or 0)
                    
                    if d == 0 and c == 0:
                        errors.append(f"Line {idx+1}: Must have a Debit or Credit amount.")
                    elif d > 0 and c > 0:
                        errors.append(f"Line {idx+1}: Cannot have both Debit and Credit amounts.")
                        
                if not balanced:
                    errors.append("Entry is not balanced. Please fix the difference.")
                if len(st.session_state.entry_lines) < 2:
                    errors.append("At least 2 lines are required.")

                if errors:
                    for e in errors:
                        error_msg(e)
                else:
                    ok, msg = save_journal(entry_date, st.session_state.entry_lines, explanation=explanation, cost_center=cost_center, cost_hana=cost_hana)
                    if ok:
                        success_msg(msg)
                        st.session_state.entry_lines = [
                            {"code": "", "dr": 0.0, "cr": 0.0},
                            {"code": "", "dr": 0.0, "cr": 0.0},
                        ]
                        st.session_state.form_key += 1
                        st.rerun()
                    else:
                        error_msg(msg)

    # ── VIEW ALL ──────────────────────────────────────────────────────────────
    with tab_view:
        section_header("All Journal Entry Lines")
        df = get_all_entries()
        if df.empty:
            st.info("No Entry yet. Use the 'New Entry' tab to add one.")
        else:
            df_disp = df.copy()
            df_disp["dr"] = df_disp["dr"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x else "-")
            df_disp["cr"] = df_disp["cr"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x else "-")
            
            if "Date" in df_disp.columns and "date" in df_disp.columns:
                df_disp["date"] = df_disp["date"].fillna(df_disp["Date"])
            elif "Date" in df_disp.columns:
                df_disp["date"] = df_disp["Date"]

            # FORMATTING UPDATE: Show full %Y-%m-%d %H:%M:%S in the table
            if "date" in df_disp.columns:
                df_disp["date"] = pd.to_datetime(df_disp["date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
                df_disp["date"] = df_disp["date"].fillna("-")
            else:
                df_disp["date"] = "-"
            
            if "cost_center" not in df_disp.columns:
                df_disp["cost_center"] = ""
            if "numerical" not in df_disp.columns:
                df_disp["numerical"] = ""
            if "explanation" not in df_disp.columns:
                df_disp["explanation"] = ""
            if "journal_no" not in df_disp.columns:
                df_disp["journal_no"] = df_disp.get("Journal No.", "")
                
            st.dataframe(
                df_disp[["journal_no", "date", "code", "account_name", "dr", "cr", "account_type", "explanation", "cost_center", "numerical"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "journal_no": "Journal #",
                    "date": "Date & Time",
                    "code": "Code",
                    "account_name": "Account",
                    "dr": "Debit",
                    "cr": "Credit",
                    "account_type": "Type",
                    "explanation": "Explanation",
                    "cost_center": "Cost Center",
                    "numerical": "Numerical",
                }
            )

    # ── MANAGE ────────────────────────────────────────────────────────────────
    with tab_manage:
        section_header("Journal Summary")
        summary = get_journal_summary()
        if summary.empty:
            st.info("No journals recorded yet.")
        else:
            summary_disp = summary.copy()
            
            if "Date" in summary_disp.columns and "date" in summary_disp.columns:
                summary_disp["date"] = summary_disp["date"].fillna(summary_disp["Date"])
            elif "Date" in summary_disp.columns:
                summary_disp["date"] = summary_disp["Date"]
                
            # FORMATTING UPDATE: Show full %Y-%m-%d %H:%M:%S in the manage table
            if "date" in summary_disp.columns:
                summary_disp["date"] = pd.to_datetime(summary_disp["date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
                summary_disp["date"] = summary_disp["date"].fillna("-")
            else:
                summary_disp["date"] = "-"
                
            summary_disp["total_dr"] = summary_disp["total_dr"].apply(lambda x: f"{x:,.2f}")
            summary_disp["total_cr"] = summary_disp["total_cr"].apply(lambda x: f"{x:,.2f}")
            summary_disp["balanced"] = summary_disp["balanced"].apply(lambda x: "✅" if x else "❌")
            
            if "journal_no" not in summary_disp.columns:
                summary_disp["journal_no"] = summary_disp.get("Journal No.", "")
                
            st.dataframe(summary_disp, use_container_width=True, hide_index=True,
                column_config={
                    "journal_no": "Journal #", "date": "Date & Time", "lines": "Lines",
                    "total_dr": "Total DR", "total_cr": "Total CR", "balanced": "Balanced"
                })

            st.divider()
            section_header("Delete a Journal Entry")
            jno_list = summary["journal_no"].tolist() if "journal_no" in summary.columns else []
            del_jno  = st.selectbox("Select Journal #", jno_list, key="del_jno")
            if st.button("🗑️ Delete Journal", type="primary"):
                ok, msg = delete_journal(str(del_jno))
                if ok:
                    success_msg(msg)
                    st.rerun()
                else:
                    error_msg(msg)