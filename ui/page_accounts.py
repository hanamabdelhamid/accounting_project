import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.components import page_header, section_header, success_msg, error_msg, type_badge, fmt_number, TYPE_COLORS
from logic.accounts_logic import (
    get_all_accounts, add_account, update_account, delete_account,
    search_accounts, ACCOUNT_TYPES
)

LEVEL_LABELS = {1: "Category", 3: "Sub-Group", 6: "Group", 9: "Account"}


def _level(code: str) -> int:
    d = len(str(code))
    if d <= 1: return 1
    if d <= 3: return 3
    if d <= 6: return 6
    return 9


def render():
    page_header("Chart of Accounts", "View, add, edit and delete accounts. Changes propagate to all entries.")

    tab_view, tab_add, tab_edit, tab_delete = st.tabs(["📋 View Accounts", "➕ Add Account", "✏️ Edit Account", "🗑️ Delete Account"])

    # ── VIEW ──────────────────────────────────────────────────────────────────
    with tab_view:
        col_search, col_filter = st.columns([3, 2])
        with col_search:
            query = st.text_input("🔍 Search by code or name", placeholder="e.g. 102 or نقدية")
        with col_filter:
            type_filter = st.multiselect("Filter by type", ACCOUNT_TYPES, default=ACCOUNT_TYPES)

        df = search_accounts(query)
        if type_filter:
            df = df[df["account_type"].isin(type_filter)]

        st.caption(f"Showing **{len(df)}** accounts")

        # Add level indicator
        df = df.copy()
        df["level"] = df["code"].apply(lambda c: LEVEL_LABELS.get(_level(str(c)), "Account"))

        # Color-coded display
        display = df.rename(columns={
            "code": "Code", "account_name": "Account Name",
            "account_type": "Type", "level": "Level"
        })[["Code", "Account Name", "Type", "Level"]]

        def color_type(val):
            c = TYPE_COLORS.get(val, "#64748B")
            return f"background-color:{c}18; color:{c}; font-weight:700;"

        styled = display.style.map(color_type, subset=["Type"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── ADD ───────────────────────────────────────────────────────────────────
    with tab_add:
        section_header("New Account")
        with st.form("add_account_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_code = st.text_input("Account Code *", placeholder="e.g. 102001011")
                new_type = st.selectbox("Account Type *", ACCOUNT_TYPES)
            with c2:
                new_name = st.text_input("Account Name *", placeholder="e.g. Bank - HSBC")

            st.caption("Code structure: 1 digit = Category · 3 digits = Sub-Group · 6 digits = Group · 9 digits = Account")
            submitted = st.form_submit_button("➕ Add Account", use_container_width=True)
            if submitted:
                ok, msg = add_account(new_code, new_name, new_type)
                if ok:
                    success_msg(msg)
                else:
                    error_msg(msg)

    # ── EDIT ──────────────────────────────────────────────────────────────────
    with tab_edit:
        section_header("Edit Existing Account")
        all_df = get_all_accounts()
        options = [f"{r['code']} — {r['account_name']}" for _, r in all_df.iterrows()]
        selected = st.selectbox("Select account to edit", options, key="edit_select")
        if selected:
            old_code = selected.split(" — ")[0]
            old_row = all_df[all_df["code"] == old_code].iloc[0]
            with st.form("edit_account_form"):
                c1, c2 = st.columns(2)
                with c1:
                    edit_code = st.text_input("Account Code", value=old_code)
                    edit_type = st.selectbox("Account Type", ACCOUNT_TYPES,
                                             index=ACCOUNT_TYPES.index(old_row["account_type"]) if old_row["account_type"] in ACCOUNT_TYPES else 0)
                with c2:
                    edit_name = st.text_input("Account Name", value=old_row["account_name"])

                st.info("⚠️ Renaming will update all existing Entry automatically.")
                submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                if submitted:
                    ok, msg = update_account(old_code, edit_code, edit_name, edit_type)
                    if ok:
                        success_msg(msg)
                    else:
                        error_msg(msg)

    # ── DELETE ────────────────────────────────────────────────────────────────
    with tab_delete:
        section_header("Delete Account")
        all_df = get_all_accounts()
        del_options = [f"{r['code']} — {r['account_name']}" for _, r in all_df.iterrows()]
        del_selected = st.selectbox("Select account to delete", del_options, key="del_select")
        if del_selected:
            del_code = del_selected.split(" — ")[0]
            st.warning(f"You are about to delete **{del_selected}**. Accounts with Entry cannot be deleted.")
            if st.button("🗑️ Confirm Delete", type="primary"):
                ok, msg = delete_account(del_code)
                if ok:
                    success_msg(msg)
                else:
                    error_msg(msg)
