import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__))

ACCOUNTS_FILE = os.path.join(DATA_DIR, "chart_of_accounts.csv")
ENTRIES_FILE = os.path.join(DATA_DIR, "journal_entries.csv")
BALANCES_FILE = os.path.join(DATA_DIR, "beginning_balances.csv")


def _read(path, dtype=None):
    return pd.read_csv(path, encoding="utf-8-sig", dtype=dtype)


def _write(df, path):
    df.to_csv(path, index=False, encoding="utf-8-sig")


def load_accounts() -> pd.DataFrame:
    return _read(ACCOUNTS_FILE, dtype={"code": str})


def save_accounts(df: pd.DataFrame):
    _write(df, ACCOUNTS_FILE)


def load_entries() -> pd.DataFrame:
    df = _read(ENTRIES_FILE, dtype={"code": str, "journal_no": str})
    if not df.empty:
        df["dr"] = pd.to_numeric(df["dr"], errors="coerce")
        df["cr"] = pd.to_numeric(df["cr"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def save_entries(df: pd.DataFrame):
    _write(df, ENTRIES_FILE)


def load_balances() -> pd.DataFrame:
    df = _read(BALANCES_FILE, dtype={"code": str})
    if not df.empty:
        df["beginning_dr"] = pd.to_numeric(df["beginning_dr"], errors="coerce").fillna(0)
        df["beginning_cr"] = pd.to_numeric(df["beginning_cr"], errors="coerce").fillna(0)
    return df


def save_balances(df: pd.DataFrame):
    _write(df, BALANCES_FILE)
