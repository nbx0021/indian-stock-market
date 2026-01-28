import pandas as pd
import numpy as np
import os

# 1. Load Data
try:
    df = pd.read_csv('data/nifty50_sectors.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(['Ticker', 'Date'], inplace=True)
    print("✅ Raw Data Loaded")
except FileNotFoundError:
    print("❌ Raw data not found. Run fetch_data.py first.")
    exit()

# ---------------------------------------------------------
# 2. CALCULATE RISK (Volatility)
# ---------------------------------------------------------
# Calculate daily returns
df['Daily_Return'] = df.groupby('Ticker')['Price'].pct_change()

# Annualized Volatility (Std Dev * sqrt(252))
risk_profile = df.groupby(['Ticker', 'Sector'])['Daily_Return'].std() * np.sqrt(252) * 100
risk_profile = risk_profile.reset_index()
risk_profile.columns = ['Ticker', 'Sector', 'Volatility_Annual_Pct']

# Annualized Return (Mean * 252)
avg_return = df.groupby('Ticker')['Daily_Return'].mean() * 252 * 100
risk_profile['Return_Annual_Pct'] = avg_return.values.round(2)
risk_profile['Volatility_Annual_Pct'] = risk_profile['Volatility_Annual_Pct'].round(2)

# Save
risk_profile.to_csv('data/stock_risk.csv', index=False)
print("✅ Risk Profile Saved")

# ---------------------------------------------------------
# 3. CALCULATE SIGNALS (MA50)
# ---------------------------------------------------------
# Rolling 50-day average
df['MA50'] = df.groupby('Ticker')['Price'].transform(lambda x: x.rolling(window=50).mean())

# Get latest date
latest_date = df['Date'].max()
signals = df[df['Date'] == latest_date].copy()

# Calculate Strength
signals['MA_Diff_Pct'] = ((signals['Price'] - signals['MA50']) / signals['MA50'] * 100).round(2)

# Determine Trend
conditions = [
    (signals['MA_Diff_Pct'] > 2),
    (signals['MA_Diff_Pct'] > 0),
    (signals['MA_Diff_Pct'] < -2),
    (signals['MA_Diff_Pct'] < 0)
]
choices = ['Strong Bullish 🚀', 'Weak Bullish ↗️', 'Strong Bearish 🩸', 'Weak Bearish ↘️']
signals['Trend'] = np.select(conditions, choices, default='Neutral')

# Save
signals[['Ticker', 'Price', 'MA50', 'MA_Diff_Pct', 'Trend']].to_csv('data/stock_signals.csv', index=False)
print("✅ Signals Saved")

# ---------------------------------------------------------
# 4. CALCULATE GROWTH (Leaderboard)
# ---------------------------------------------------------
# Cumulative Return: (1 + r).cumprod()
df['Cumulative_Growth'] = df.groupby('Ticker')['Daily_Return'].apply(lambda x: (1 + x).cumprod())
df['Investment_Value_Numeric'] = (df['Cumulative_Growth'] * 100000).round(0)

# Save
df[['Date', 'Ticker', 'Investment_Value_Numeric']].to_csv('data/stock_growth.csv', index=False)
print("✅ Growth Data Saved")

# ---------------------------------------------------------
# 5. CALCULATE CORRELATION MATRIX
# ---------------------------------------------------------
pivot_df = df.pivot(index='Date', columns='Ticker', values='Daily_Return')
corr_matrix = pivot_df.corr()

# Save
corr_matrix.to_csv('data/stock_correlation.csv')
print("✅ Correlation Matrix Saved")