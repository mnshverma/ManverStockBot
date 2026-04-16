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

@st.cache_data(ttl=1800) # Increased to 30 mins to avoid Rate Limits
def get_snapshot():
    """Fetches Nifty 50 once and caches for 30 minutes."""
    try:
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
    st.set_page_config(page_title="Manver Insights", width='wide' if hasattr(st, 'set_page_config') else None)
    apply_ui()
    st.markdown('<h1 class="h-title">Manver Insights</h1>', unsafe_allow_html=True)

    # Use session state to cache search results locally to avoid re-fetching on UI clicks
    if 'last_search' not in st.session_state: st.session_state.last_search = ""
    if 'search_data' not in st.session_state: st.session_state.search_data = None

    q = st.text_input("🔍 Global Predictive Search", placeholder="e.g. TCS, ZOMATO, AAPL").upper().strip()
    
    # Only fetch if new search or state empty
    if q and q != st.session_state.last_search:
        st.session_state.search_data = None
        st.session_state.last_search = q
        
        found = False
        # Limit attempts to reduce request count
        attempts = [f"{q}.NS", q] # Try NSE then verbatim
        
        for tsym in attempts:
            with st.spinner(f"AI Fetching {tsym}..."):
                try:
                    df = yf.download(tsym, period="1y", progress=False)
                    if not df.empty and len(df) > 1:
                        st.session_state.search_data = {'df': df, 'ticker': tsym}
                        found = True
                        break
                except Exception as e:
                    if "Rate limited" in str(e):
                        st.error("⚠️ Yahoo Finance is rate limiting requests. Please wait a few minutes.")
                        break
                    continue
        if not found and not "Rate limited" in str(st.session_state.get('error', '')):
            st.warning(f"No results for {q}. Try adding exchange suffix (e.g. {q}.NS)")

    # Display cached search results
    if st.session_state.search_data:
        sd = st.session_state.search_data
        df = sd['df']
        p = float(df['Close'].iloc[-1])
        pp = float(df['Close'].iloc[-2])
        chg = ((p-pp)/pp)*100
        
        # Prediction Score Logic
        rsi = 50
        if len(df) > 15:
            delta = df['Close'].diff()
            gn, ls = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gn/ls).iloc[-1]))
        
        pred = "🚀 STRONG BUY" if rsi < 35 else "📈 BUY" if rsi < 50 else "📉 SELL" if rsi > 70 else "⚪ HOLD"
        
        st.divider()
        st.markdown(f"""
        <div class="p-card">
            <h3>{sd['ticker']}</h3>
            <h1 style="color:{'#4ade80' if 'BUY' in pred else '#f87171' if 'SELL' in pred else 'white'};">{pred}</h1>
            <h2>₹{p:,.2f} <span style="color:{'#4ade80' if chg > 0 else '#f87171'};">{chg:+.2f}%</span></h2>
            <div style="margin-top:10px;">
                <span style="background:rgba(255,255,255,0.1); padding:5px 10px; border-radius:10px;">RSI: {rsi:.1f}</span>
                <span style="background:rgba(255,255,255,0.1); padding:5px 10px; border-radius:10px; margin-left:10px;">Decision: {pred}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Candlestick(x=df.index[-120:], open=df['Open'][-120:], high=df['High'][-120:], low=df['Low'][-120:], close=df['Close'][-120:]))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, width='stretch')

    # Snapshot Dashboard
    st.divider()
    st.subheader("🌐 Indian Market Snapshot")
    snap = get_snapshot()
    if not snap.empty:
        st.dataframe(snap.sort_values('Change', ascending=False).head(10), hide_index=True, width='stretch')
    else:
        st.info("Market Snapshot is cooling down to avoid rate limits. Use search for real-time data.")

if __name__ == "__main__":
    main()
