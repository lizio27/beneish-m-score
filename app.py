import streamlit as st
from beneish import fetch_financial_data, calculate_m_score, interpret_m_score

st.set_page_config(page_title="Beneish M-Score Calculator", layout="wide")
st.title("🚀 Detect Earnings Manipulation")
st.markdown("Enter a stock ticker (e.g., **AAPL**, **TSLA**):")

ticker = st.text_input("Ticker Symbol", placeholder="TSLA").upper()

if st.button("Analyze"):
    if not ticker:
        st.error("Please enter a ticker.")
    else:
        with st.spinner("Calculating..."):
            try:
                data = fetch_financial_data(ticker)
                if data:
                    m_score, components, _ = calculate_m_score(data, "t", "t-1")
                    interpretation = interpret_m_score(m_score, components)

                    st.subheader(f"**{ticker} M-Score: {m_score:.2f}**")
                    st.write("Threshold: **-1.78**")
                    if m_score > -1.78:
                        st.error("High risk of earnings manipulation ⚠️")
                    else:
                        st.success("Low risk ✅")

                    st.subheader("Component Breakdown")
                    col1, col2 = st.columns(2)
                    for key, value in components.items():
                        col1.metric(key, f"{value:.2f}")

                    st.subheader("Red Flags")
                    for key, desc in interpretation["components"].items():
                        if "High" in desc:
                            st.error(f"🔴 {key}: {desc}")
                        else:
                            st.success(f"🟢 {key}: {desc}")
                else:
                    st.error("Data not found. Check the ticker symbol.")
            except Exception as e:
                st.error(f"Error: {str(e)}")