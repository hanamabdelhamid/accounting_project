import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.db import load_entries, load_balances, save_balances, load_accounts

def get_trial_balance() -> pd.DataFrame:
    accounts_df = load_accounts()
    entries_df = load_entries()
    balances_df = load_balances()

    balances = {}
    if not accounts_df.empty:
        for _, row in accounts_df.iterrows():
            code = str(row["code"]).strip()
            balances[code] = {
                "name": row["account_name"],
                "type": row["account_type"],
                "ob_dr": 0.0, "ob_cr": 0.0, "mv_dr": 0.0, "mv_cr": 0.0
            }

    # 1. Opening balances (Leaf levels)
    if not balances_df.empty:
        balances_df["code"] = balances_df["code"].astype(str).str.strip()
        for _, row in balances_df.iterrows():
            code = row["code"]
            if code in balances:
                balances[code]["ob_dr"] += float(row.get("beginning_dr") or 0)
                balances[code]["ob_cr"] += float(row.get("beginning_cr") or 0)

    # 2. Movement from entries (Leaf levels)
    if not entries_df.empty:
        entries_df["code"] = entries_df["code"].astype(str).str.strip()
        mov = entries_df.groupby("code").agg(
            dr=("dr", lambda x: pd.to_numeric(x, errors='coerce').fillna(0).sum()),
            cr=("cr", lambda x: pd.to_numeric(x, errors='coerce').fillna(0).sum()),
        ).reset_index()
        
        for _, row in mov.iterrows():
            code = str(row["code"]).strip()
            if code in balances:
                balances[code]["mv_dr"] += float(row["dr"])
                balances[code]["mv_cr"] += float(row["cr"])

    # 3. Hierarchical Roll-up (Bottom-up)
    sorted_codes = sorted(list(balances.keys()), key=len, reverse=True)
    for code in sorted_codes:
        parent_code = None
        if len(code) == 9: parent_code = code[:6]
        elif len(code) == 6: parent_code = code[:3]
        elif len(code) == 3: parent_code = code[:1]

        if parent_code and parent_code in balances:
            balances[parent_code]["ob_dr"] += balances[code]["ob_dr"]
            balances[parent_code]["ob_cr"] += balances[code]["ob_cr"]
            balances[parent_code]["mv_dr"] += balances[code]["mv_dr"]
            balances[parent_code]["mv_cr"] += balances[code]["mv_cr"]

    # 4. Format the final output
    rows = []
    for code in sorted(list(balances.keys())):
        b = balances[code]
        tb_dr = b["ob_dr"] + b["mv_dr"]
        tb_cr = b["ob_cr"] + b["mv_cr"]
        bal = tb_dr - tb_cr

        if tb_dr == 0 and tb_cr == 0 and b["ob_dr"] == 0 and b["ob_cr"] == 0:
            continue

        indent = ""
        if len(code) == 3: indent = "   "
        elif len(code) == 6: indent = "      "
        elif len(code) == 9: indent = "         "

        rows.append({
            "Code": code,
            "Account Name": indent + str(b["name"]),
            "Opening Balance - Debit": b["ob_dr"],
            "Opening Balance - Credit": b["ob_cr"],
            "Movement - Debit": b["mv_dr"],
            "Movement - Credit": b["mv_cr"],
            "Total - Debit": tb_dr,
            "Total - Credit": tb_cr,
            "Balance": abs(bal),
            "Balance Type": "Debit" if bal >= 0 else "Credit",
            "Account Type": b["type"],
            "Level": len(code),
            "beg_dr": b["ob_dr"], "beg_cr": b["ob_cr"],
            "mov_dr": b["mv_dr"], "mov_cr": b["mv_cr"],
            "tot_dr": tb_dr, "tot_cr": tb_cr,
            "bal_dr": bal if bal > 0 else 0, 
            "bal_cr": -bal if bal < 0 else 0,
            "account_type": b["type"],
            "code": code,
            "account_name": b["name"]
        })

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def _get_leaf_mask(df: pd.DataFrame) -> pd.Series:
    codes = df["code"].astype(str).tolist()
    return df["code"].astype(str).apply(
        lambda c: not any(other != c and other.startswith(c) for other in codes)
    )

