import pandas as pd
from datetime import date, datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.db import load_entries, save_entries
from logic.accounts_logic import get_account_code_name_map, get_account_type_map


def get_next_journal_no() -> int:
    df = load_entries()
    if df.empty or "journal_no" not in df.columns or df["journal_no"].dropna().empty:
        return 1
    nums = pd.to_numeric(df["journal_no"], errors="coerce").dropna()
    return int(nums.max()) + 1 if not nums.empty else 1


def get_all_entries() -> pd.DataFrame:
    return load_entries()


def get_journal_entries(journal_no: str) -> pd.DataFrame:
    df = load_entries()
    return df[df["journal_no"] == str(journal_no)].reset_index(drop=True)


def validate_journal(lines: list[dict]) -> tuple[bool, str]:
    """Lines: list of {code, dr, cr}"""
    if len(lines) < 2:
        return False, "A journal entry must have at least 2 lines."
    total_dr = sum(float(l.get("dr") or 0) for l in lines)
    total_cr = sum(float(l.get("cr") or 0) for l in lines)
    if abs(total_dr - total_cr) > 0.01:
        return False, f"Debits ({total_dr:,.2f}) ≠ Credits ({total_cr:,.2f}). Entry is not balanced."
    for l in lines:
        dr = float(l.get("dr") or 0)
        cr = float(l.get("cr") or 0)
        if dr > 0 and cr > 0:
            return False, "A line cannot have both Debit and Credit."
        if dr == 0 and cr == 0:
            return False, "Each line must have either a Debit or Credit amount."
    return True, "OK"


def save_journal(
    entry_date: date = None,
    lines: list[dict] = None,
    journal_no: int = None,
    explanation: str = "",
    cost_center: str = "",
    cost_hana: str = ""
) -> tuple[bool, str]:
    if lines is None:
        lines = []
        
    valid, msg = validate_journal(lines)
    if not valid:
        return False, msg

    if journal_no is None:
        journal_no = get_next_journal_no()

    code_name = get_account_code_name_map()
    code_type = get_account_type_map()

    if entry_date is None:
        final_datetime = datetime.now()
    elif type(entry_date) is date:
        final_datetime = datetime.combine(entry_date, datetime.now().time())
    else:
        final_datetime = entry_date

    safe_date = final_datetime.strftime("%Y-%m-%d %H:%M:%S") if hasattr(final_datetime, 'strftime') else str(final_datetime)

    new_rows = []
    for l in lines:
        code = str(l["code"])
        new_rows.append({
            "date": safe_date,
            "code": code,
            "account_name": code_name.get(code, l.get("account_name", "")),
            "dr": float(l.get("dr") or 0) or None,
            "cr": float(l.get("cr") or 0) or None,
            "journal_no": str(journal_no),
            "explanation": explanation,
            "cost_center": cost_center,
            "account_type": code_type.get(code, l.get("account_type", "")),
            "numerical": cost_hana,
        })

    df = load_entries()
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    save_entries(df)
    return True, f"Journal entry #{journal_no} saved with {len(lines)} lines."


def delete_journal(journal_no: str) -> tuple[bool, str]:
    df = load_entries()
    if str(journal_no) not in df["journal_no"].values:
        return False, f"Journal #{journal_no} not found."
    df = df[df["journal_no"] != str(journal_no)].reset_index(drop=True)
    save_entries(df)
    return True, f"Journal #{journal_no} deleted."


def get_journal_summary() -> pd.DataFrame:
    df = load_entries()
    if df.empty:
        return pd.DataFrame(columns=["journal_no", "date", "lines", "total_dr", "total_cr", "balanced"])
    grp = df.groupby("journal_no").agg(
        date=("date", "first"),
        lines=("code", "count"),
        total_dr=("dr", lambda x: pd.to_numeric(x, errors='coerce').fillna(0).sum()),
        total_cr=("cr", lambda x: pd.to_numeric(x, errors='coerce').fillna(0).sum()),
    ).reset_index()
    grp["balanced"] = abs(grp["total_dr"] - grp["total_cr"]) < 0.01
    grp = grp.sort_values("journal_no")
    return grp