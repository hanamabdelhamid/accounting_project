import streamlit as st
from ui import (
    page_accounts,
    page_entries,
    page_trial_balance,
    page_income_statement,
    page_balance_sheet
)

st.set_page_config(page_title="Accounting System", layout="wide", initial_sidebar_state="collapsed")

def main():
    st.markdown("""
        <style>
            /* ─── GLOBAL HIDES & FIXES ─── */
            [data-testid="collapsedControl"] { display: none !important; }
            .stAppDeployButton { display: none !important; }
            [data-testid="stHeader"] { background: transparent !important; }
            .block-container { padding-top: 5.5rem !important; }

            /* ─── DESKTOP NAVBAR (GLASS PILL) ─── */
            div[data-testid="stRadio"] {
                position: fixed !important;
                top: 10px !important; 
                left: 10px !important; 
                right: 10px !important; 
                z-index: 999990 !important; 
                background-color: rgba(255, 255, 255, 0.95) !important; 
                backdrop-filter: blur(10px);
                padding: 10px 15px !important; 
                border-radius: 50px !important; 
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important; 
                border: 1px solid rgba(0, 0, 0, 0.05) !important;
            }

            div[data-testid="stRadio"] > div[role="radiogroup"] {
                display: flex;
                flex-direction: row;
                flex-wrap: nowrap !important;
                align-items: center;
                gap: 8px;
                width: 100%;
            }
            
            div[data-testid="stRadio"] > div[role="radiogroup"]::before {
                content: "📊 Accounting";
                font-size: 20px;
                font-weight: 900;
                color: #6366F1; 
                margin-right: auto; 
                padding-left: 5px;
                white-space: nowrap;
            }
            
            div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
                display: none !important;
            }
            
            div[data-testid="stRadio"] > div[role="radiogroup"] > label {
                padding: 6px 10px;
                margin: 0 4px;
                background-color: transparent !important;
                border: none !important;
                border-bottom: 2px solid transparent !important; 
                border-radius: 0 !important; 
                font-size: 14px; 
                font-weight: 600;
                color: #4B5563 !important; 
                white-space: nowrap; 
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover,
            div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
                color: #6366F1 !important; 
                border-bottom: 2px solid #6366F1 !important;
            }

            /* ─── MOBILE NAVBAR (HAMBURGER MENU) ─── */
            @media (max-width: 768px) {
                /* Make the main container invisible but keep it spanning the top */
                div[data-testid="stRadio"] {
                    background-color: transparent !important;
                    box-shadow: none !important;
                    border: none !important;
                    padding: 0 !important;
                    pointer-events: none !important; /* Lets you click the app behind it */
                }
                
                /* Keep the App Title visible on the top left */
                div[data-testid="stRadio"]::before {
                    content: "📊 Accounting";
                    position: absolute;
                    left: 10px;
                    top: 10px;
                    font-size: 22px;
                    font-weight: 900;
                    color: #6366F1;
                    pointer-events: auto;
                }

                /* Transform the radio group into a circular button on the right */
                div[data-testid="stRadio"] > div[role="radiogroup"] {
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 48px;
                    height: 48px;
                    background-color: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    border: 1px solid rgba(0,0,0,0.05);
                    flex-direction: column !important;
                    overflow: hidden;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    padding: 0;
                    pointer-events: auto;
                }

                /* Hide the desktop title */
                div[data-testid="stRadio"] > div[role="radiogroup"]::before {
                    display: none !important;
                }

                /* The Hamburger Icon */
                div[data-testid="stRadio"] > div[role="radiogroup"]::after {
                    content: "☰";
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 48px;
                    height: 48px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 22px;
                    color: #6366F1;
                    pointer-events: none;
                }

                /* Hover/Tap triggers the dropdown expansion */
                div[data-testid="stRadio"] > div[role="radiogroup"]:hover,
                div[data-testid="stRadio"] > div[role="radiogroup"]:focus-within {
                    width: 220px;
                    height: 340px; /* INCREASED HEIGHT to fit all fields */
                    border-radius: 15px;
                    padding-top: 50px;
                    padding-bottom: 15px; /* Added padding to the bottom */
                    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
                }

                /* Change icon to X when opened */
                div[data-testid="stRadio"] > div[role="radiogroup"]:hover::after,
                div[data-testid="stRadio"] > div[role="radiogroup"]:focus-within::after {
                    content: "✖";
                    font-size: 18px;
                }

                /* Style the individual links for mobile */
                div[data-testid="stRadio"] > div[role="radiogroup"] > label {
                    opacity: 0;
                    padding: 14px 20px !important;
                    margin: 0 !important;
                    width: 100%;
                    border-bottom: 1px solid rgba(0,0,0,0.05) !important;
                    border-radius: 0 !important;
                    transition: opacity 0.2s ease;
                }

                /* Fade in links when expanded */
                div[data-testid="stRadio"] > div[role="radiogroup"]:hover > label,
                div[data-testid="stRadio"] > div[role="radiogroup"]:focus-within > label {
                    opacity: 1;
                }

                .block-container {
                    padding-top: 4.5rem !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    pages = [
        "Accounts", 
        "Entry", 
        "Trial Balance", 
        "Income Statement", 
        "Balance Sheet"
    ]
    
    selected_page = st.radio(
        "Navigation",
        options=pages,
        horizontal=True,
        label_visibility="collapsed"
    )

    if selected_page == "Accounts":
        page_accounts.render()
    elif selected_page == "Entry":
        page_entries.render()
    elif selected_page == "Trial Balance":
        page_trial_balance.render()
    elif selected_page == "Income Statement":
        page_income_statement.render()
    elif selected_page == "Balance Sheet":
        page_balance_sheet.render()

if __name__ == "__main__":
    main()