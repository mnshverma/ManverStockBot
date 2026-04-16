import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

TRIGGER_PARAM = "manver_agent_8am"

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

@st.cache_data(ttl=1800)
def get_snapshot():
    try:
        # Use a flat download for dashboard to avoid MultiIndex issues
        df_batch = yf.download(NIFTY50_TICKERS, period="2d", progress=False)
        data = []
        for s in NIFTY50_TICKERS:
            try:
                # Handle MultiIndex if present
                if isinstance(df_batch.columns, pd.MultiIndex):
                    # MultiIndex columns are (Metric, Ticker)
                    cp = df_batch['Close'][s].iloc[-1]
                    pp = df_batch['Close'][s].iloc[-2]
                else:
                    continue # Should be MultiIndex for batch
                data.append({'Symbol': s.replace('.NS',''), 'Price': round(float(cp),2), 'Change': round(((cp-pp)/pp)*100, 2)})
            except: continue
        return pd.DataFrame(data)
    except: return pd.DataFrame()

def apply_ui():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; color: white; font-family: 'Inter', sans-serif; }
        .p-card { background: #1e293b; border-radius: 15px; padding: 25px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
        .h-title { font-weight: 800; font-size: 3rem; text-align: center; color: #60a5fa; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Manver Insights", layout="wide")
    apply_ui()
    st.markdown('<h1 class="h-title">Manver Insights</h1>', unsafe_allow_html=True)

    if 'last_search' not in st.session_state: st.session_state.last_search = ""
    if 'search_data' not in st.session_state: st.session_state.search_data = None

    q = st.text_input("🔍 Predictive Search", placeholder="e.g. TCS, NCC, ZOMATO").upper().strip()
    
    if q and q != st.session_state.last_search:
        st.session_state.search_data = None
        st.session_state.last_search = q
        found = False
        # Use Ticker.history for search - more stable for single stock objects
        for s_ticker in [f"{q}.NS", q, f"{q}.BO"]:
            try:
                t = yf.Ticker(s_ticker)
                df = t.history(period="1y")
                if not df.empty and len(df) > 1:
                    st.session_state.search_data = {'df': df, 'ticker': s_ticker}
                    found = True
                    break
            except: continue
        if not found: st.warning("Ticker not found.")

    if st.session_state.search_data:
        sd = st.session_state.search_data
        df = sd['df']
        # Convert to float safely
        p = float(df['Close'].iloc[-1])
        pp = float(df['Close'].iloc[-2])
        chg = ((p-pp)/pp)*100
        
        # Simple Prediction Logic
        delta = df['Close'].diff()
        gn, ls = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gn/ls).iloc[-1])) if not (gn/ls).empty else 50
        pred = "🚀 STRONG BUY" if rsi < 35 else "📈 BUY" if rsi < 50 else "📉 SELL" if rsi > 70 else "⚪ HOLD"
        
        st.markdown(f"""
        <div class="p-card">
            <h3>{sd['ticker']}</h3>
            <h1 style="color:{'#4ade80' if 'BUY' in pred else '#f87171' if 'SELL' in pred else 'white'};">{pred}</h1>
            <h2>₹{p:,.2f} <span style="color:{'#4ade80' if chg > 0 else '#f87171'};">{chg:+.2f}%</span></h2>
            <p>RSI: {rsi:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Candlestick(x=df.index[-120:], open=df['Open'][-120:], high=df['High'][-120:], low=df['Low'][-120:], close=df['Close'][-120:]))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📊 Market Snapshot")
    snap = get_snapshot()
    if not snap.empty:
        st.dataframe(snap.sort_values('Change', ascending=False).head(10), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
