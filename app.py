import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Nifty 50 Quant Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Nifty 50 Quantitative Dashboard")
st.caption(
    "Automated pipeline: **GitHub Actions → Databricks (Spark) → Streamlit**"
)

# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data():
    signals = pd.read_csv("data/stock_signals.csv")
    risk = pd.read_csv("data/stock_risk.csv")
    corr = pd.read_csv("data/stock_correlation.csv", index_col=0)
    growth = pd.read_csv("data/stock_growth.csv")

    growth["Date"] = pd.to_datetime(growth["Date"])
    return signals, risk, corr, growth


try:
    df_signals, df_risk, df_corr, df_growth = load_data()
except Exception as e:
    st.error("❌ Unable to load data. Please run the pipeline.")
    st.stop()

# ---------------------------------------------------
# SIDEBAR (CONTROLS)
# ---------------------------------------------------
st.sidebar.header("⚙️ Dashboard Controls")

sector_filter = st.sidebar.multiselect(
    "Select Sector(s)",
    options=sorted(df_risk["Sector"].unique()),
    default=sorted(df_risk["Sector"].unique())
)

trend_filter = st.sidebar.multiselect(
    "Select Trend",
    options=sorted(df_signals["Trend"].unique()),
    default=sorted(df_signals["Trend"].unique())
)

# Apply filters
df_signals_f = df_signals[
    (df_signals["Trend"].isin(trend_filter))
]

df_risk_f = df_risk[
    (df_risk["Sector"].isin(sector_filter))
]

# ---------------------------------------------------
# SECTION 1: KPIs
# ---------------------------------------------------
st.markdown("## 🚦 Market Overview")

col1, col2, col3, col4 = st.columns(4)

bullish = df_signals_f["Trend"].str.contains("Bullish").sum()
bearish = df_signals_f["Trend"].str.contains("Bearish").sum()
neutral = len(df_signals_f) - bullish - bearish

top_pick = (
    df_signals_f.sort_values("MA_Diff_Pct", ascending=False)
    .iloc[0]
    if not df_signals_f.empty
    else None
)

col1.metric("Bullish Stocks", bullish, "Momentum ↑")
col2.metric("Bearish Stocks", bearish, "Momentum ↓", delta_color="inverse")
col3.metric("Neutral", neutral, "Sideways")
if top_pick is not None:
    col4.metric(
        "Top Momentum",
        top_pick["Ticker"],
        f"{top_pick['MA_Diff_Pct']}%"
    )

# ---------------------------------------------------
# SECTION 2: SIGNAL TABLE
# ---------------------------------------------------
st.markdown("## 📋 Trading Signals")

def style_trend(val):
    if "Bullish" in val:
        return "background-color:#d4edda;color:#155724;"
    elif "Bearish" in val:
        return "background-color:#f8d7da;color:#721c24;"
    return "background-color:#fdfdfd;color:black;"


st.dataframe(
    df_signals_f.sort_values("MA_Diff_Pct", ascending=False)
    .style.map(style_trend, subset=["Trend"]),
    use_container_width=True,
    height=420
)

# ---------------------------------------------------
# SECTION 3: RISK VS RETURN
# ---------------------------------------------------
st.markdown("## ⚖️ Risk vs Return Profile")

fig_risk = px.scatter(
    df_risk_f,
    x="Volatility_Annual_Pct",
    y="Return_Annual_Pct",
    size="Volatility_Annual_Pct",
    color="Sector",
    text="Ticker",
    labels={
        "Volatility_Annual_Pct": "Annualized Volatility (%)",
        "Return_Annual_Pct": "Annual Return (%)"
    },
    title="Risk–Return Tradeoff"
)

fig_risk.add_hline(y=0, line_dash="dash", line_color="red")
fig_risk.update_traces(textposition="top center")
fig_risk.update_layout(legend_title_text="Sector")

st.plotly_chart(fig_risk, use_container_width=True)

# ---------------------------------------------------
# SECTION 4: CORRELATION MATRIX
# ---------------------------------------------------
st.markdown("## 🔗 Correlation Matrix")

fig_corr = px.imshow(
    df_corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    title="Inter-Stock Correlation",
    aspect="auto"   # <-- important
)

fig_corr.update_layout(
    height=750,     # <-- makes it BIG
    margin=dict(l=40, r=40, t=80, b=40),
    coloraxis_colorbar=dict(
        title="Correlation",
        len=0.8
    )
)

st.plotly_chart(fig_corr, use_container_width=True)


# ---------------------------------------------------
# SECTION 5: WEALTH GROWTH
# ---------------------------------------------------
st.markdown("## 💰 Wealth Growth Analysis")

top_n = st.slider("Number of Top Momentum Stocks", 3, 10, 5)

top_tickers = (
    df_signals.sort_values("MA_Diff_Pct", ascending=False)
    .head(top_n)["Ticker"]
    .tolist()
)

df_growth_f = df_growth[df_growth["Ticker"].isin(top_tickers)]

fig_growth = px.line(
    df_growth_f,
    x="Date",
    y="Investment_Value_Numeric",
    color="Ticker",
    title="Growth of ₹1,00,000 Investment"
)

fig_growth.update_layout(
    yaxis_title="Portfolio Value (₹)",
    xaxis_title="Date"
)

st.plotly_chart(fig_growth, use_container_width=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("📌 Educational purpose only. Not financial advice.")
st.caption("Developed by Quant Enthusiast. Narendra Bhandari.@2026")