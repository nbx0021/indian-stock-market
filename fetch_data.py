import yfinance as yf
import pandas as pd
import os

# 1. Define the "Market Basket" (Top 2 stocks per sector)
# Note: We use ".NS" for NSE (National Stock Exchange) symbols
# Corrected Ticker List
tickers = {
    'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS'],
    'IT': ['TCS.NS', 'INFY.NS'],
    'Oil_Gas': ['RELIANCE.NS', 'ONGC.NS'],
    'FMCG': ['HINDUNILVR.NS', 'ITC.NS'],
    'Auto': ['TMPV.NS', 'M&M.NS']
}

print("🚀 Starting Data Fetch for Nifty 50 Sectors...")

all_data = []

# 2. Loop through each sector and ticker
for sector, stock_list in tickers.items():
    for ticker in stock_list:
        print(f"  Downloading: {ticker} ({sector})...")

        # Download 5 years of history
        # Fix: Explicitly set auto_adjust=False to ensure 'Adj Close' column is included
        df = yf.download(ticker, period="5y", interval="1d", progress=False, auto_adjust=False)

        # 3. Data Engineering (Add Metadata)
        if len(df) > 0:
            # yfinance returns a MultiIndex column structure in newer versions.
            # We flatten it to keep it simple.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['Ticker'] = ticker
            df['Sector'] = sector
            df.reset_index(inplace=True) # Make Date a normal column

            # Select only columns we need
            cols = ['Date', 'Ticker', 'Sector', 'Close', 'Adj Close', 'Volume']
            df = df[cols]

            all_data.append(df)

# 4. Merge into one Master DataFrame
if all_data:
    final_df = pd.concat(all_data)

    # Create a 'data' folder if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save to CSV
    file_path = 'data/nifty50_sectors.csv'
    final_df.to_csv(file_path, index=False)

    print(f"\n✅ Success! Saved {len(final_df)} rows to '{file_path}'")
    print(final_df.head())
else:
    print("\n❌ Error: No data fetched.")