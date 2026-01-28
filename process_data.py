import pandas as pd
import numpy as np
import os

# 1. Load Data
try:
    # Use absolute path to be safe in GitHub Actions
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'nifty50_sectors.csv')
    
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # ---------------------------------------------------------
    # 1.1 THE FIX: RENAME 'Close' TO 'Price'
    # ---------------------------------------------------------
    if 'Close' in df.columns:
        df.rename(columns={'Close': 'Price'}, inplace=True)
    elif 'Adj Close' in df.columns:
        df.rename(columns={'Adj Close': 'Price'}, inplace=True)
        
    if 'Price' not in df.columns:
        print(f"❌ Error: Still cannot find 'Price' column. Available columns: {df.columns.tolist()}")
        exit(1)

    df.sort_values(['Ticker', 'Date'], inplace=True)
    print("✅ Raw Data Loaded & Renamed Successfully")

except FileNotFoundError:
    print("❌ Raw data not found. Run fetch_data.py first.")
    exit(1)

# ---------------------------------------------------------
# 2. CALCULATE RISK (Volatility)
# ---------------------------------------------------------
df['Daily_Return'] = df.groupby('Ticker')['Price'].pct_change()

risk_profile = df.groupby(['Ticker', 'Sector'])['Daily_Return'].std() * np.sqrt(252) * 100
risk_profile = risk_profile.reset_index()
risk_profile.columns = ['Ticker', 'Sector', 'Volatility_Annual_Pct']

avg_return = df.groupby('Ticker')['Daily_Return'].mean() * 252 * 100
risk_profile['Return_Annual_Pct'] = avg_return.values.round(2)
risk_profile['Volatility_Annual_Pct'] = risk_profile['Volatility_Annual_Pct'].round(2)

risk_path = os.path.join(base_dir, 'data', 'stock_risk.csv')
risk_profile.to_csv(risk_path, index=False)
print("✅ Risk Profile Saved")

# ---------------------------------------------------------
# 3. CALCULATE SIGNALS (MA50)
# ---------------------------------------------------------
df['MA50'] = df.groupby('Ticker')['Price'].transform(lambda x: x.rolling(window=50).mean())

latest_date = df['Date'].max()
signals = df[df['Date'] == latest_date].copy()

signals['MA_Diff_Pct'] = ((signals['Price'] - signals['MA50']) / signals['MA50'] * 100).round(2)

conditions = [
    (signals['MA_Diff_Pct'] > 2),
    (signals['MA_Diff_Pct'] > 0),
    (signals['MA_Diff_Pct'] < -2),
    (signals['MA_Diff_Pct'] < 0)
]
choices = ['Strong Bullish 🚀', 'Weak Bullish ↗️', 'Strong Bearish 🩸', 'Weak Bearish ↘️']
signals['Trend'] = np.select(conditions, choices, default='Neutral')

signals_path = os.path.join(base_dir, 'data', 'stock_signals.csv')
signals[['Ticker', 'Price', 'MA50', 'MA_Diff_Pct', 'Trend']].to_csv(signals_path, index=False)
print("✅ Signals Saved")

# ---------------------------------------------------------
# 4. CALCULATE GROWTH (Leaderboard) - FIXED
# ---------------------------------------------------------
# We use .transform() here to ensure the index matches the original dataframe
df['Cumulative_Growth'] = df.groupby('Ticker')['Daily_Return'].transform(lambda x: (1 + x).cumprod())
df['Investment_Value_Numeric'] = (df['Cumulative_Growth'] * 100000).round(0)

growth_path = os.path.join(base_dir, 'data', 'stock_growth.csv')
df[['Date', 'Ticker', 'Investment_Value_Numeric']].to_csv(growth_path, index=False)
print("✅ Growth Data Saved")

# ---------------------------------------------------------
# 5. CALCULATE CORRELATION MATRIX
# ---------------------------------------------------------
pivot_df = df.pivot(index='Date', columns='Ticker', values='Daily_Return')
corr_matrix = pivot_df.corr()

corr_path = os.path.join(base_dir, 'data', 'stock_correlation.csv')
corr_matrix.to_csv(corr_path)
print("✅ Correlation Matrix Saved")