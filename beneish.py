#!/usr/bin/env python
# coding: utf-8

# In[8]:


import yfinance as yf

# Beneish M-Score Formula Coefficients
coefficients = {
    "DSRI": 0.92,
    "GMI": 0.528,
    "AQI": 0.404,
    "SGI": 0.892,
    "DEPI": 0.115,
    "SGAI": -0.172,
    "TATA": 4.679,
    "LVGI": -0.327,
    "Constant": -4.84
}

def fetch_financial_data(ticker):
    print(f"Fetching financial data for {ticker}...")
    stock = yf.Ticker(ticker)
    income_stmt = stock.income_stmt
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cash_flow
    
    data = {}
    
    try:
        # Income Statement (Current Year: t, Prior Year: t-1, Previous Year: t-2)
        data["Total Revenue_t"] = income_stmt.loc['Total Revenue'].iloc[0] 
        data["Total Revenue_t-1"] = income_stmt.loc['Total Revenue'].iloc[1] 
        data["Total Revenue_t-2"] = income_stmt.loc['Total Revenue'].iloc[2] 
        data["Cost Of Revenue_t"] = income_stmt.loc['Cost Of Revenue'].iloc[0] 
        data["Cost Of Revenue_t-1"] = income_stmt.loc['Cost Of Revenue'].iloc[1] 
        data["Cost Of Revenue_t-2"] = income_stmt.loc['Cost Of Revenue'].iloc[2] 
        data["Selling General And Administration_t"] = income_stmt.loc['Selling General And Administration'].iloc[0]
        data["Selling General And Administration_t-1"] = income_stmt.loc['Selling General And Administration'].iloc[1]
        data["Selling General And Administration_t-2"] = income_stmt.loc['Selling General And Administration'].iloc[2]
        data["Net Income_t"] = income_stmt.loc['Net Income'].iloc[0]
        data["Net Income_t-1"] = income_stmt.loc['Net Income'].iloc[1]
        data["Net Income_t-2"] = income_stmt.loc['Net Income'].iloc[2]
        
        # Balance Sheet
        data["Accounts Receivable_t"] = balance_sheet.loc['Accounts Receivable'].iloc[0]
        data["Accounts Receivable_t-1"] = balance_sheet.loc['Accounts Receivable'].iloc[1]
        data["Accounts Receivable_t-2"] = balance_sheet.loc['Accounts Receivable'].iloc[2]
        data["Current Assets_t"] = balance_sheet.loc['Current Assets'].iloc[0]
        data["Current Assets_t-1"] = balance_sheet.loc['Current Assets'].iloc[1]
        data["Current Assets_t-2"] = balance_sheet.loc['Current Assets'].iloc[2]
        data["Net PPE_t"] = balance_sheet.loc['Net PPE'].iloc[0]
        data["Net PPE_t-1"] = balance_sheet.loc['Net PPE'].iloc[1]
        data["Net PPE_t-2"] = balance_sheet.loc['Net PPE'].iloc[2]
        data["Total Assets_t"] = balance_sheet.loc['Total Assets'].iloc[0]
        data["Total Assets_t-1"] = balance_sheet.loc['Total Assets'].iloc[1]
        data["Total Assets_t-2"] = balance_sheet.loc['Total Assets'].iloc[2]
        data["Total Liabilities Net Minority Interest_t"] = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]
        data["Total Liabilities Net Minority Interest_t-1"] = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[1]
        data["Total Liabilities Net Minority Interest_t-2"] = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[2]
        
        # Cash Flow Statement
        data["Depreciation_t"] = cash_flow.loc['Depreciation And Amortization'].iloc[0]
        data["Depreciation_t-1"] = cash_flow.loc['Depreciation And Amortization'].iloc[1]
        data["Depreciation_t-2"] = cash_flow.loc['Depreciation And Amortization'].iloc[2]
        data["Operating Cash Flow_t"] = cash_flow.loc['Operating Cash Flow'].iloc[0]
        data["Operating Cash Flow_t-1"] = cash_flow.loc['Operating Cash Flow'].iloc[1]
        data["Operating Cash Flow_t-2"] = cash_flow.loc['Operating Cash Flow'].iloc[2]
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        print("This could be due to missing financial data or different naming conventions in the financial statements.")
        return None

