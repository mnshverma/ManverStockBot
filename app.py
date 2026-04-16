import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

TRIGGER_PARAM = "manver_agent_8am"

# Hardcoded for dashboard
NIFTY50_TICKERS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
    "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS",
    "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]

@st.cache_data(ttl=600)
def get_dashboard_data():
    try:
        # Batch download is MUCH faster than individual Tickers
        df_batch = yf.download(NIFTY50_TICKERS, period="2d", group_by='ticker', progress=False)
        data = []
        for s in NIFTY50_TICKERS:
            try:
                hist = df_batch[s]
                if hist.empty: continue
                cp = hist['Close'].iloc[-1]
                pp = hist['Close'].iloc[-2]
                data.append({'Symbol': s.replace('.NS',''), 'Price': round(cp,2), 'Change': round(((cp-pp)/pp)*100, 2)})
            except: continue
        return pd.DataFrame(data)
    except: return pd.DataFrame()

def apply_ui():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; color: white; font-family: 'Inter', sans-serif; }
        .p-card { background: #1e293b; border-radius: 15px; padding: 25px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
        .h-title { background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 3rem; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Manver Insights", layout="wide")
    apply_ui()
    st.markdown('<h1 class="h-title">Manver Insights</h1>', unsafe_allow_html=True)

    # Search Logic - REFACTORED for Maximum Reliability
    q = st.text_input("🔍 Global Predictive Search", placeholder="e.g. TCS, ZOMATO, RELIANCE, AAPL").upper().strip()
    
    if q:
        found = False
        # Try Indian NSE first, then Indian BSE, then verbatim
        attempts = [f"{q}.NS", f"{q}.BO", q]
        
        for ticker_sym in attempts:
            with st.spinner(f"AI Model analyzing {ticker_sym}..."):
                try:
                    df = yf.download(ticker_sym, period="1y", progress=False)
                    if not df.empty and len(df) > 1:
                        price = float(df['Close'].iloc[-1])
                        prev = float(df['Close'].iloc[-2])
                        change = ((price - prev) / prev) * 100
                        
                        # AI Logic (Simple for speed now to fix "no data" issue)
                        rsi = 50 # Default
                        if len(df) > 15:
                            delta = df['Close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                            rsi = 100 - (100 / (1 + (gain/loss).iloc[-1]))
                        
                        pred = "📈 BUY" if rsi < 45 else "📉 SELL" if rsi > 70 else "⚪ HOLD"
                        
                        st.divider()
                        st.markdown(f"""
                        <div class="p-card">
                            <h3>{ticker_sym}</h3>
                            <h1 style="color:{'#4ade80' if 'BUY' in pred else '#f87171' if 'SELL' in pred else 'white'};">{pred}</h1>
                            <h2>₹{price:,.2f} <span style="font-size:1.2rem; color:{'#4ade80' if change > 0 else '#f87171'};">{change:+.2f}%</span></h2>
                            <p>RSI: {rsi:.1f} | Momentum is {'Positive' if change > 0 else 'Negative'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        fig = go.Figure(go.Candlestick(x=df.index[-126:], open=df['Open'][-126:], high=df['High'][-126:], low=df['Low'][-126:], close=df['Close'][-126:]))
                        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)
                        found = True
                        break
                except Exception as e:
                    # Silent fail to try next suffix
                    continue
        
        if not found:
            st.warning(f"Unable to find data for '{q}'. If it is an Indian stock, please try fully qualified ticker (e.g. RELIANCE.NS).")

    st.divider()
    st.subheader("📊 Market Snapshot")
    snap_df = get_dashboard_data()
    if not snap_df.empty:
        st.dataframe(snap_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