def get_income_statement() -> dict:
    tb = get_trial_balance()
    if tb.empty:
        return {"revenues": pd.DataFrame(), "expenses": pd.DataFrame(), "net_income": 0}

    tb_leaf = tb[_get_leaf_mask(tb)].copy()

    rev = tb_leaf[tb_leaf["account_type"] == "Revenue"].copy()
    exp = tb_leaf[tb_leaf["account_type"] == "Expense"].copy()

    rev["amount"] = rev["Total - Credit"] - rev["Total - Debit"]
    exp["amount"] = abs(exp["Total - Debit"] - exp["Total - Credit"])
    
    rev = rev[rev["amount"] != 0]
    exp = exp[exp["amount"] != 0]

    total_rev = rev["amount"].sum()
    total_exp = exp["amount"].sum()
    net_income = total_rev - total_exp

    return {
        "revenues": rev[["code", "account_name", "amount"]],
        "expenses": exp[["code", "account_name", "amount"]],
        "total_revenues": total_rev,
        "total_expenses": total_exp,
        "net_income": net_income,
    }

def get_balance_sheet() -> dict:
    tb = get_trial_balance()
    is_data = get_income_statement()

    if tb.empty:
        return {"assets": pd.DataFrame(), "liabilities_equity": pd.DataFrame(),
                "total_assets": 0, "total_liabilities_equity": 0}

    tb_leaf = tb[_get_leaf_mask(tb)].copy()

    assets = tb_leaf[tb_leaf["account_type"] == "Asset"].copy()
    le = tb_leaf[tb_leaf["account_type"] == "Liability/Equity"].copy()

    assets["amount"] = assets["Total - Debit"] - assets["Total - Credit"]
    le["amount"] = le["Total - Credit"] - le["Total - Debit"]

    assets = assets[assets["amount"] != 0]
    le = le[le["amount"] != 0]

    total_assets = assets["amount"].sum()
    total_le = le["amount"].sum() + is_data["net_income"]

    return {
        "assets": assets[["code", "account_name", "amount"]],
        "liabilities_equity": le[["code", "account_name", "amount"]],
        "total_assets": total_assets,
        "total_liabilities_equity": total_le,
        "net_income": is_data["net_income"],
    }

def update_beginning_balance(code: str, beg_dr: float, beg_cr: float) -> tuple[bool, str]:
    df = load_balances()
    code = str(code).strip()
    
    accounts = load_accounts()
    accounts["code"] = accounts["code"].astype(str).str.strip()
    acc = accounts[accounts["code"] == code]
    if acc.empty:
        return False, "Account not found."
        
    name = acc["account_name"].values[0]
    atype = acc["account_type"].values[0]

    if not df.empty:
        df["code"] = df["code"].astype(str).str.strip()

    # Clean out old duplicates
    if not df.empty and code in df["code"].values:
        df = df[df["code"] != code] 

    # If both inputs are exactly zero, do not write a new row (effectively deletes it)
    if float(beg_dr) == 0.0 and float(beg_cr) == 0.0:
        save_balances(df)
        return True, "Balance cleared from system."

    new_row = pd.DataFrame([{"code": code, "account_name": name, "account_type": atype,
                              "beginning_dr": float(beg_dr), "beginning_cr": float(beg_cr)}])
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row], ignore_index=True)
        
    save_balances(df)
    return True, "Beginning balance updated."

def delete_beginning_balance(code: str) -> tuple[bool, str]:
    """Manually deletes a single account's beginning balance from the CSV."""
    df = load_balances()
    if not df.empty:
        df["code"] = df["code"].astype(str).str.strip()
        df = df[df["code"] != str(code).strip()]
        save_balances(df)
    return True, "Balance deleted."

def clear_all_balances() -> tuple[bool, str]:
    """Wipes the entire beginning balances database clean."""
    df = pd.DataFrame(columns=["code", "account_name", "account_type", "beginning_dr", "beginning_cr"])
    save_balances(df)
    return True, "All opening balances have been cleared."