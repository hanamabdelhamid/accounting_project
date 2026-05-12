import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.db import load_accounts, save_accounts, load_entries, save_entries

ACCOUNT_TYPES = ["Asset", "Liability/Equity", "Expense", "Revenue"]


def get_all_accounts() -> pd.DataFrame:
    return load_accounts()


def add_account(code: str, name: str, account_type: str) -> tuple[bool, str]:
    df = load_accounts()
    code = code.strip()
    name = name.strip()
    if not code or not name:
        return False, "Code and name are required."
    if code in df["code"].values:
        return False, f"Account code '{code}' already exists."
    new_row = pd.DataFrame([{"code": code, "account_name": name, "account_type": account_type}])
    df = pd.concat([df, new_row], ignore_index=True)
    df = df.sort_values("code").reset_index(drop=True)
    save_accounts(df)
    return True, f"Account '{code} - {name}' added successfully."


def update_account(old_code: str, new_code: str, new_name: str, new_type: str) -> tuple[bool, str]:
    df = load_accounts()
    if old_code not in df["code"].values:
        return False, "Account not found."
    new_code = new_code.strip()
    new_name = new_name.strip()
    if not new_code or not new_name:
        return False, "Code and name are required."
    if new_code != old_code and new_code in df["code"].values:
        return False, f"Code '{new_code}' already exists."

    df.loc[df["code"] == old_code, ["code", "account_name", "account_type"]] = [new_code, new_name, new_type]
    save_accounts(df)

    if old_code != new_code or True:
        entries = load_entries()
        if not entries.empty:
            mask = entries["code"] == old_code
            entries.loc[mask, "code"] = new_code
            entries.loc[mask, "account_name"] = new_name
            entries.loc[mask, "account_type"] = new_type
            save_entries(entries)

    return True, f"Account updated successfully."


def delete_account(code: str) -> tuple[bool, str]:
    df = load_accounts()
    if code not in df["code"].values:
        return False, "Account not found."
    entries = load_entries()
    if not entries.empty and code in entries["code"].values:
        return False, "Cannot delete: account has Entry."
    df = df[df["code"] != code].reset_index(drop=True)
    save_accounts(df)
    return True, f"Account '{code}' deleted."


def search_accounts(query: str) -> pd.DataFrame:
    df = load_accounts()
    if not query:
        return df
    q = query.lower()
    mask = df["code"].str.lower().str.contains(q) | df["account_name"].str.lower().str.contains(q)
    return df[mask].reset_index(drop=True)


def get_account_code_name_map() -> dict:
    df = load_accounts()
    return dict(zip(df["code"], df["account_name"]))


def get_account_type_map() -> dict:
    df = load_accounts()
    return dict(zip(df["code"], df["account_type"]))
