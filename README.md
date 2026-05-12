# Accounting System — University Project

A Streamlit-based accounting application with CSV local storage.

## Project Structure

```
accounting_system/
│
├── app.py                        # Main entry point — run this
│
├── data/                         # Data layer (CSV files + read/write helpers)
│   ├── db.py                     # All CSV read/write functions
│   ├── chart_of_accounts.csv     # Chart of accounts (customizable)
│   ├── journal_entries.csv       # All journal entry lines
│   └── beginning_balances.csv    # Beginning-of-year balances
│
├── logic/                        # Business logic layer
│   ├── accounts_logic.py         # Add / edit / delete accounts
│   ├── entries_logic.py          # Journal entry validation & saving
│   └── reports_logic.py         # Trial balance, income statement, balance sheet
│
├── ui/                           # UI layer
│   ├── components.py             # Shared CSS, colors, helper functions
│   ├── page_dashboard.py         # Dashboard overview
│   ├── page_accounts.py          # Chart of accounts management
│   ├── page_entries.py           # Journal entry form & viewer
│   ├── page_trial_balance.py     # Trial balance report
│   ├── page_income_statement.py  # Income statement report
│   └── page_balance_sheet.py     # Balance sheet report
│
└── requirements.txt
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app will open at http://localhost:8501

## Features

| Page              | Description                                                     |
| ----------------- | --------------------------------------------------------------- |
| Dashboard         | KPI overview, recent journals, health checks                    |
| Chart of Accounts | Add / edit / delete accounts — changes propagate to all entries |
| Entry             | Record transactions with debit/credit balance validation        |
| Trial Balance     | Beginning balances + movements = totals & net balances          |
| Income Statement  | Auto-generated from Revenue & Expense accounts                  |
| Balance Sheet     | Auto-generated from Asset & Liability/Equity accounts           |

## Account Code Structure

| Digits | Level     | Example                  |
| ------ | --------- | ------------------------ |
| 1      | Category  | 1 = Assets               |
| 3      | Sub-Group | 101 = Fixed Assets       |
| 6      | Group     | 101001 = Cooling Fridges |
| 9      | Account   | 101001001 = Fridge #1    |