def safe_divide(numerator, denominator, default=1.0):
    """Safe division function to handle zero division errors"""
    if denominator == 0:
        return default
    return numerator / denominator

def calculate_m_score(data, year_suffix_t, year_suffix_t_minus_1):
    try:
        # Calculate the 8 ratios for the given year suffixes with safe division
        DSRI = safe_divide(
            safe_divide(data[f'Accounts Receivable_{year_suffix_t}'], data[f'Total Revenue_{year_suffix_t}']),
            safe_divide(data[f'Accounts Receivable_{year_suffix_t_minus_1}'], data[f'Total Revenue_{year_suffix_t_minus_1}'])
        )
        
        # Gross Margin for current and previous periods
        gm_t_minus_1 = safe_divide(data[f'Total Revenue_{year_suffix_t_minus_1}'] - data[f'Cost Of Revenue_{year_suffix_t_minus_1}'], 
                                   data[f'Total Revenue_{year_suffix_t_minus_1}'])
        gm_t = safe_divide(data[f'Total Revenue_{year_suffix_t}'] - data[f'Cost Of Revenue_{year_suffix_t}'], 
                           data[f'Total Revenue_{year_suffix_t}'])
        GMI = safe_divide(gm_t_minus_1, gm_t)
        
        # Asset Quality for current and previous periods
        aqi_t = 1 - safe_divide(data[f'Current Assets_{year_suffix_t}'] + data[f'Net PPE_{year_suffix_t}'], 
                              data[f'Total Assets_{year_suffix_t}'])
        aqi_t_minus_1 = 1 - safe_divide(data[f'Current Assets_{year_suffix_t_minus_1}'] + data[f'Net PPE_{year_suffix_t_minus_1}'], 
                                       data[f'Total Assets_{year_suffix_t_minus_1}'])
        AQI = safe_divide(aqi_t, aqi_t_minus_1)
        
        # Sales Growth Index
        SGI = safe_divide(data[f'Total Revenue_{year_suffix_t}'], data[f'Total Revenue_{year_suffix_t_minus_1}'])
        
        # Depreciation Index
        depi_t_minus_1 = safe_divide(data[f'Depreciation_{year_suffix_t_minus_1}'], 
                                    (data[f'Net PPE_{year_suffix_t_minus_1}'] + data[f'Depreciation_{year_suffix_t_minus_1}']))
        depi_t = safe_divide(data[f'Depreciation_{year_suffix_t}'], 
                           (data[f'Net PPE_{year_suffix_t}'] + data[f'Depreciation_{year_suffix_t}']))
        DEPI = safe_divide(depi_t_minus_1, depi_t)
        
        # SG&A Index
        sgai_t = safe_divide(data[f'Selling General And Administration_{year_suffix_t}'], data[f'Total Revenue_{year_suffix_t}'])
        sgai_t_minus_1 = safe_divide(data[f'Selling General And Administration_{year_suffix_t_minus_1}'], 
                                    data[f'Total Revenue_{year_suffix_t_minus_1}'])
        SGAI = safe_divide(sgai_t, sgai_t_minus_1)
        
        # Total Accruals to Total Assets
        TATA = safe_divide(data[f'Net Income_{year_suffix_t}'] - data[f'Operating Cash Flow_{year_suffix_t}'], 
                         data[f'Total Assets_{year_suffix_t}'])
        
        # Leverage Index
        lvgi_t = safe_divide(data[f'Total Liabilities Net Minority Interest_{year_suffix_t}'], data[f'Total Assets_{year_suffix_t}'])
        lvgi_t_minus_1 = safe_divide(data[f'Total Liabilities Net Minority Interest_{year_suffix_t_minus_1}'], 
                                   data[f'Total Assets_{year_suffix_t_minus_1}'])
        LVGI = safe_divide(lvgi_t, lvgi_t_minus_1)
        
        # Collect individual components with their values
        components = {
            "DSRI": DSRI,
            "GMI": GMI,
            "AQI": AQI,
            "SGI": SGI,
            "DEPI": DEPI,
            "SGAI": SGAI,
            "TATA": TATA,
            "LVGI": LVGI
        }
        
        # Check for NaN or infinity values and replace with 1.0 (neutral)
        for key, value in components.items():
            if value != value or value == float('inf') or value == float('-inf'):  # Check for NaN or infinity
                print(f"Warning: {key} calculation resulted in an invalid value. Using 1.0 instead.")
                components[key] = 1.0
        
        # Calculate weighted components
        weighted_components = {}
        for key, value in components.items():
            weighted_components[key] = coefficients[key] * value
        
        # Calculate M-Score
        m_score = coefficients["Constant"]
        for key, value in weighted_components.items():
            m_score += value
        
        return m_score, components, weighted_components
    
    except Exception as e:
        print(f"Error calculating M-Score: {e}")
        # Return default values
        default_components = {k: 1.0 for k in ["DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "TATA", "LVGI"]}
        default_weighted = {k: coefficients[k] for k in default_components}
        return coefficients["Constant"] + sum(default_weighted.values()), default_components, default_weighted

def interpret_m_score(m_score, components):
    result = {}
    
    # Overall interpretation
    if m_score < -1.78:
        result["overall"] = "Low probability of earnings manipulation."
    else:
        result["overall"] = "High probability of earnings manipulation."
    
    # Individual components interpretation
    result["components"] = {}
    
    # DSRI - Days Sales in Receivables Index
    if components["DSRI"] > 1.031:
        result["components"]["DSRI"] = "High - Possible inflated revenues"
    else:
        result["components"]["DSRI"] = "Normal"
    
    # GMI - Gross Margin Index
    if components["GMI"] > 1.193:
        result["components"]["GMI"] = "High - Deteriorating margins, negative signal"
    else:
        result["components"]["GMI"] = "Normal"
    
    # AQI - Asset Quality Index
    if components["AQI"] > 1.254:
        result["components"]["AQI"] = "High - Possible capitalization of expenses"
    else:
        result["components"]["AQI"] = "Normal"
    
    # SGI - Sales Growth Index
    if components["SGI"] > 1.607:
        result["components"]["SGI"] = "High - Unusual sales growth, pressure to manipulate"
    else:
        result["components"]["SGI"] = "Normal"
    
    # DEPI - Depreciation Index
    if components["DEPI"] > 1.077:
        result["components"]["DEPI"] = "High - Possible slowing of depreciation rates"
    else:
        result["components"]["DEPI"] = "Normal"
    
    # SGAI - SG&A Index
    if components["SGAI"] > 1.041:
        result["components"]["SGAI"] = "High - Loss of cost control"
    else:
        result["components"]["SGAI"] = "Normal"
    
    # TATA - Total Accruals to Total Assets
    if components["TATA"] > 0.018:
        result["components"]["TATA"] = "High - Possible earnings manipulation through accruals"
    else:
        result["components"]["TATA"] = "Normal"
    
    # LVGI - Leverage Index
    if components["LVGI"] > 1.111:
        result["components"]["LVGI"] = "High - Increased leverage, potential manipulation to meet debt covenants"
    else:
        result["components"]["LVGI"] = "Normal"
    
    return result

def print_report(period_label, ticker, m_score, components, weighted_components, interpretation):
    print("\n" + "="*60)
    print(f"BENEISH M-SCORE ANALYSIS FOR {ticker} - {period_label}")
    print("="*60)
    
    print("\nINDIVIDUAL RATIO VALUES:")
    print("-"*60)
    for key, value in components.items():
        print(f"{key}: {value:.4f}")
    
    print("\nWEIGHTED COMPONENTS:")
    print("-"*60)
    for key, value in weighted_components.items():
        print(f"{key} ({coefficients[key]:+.3f} × {components[key]:.4f}): {value:.4f}")
    
    print("\nFINAL CALCULATION:")
    print("-"*60)
    component_sum = sum(weighted_components.values())
    print(f"Constant: {coefficients['Constant']}")
    print(f"Sum of weighted components: {component_sum:.4f}")
    print(f"M-Score = {coefficients['Constant']} + {component_sum:.4f} = {m_score:.4f}")
    
    print("\nINTERPRETATION:")
    print("-"*60)
    print(f"M-Score: {m_score:.4f}")
    print(f"Threshold: -1.78")
    print(f"Result: {interpretation['overall']}")
    
    print("\nCOMPONENT ANALYSIS:")
    print("-"*60)
    for key, value in interpretation["components"].items():
        print(f"{key}: {value}")

def print_comparison(current_year, prior_year, current_m_score, prior_m_score, 
                    current_components, prior_components, 
                    current_weighted, prior_weighted):
    
    print("-"*60)
    print("\nNOTE:")
    print("The Beneish M-Score is a probabilistic model that identifies the likelihood of")
    print("earnings manipulation. A score greater than -1.78 suggests a high probability of")
    print("earnings manipulation. This is for informational purposes only and should not be")
    print("considered financial advice. Further investigation is recommended.")
    print("-"*60)
    
    print("\n" + "="*60)
    print(f"RESULTS / SUMMARY")
    print("="*60)
    
    
    print(f"\nCurrent Year ({current_year}) M-Score: {current_m_score:.4f}")
    print(f"Prior Year ({prior_year}) M-Score: {prior_m_score:.4f}")
    print(f"Threshold: -1.78")
    
    if current_m_score > prior_m_score:
        change_str = f"Increased by {current_m_score - prior_m_score:.4f}"
        change_interpretation = "higher"
    else:
        change_str = f"Decreased by {prior_m_score - current_m_score:.4f}"
        change_interpretation = "lower"
    
    print(f"Change: {change_str}")
    print(f"The M-Score has {change_str.lower()}, indicating a {change_interpretation} likelihood of earnings manipulation in the current period.")
    
def main():
    # Allow user to select a ticker
    default_ticker = "NVDA"
    user_ticker = input(f"Enter ticker symbol (default: {default_ticker}): ").strip().upper()
    ticker = user_ticker if user_ticker else default_ticker
    
    # Fetch data
    data = fetch_financial_data(ticker)
    
    if data:
        try:
            # Calculate M-Score for current period (t vs t-1)
            current_m_score, current_components, current_weighted = calculate_m_score(data, "t", "t-1")
            current_interpretation = interpret_m_score(current_m_score, current_components)
            
            # Calculate M-Score for prior period (t-1 vs t-2)
            prior_m_score, prior_components, prior_weighted = calculate_m_score(data, "t-1", "t-2")
            prior_interpretation = interpret_m_score(prior_m_score, prior_components)
            
            # Get the actual years from the data (if available, otherwise use generic labels)
            try:
                current_year = f"Current Period"
                prior_year = f"Prior Period"
            except:
                current_year = "Current Period"
                prior_year = "Prior Period"
            
            # Print year-over-year comparison
            print_comparison(current_year, prior_year, current_m_score, prior_m_score, 
                            current_components, prior_components, 
                            current_weighted, prior_weighted)   
    
            # Print detailed reports for both periods
            print_report(current_year, ticker, current_m_score, current_components, current_weighted, current_interpretation)
            print_report(prior_year, ticker, prior_m_score, prior_components, prior_weighted, prior_interpretation)
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            print("This might be due to incomplete or inconsistent financial data.")
    else:
        print(f"Unable to calculate Beneish M-Score for {ticker} due to insufficient data. This problem is especially present for Banks.")
        print("Try another ticker or check if the company has complete financial statements available.")

if __name__ == "__main__":
    main()


# In[ ]:




