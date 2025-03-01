import streamlit as st
from beneish import fetch_financial_data, calculate_m_score, interpret_m_score

# Streamlit app configuration
st.set_page_config(page_title="Beneish M-Score Calculator", layout="wide")
st.title("🚀 Beneish M-Score Calculator")
st.markdown("""
**Detect earnings manipulation** using the Beneish M-Score model.  
Enter a stock ticker below (e.g., `AAPL`, `TSLA`):
""")

# User input
ticker = st.text_input("Enter a ticker symbol:", placeholder="TSLA").upper()

# Add a collapsible section for ratio explanations
with st.expander("📚 **What are the Beneish M-Score Ratios?**"):
    st.markdown("""
    The Beneish M-Score uses **8 financial ratios** to detect earnings manipulation. Here's what each ratio means:

    - **DSRI (Days Sales in Receivables Index)**:
      Measures the change in accounts receivable relative to sales. A high value may indicate inflated revenues.
      - **Formula**: (Receivables_t / Sales_t) / (Receivables_t-1 / Sales_t-1)

    - **GMI (Gross Margin Index)**:
      Tracks changes in gross margin. A high value suggests deteriorating profitability, which could signal manipulation.
      - **Formula**: (Gross Margin_t-1 / Sales_t-1) / (Gross Margin_t / Sales_t)

    - **AQI (Asset Quality Index)**:
      Measures the proportion of non-current assets. A high value may indicate capitalization of expenses.
      - **Formula**: (1 - (Current Assets_t + PPE_t) / Total Assets_t) / (1 - (Current Assets_t-1 + PPE_t-1) / Total Assets_t-1)

    - **SGI (Sales Growth Index)**:
      Tracks sales growth. Unusually high growth may indicate manipulation.
      - **Formula**: Sales_t / Sales_t-1

    - **DEPI (Depreciation Index)**:
      Measures changes in depreciation rates. A high value may suggest slowing depreciation to inflate earnings.
      - **Formula**: (Depreciation_t-1 / (PPE_t-1 + Depreciation_t-1)) / (Depreciation_t / (PPE_t + Depreciation_t))

    - **SGAI (Selling, General, and Administrative Expenses Index)**:
      Tracks changes in SG&A expenses relative to sales. A high value may indicate loss of cost control.
      - **Formula**: (SG&A_t / Sales_t) / (SG&A_t-1 / Sales_t-1)

    - **TATA (Total Accruals to Total Assets)**:
      Measures the proportion of accruals to total assets. High accruals may indicate earnings manipulation.
      - **Formula**: (Net Income_t - Operating Cash Flow_t) / Total Assets_t

    - **LVGI (Leverage Index)**:
      Tracks changes in leverage. A high value may indicate increased financial risk or manipulation.
      - **Formula**: (Total Liabilities_t / Total Assets_t) / (Total Liabilities_t-1 / Total Assets_t-1)
    """)

if st.button("Analyze"):
    if not ticker:
        st.error("Please enter a ticker symbol.")
    else:
        with st.spinner("Fetching data and calculating..."):
            try:
                # Fetch data
                data = fetch_financial_data(ticker)
                
                if data:
                    # Calculate M-Score for the latest year (t vs t-1)
                    m_score, components, _ = calculate_m_score(data, "t", "t-1")
                    interpretation = interpret_m_score(m_score, components)
                    
                    # Display results
                    st.success(f"**M-Score for {ticker}: {m_score:.2f}**")
                    if m_score > -1.78:
                        st.error("⚠️ **High probability of earnings manipulation**")
                    else:
                        st.success("✅ **Low probability of earnings manipulation**")
                    
                    # Show component breakdown
                    st.subheader("Component Analysis:")
                    col1, col2 = st.columns(2)
                    for key, value in components.items():
                        col1.metric(label=key, value=f"{value:.2f}")
                    
                    # Show interpretations
                    st.subheader("Red Flags:")
                    for key, desc in interpretation["components"].items():
                        if "High" in desc:
                            st.error(f"- {key}: {desc}")
                        else:
                            st.success(f"- {key}: {desc}")
                else:
                    st.error("Failed to fetch data. Check if the ticker is valid or has complete financial statements.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
