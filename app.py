import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

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

def get_clean_price(df, col='Close'):
    try:
        data = df[col]
        if isinstance(data, pd.DataFrame): data = data.iloc[:, 0]
        val = data.dropna().iloc[-1]
        if hasattr(val, '__iter__') and not isinstance(val, (str, bytes)): val = val[0]
        return float(val)
    except: return None

@st.cache_data(ttl=1800)
def get_snapshot():
    try:
        df_batch = yf.download(NIFTY50_TICKERS, period="5d", progress=False)
        data = []
        for s in NIFTY50_TICKERS:
            try:
                close_s = df_batch['Close'][s] if s in df_batch['Close'] else None
                if close_s is not None:
                    cp = float(close_s.dropna().iloc[-1])
                    pp = float(close_s.dropna().iloc[-2])
                    data.append({'Symbol': s.replace('.NS',''), 'Price': round(cp,2), 'Change': round(((cp-pp)/pp)*100, 2)})
            except: continue
        return pd.DataFrame(data)
    except: return pd.DataFrame()

def main():
    st.set_page_config(page_title="Manver Insights", layout="wide")
    st.markdown('<h1 style="text-align:center; color:#60a5fa; font-weight:800; font-size:3.5rem;">Manver Insights</h1>', unsafe_allow_html=True)

    if 'search_data' not in st.session_state: st.session_state.search_data = None
    if 'last_q' not in st.session_state: st.session_state.last_q = ""

    q = st.text_input("🔍 Global Predictive Search", placeholder="ZOMATO, TCS, NCC...").upper().strip()
    
    if q and q != st.session_state.last_q:
        st.session_state.last_q = q
        st.session_state.search_data = None # Clear old results!
        found = False
        for sym in [f"{q}.NS", q, f"{q}.BO"]:
            try:
                df = yf.download(sym, period="1y", progress=False)
                if not df.empty and len(df) > 1:
                    st.session_state.search_data = {'df': df, 'ticker': sym} # Consistent key
                    found = True
                    break
            except: continue
        if not found: st.warning("Ticker not discovered.")

    if st.session_state.search_data:
        sd = st.session_state.search_data
        df = sd['df']
        t_name = sd.get('ticker', q) # Fallback handling
        
        p = get_clean_price(df, 'Close')
        if p is not None:
            try:
                c_series = df['Close']
                if isinstance(c_series, pd.DataFrame): c_series = c_series.iloc[:, 0]
                pp = float(c_series.dropna().iloc[-2])
                chg = ((p-pp)/pp)*100
                
                diff = c_series.diff()
                g = diff.where(diff > 0, 0).rolling(14).mean()
                l = (-diff.where(diff < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (g/l).iloc[-1])) if not (g/l).empty else 50
                pred = "🚀 STRONG BUY" if rsi < 35 else "📈 BUY" if rsi < 50 else "📉 SELL" if rsi > 70 else "⚪ HOLD"
                
                st.markdown(f"""
                <div style="background:#1e293b; padding:30px; border-radius:15px; border-left:8px solid #3b82f6;">
                    <h3 style="margin:0;">{t_name}</h3>
                    <h1 style="color:{'#4ade80' if 'BUY' in pred else '#f87171' if 'SELL' in pred else 'white'}; margin:15px 0;">{pred}</h1>
                    <h2 style="margin:0;">₹{p:,.2f} <span style="font-size:1.2rem; color:{'#4ade80' if chg > 0 else '#f87171'};">{chg:+.2f}%</span></h2>
                </div>
                """, unsafe_allow_html=True)
                
                fig = go.Figure(go.Candlestick(x=df.index[-120:], open=df['Open'].iloc[-120:].values.flatten(), high=df['High'].iloc[-120:].values.flatten(), low=df['Low'].iloc[-120:].values.flatten(), close=df['Close'].iloc[-120:].values.flatten()))
                fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.error("Error visualizing data. Try refreshing.")

    st.divider()
    st.subheader("📊 Indian Market snapshot")
    snap = get_snapshot()
    if not snap.empty:
        st.dataframe(snap.sort_values('Change', ascending=False), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
