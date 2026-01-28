

# 📈 Nifty 50 Quantitative Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://indian-stock-market-rqezpfkhqcxv866hheb6s7.streamlit.app/)
[![Daily Pipeline](https://github.com/nbx0021/indian-stock-market/actions/workflows/daily_run.yml/badge.svg)](https://github.com/nbx0021/indian-stock-market/actions)

A fully automated End-to-End Data Engineering pipeline that fetches Nifty 50 stock data, performs quantitative risk/return analysis, and visualizes actionable trading signals.

**🔗 Live Dashboard:** [Click Here to View App](https://indian-stock-market-rqezpfkhqcxv866hheb6s7.streamlit.app/)

---

## 🏗️ Architecture

The pipeline follows a modern **CI/CD (Continuous Integration/Continuous Deployment)** workflow:

```
graph LR
    A[Yahoo Finance API] -->|Fetch| B(GitHub Actions);
    B -->|Process (Pandas/NumPy)| C{Data Transformation};
    C -->|Save CSVs| D[GitHub Repository];
    D -->|Trigger| E[Streamlit Cloud];
    E -->|Visualize| F[Live Dashboard];

```

## 🚀 The Engineering Journey: From Spark to Serverless

This project evolved in two distinct phases to optimize for cost and automation.

### **Phase 1: Exploration & Analysis (Databricks + PySpark)**

* **Goal:** rigorous EDA (Exploratory Data Analysis) and handling potential big data scale.
* **Tech:** Databricks Community Edition, PySpark.
* **Process:**
* Ingested raw stock data into Spark DataFrames.
* Used `pyspark.sql.window` functions to calculate Moving Averages and Volatility.
* Performed heavy correlation matrix calculations using `VectorAssembler`.
* *Outcome:* Validated the mathematical models and "Quant" logic.



### **Phase 2: Production Automation (GitHub Actions + Pandas)**

* **Goal:** Complete "Set It and Forget It" automation without manual cluster management.
* **Tech:** GitHub Actions, Python (Pandas/NumPy), Streamlit.
* **The Shift:** * Since the daily Nifty 50 dataset is lightweight (<1GB), spinning up a Spark cluster daily was inefficient.
* I ported the validated Spark logic to **Pandas/NumPy** for execution inside a standard CI/CD runner.
* **Result:** The pipeline now runs automatically every day at 4:00 PM IST (Market Close), costing ₹0 and requiring 0 manual intervention.



---

## 📊 Key Features

1. **🚦 Actionable Signals:**
* Identifies Bullish/Bearish trends using a **50-Day Moving Average Crossover** strategy.
* Calculates "Signal Strength" (Distance from MA).


2. **⚖️ Risk Profile:**
* Annualized Volatility vs. Annualized Return scatter plot.
* Helps identify "High Risk / High Reward" stocks vs. "Stable" defenders.


3. **💰 Growth Leaderboard:**
* Simulates a ₹1,00,000 investment over the last 5 years.
* Tracks the cumulative wealth generation of top performers.


4. **🔗 Correlation Matrix:**
* Heatmap showing how sectors move together (crucial for portfolio diversification).



---

## 🛠️ Tech Stack

* **Data Source:** `yfinance` (Yahoo Finance API)
* **Automation:** GitHub Actions (YAML Workflows)
* **Processing:** Python, Pandas, NumPy
* **Visualization:** Streamlit, Plotly Express
* **Version Control:** Git

---

## 💻 How to Run Locally

1. **Clone the repository:**
```bash
git clone [https://github.com/nbx0021/indian-stock-market.git](https://github.com/nbx0021/indian-stock-market.git)
cd indian-stock-market

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the dashboard:**
```bash
streamlit run app.py

```



---

## 🤖 Automation Workflow

The project uses `.github/workflows/daily_run.yml` to orchestrate the daily update:

1. **Trigger:** Cron schedule (`30 10 * * *` = 4:00 PM IST).
2. **Fetch:** Runs `fetch_data.py` to get latest closing prices.
3. **Process:** Runs `process_data.py` to recalculate indicators.
4. **Commit:** The "GitHub Action Bot" pushes the new CSV files to the repo.
5. **Deploy:** Streamlit detects the commit and refreshes the live site.

```
