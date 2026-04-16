import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

TRIGGER_PARAM = "manver_agent_8am"

# Hardcoded only for the Snapshot Dashboard
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
    """Fetches Nifty 50 for the bottom snapshot."""
    data = []
    cols = ['Symbol', 'Price', 'Change', 'Sector']
    for s in NIFTY50_TICKERS:
        try:
            t = yf.Ticker(s)
            h = t.history(period="2d")
            if h.empty: continue
            cp = h['Close'].iloc[-1]
            pp = h['Close'].iloc[-2]
            data.append({
                'Symbol': s.replace('.NS',''),
                'Price': round(cp, 2),
                'Change': round(((cp-pp)/pp)*100, 2),
                'Sector': 'Index'
            })
        except: continue
    return pd.DataFrame(data, columns=cols) if data else pd.DataFrame(columns=cols)

def get_sentiment(news):
    if not news: return 0
    p = ['profit', 'growth', 'surge', 'buy', 'expansion', 'up']
    n = ['loss', 'drop', 'slump', 'sell', 'down', 'negative']
    s = 0
    for item in news[:5]:
        tit = item.get('title', '').lower()
        s += sum(1 for w in p if w in tit)
        s -= sum(1 for w in n if w in tit)
    return s

def get_ai_score(price, rsi, change, sent):
    score = 0
    reasons = []
    if rsi < 30: score += 3; reasons.append("Strictly Oversold (Potential Rebound)")
    elif rsi > 70: score -= 3; reasons.append("Overbought (Cool-off expected)")
    if change > 2.5: score += 2; reasons.append("Breakout Momentum")
    if sent > 0: score += 2; reasons.append("Positive News Volume")
    
    if score >= 3: res = "🚀 STRONG BUY"
    elif score >= 1: res = "📈 BUY"
    elif score <= -3: res = "📉 STRONG SELL"
    elif score <= -1: res = "⚠️ SELL"
    else: res = "⚪ HOLD"
    
    return res, score, reasons

def apply_ui():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; color: white; font-family: 'Inter', sans-serif; }
        .p-card { background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.05); border-left: 8px solid #3b82f6; margin-bottom: 25px; }
        .h-title { background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 3.5rem; text-align: center; }
        .live-tag { background: #ef4444; color: white; padding: 3px 10px; border-radius: 5px; font-size: 0.7rem; font-weight: 800; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Manver Insights", page_icon="📈", layout="wide")
    apply_ui()
    
    st.markdown('<h1 class="h-title">Manver Insights</h1>', unsafe_allow_html=True)
    
    # Simple & Robust Search
    q = st.text_input("🔍 Search Any Indian or Global Stock", placeholder="ZOMATO, TCS, NCC, AAPL, BTC-USD").strip().upper()
    
    if q:
        with st.spinner(f"Analyzing {q}..."):
            data = None
            # Try variations to ensure we catch the stock
            for sym in [f"{q}.NS", q, f"{q}.BO"]:
                try:
                    ticker = yf.Ticker(sym)
                    # Use period="5d" to ensure we get a price even if market is closed
                    hist = ticker.history(period="1mo")
                    if hist.empty: continue
                    
                    price = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else price
                    chg = ((price - prev) / prev) * 100
                    
                    # Sentiment & RSI
                    news = ticker.get_news()
                    sent = get_sentiment(news)
                    
                    # RSI Calc
                    dt = hist['Close'].diff()
                    gn = dt.where(dt>0,0).rolling(14).mean()
                    ls = (-dt.where(dt<0,0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gn/ls).iloc[-1])) if not (gn/ls).empty else 50
                    
                    pred, sc, res = get_ai_score(price, rsi, chg, sent)
                    info = ticker.info # Only for the Name if possible
                    
                    st.divider()
                    l_name = info.get('longName', q)
                    st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="margin:0;">{l_name} ({sym})</h2>
                            <span class="live-tag">LIVE PRICE</span>
                        </div>
                        <h1 style="color:{'#4ade80' if 'BUY' in pred else '#f87171' if 'SELL' in pr else 'white'}; font-size: 3.5rem; margin: 15px 0;">{pred}</h1>
                        <h2 style="margin:0;">₹{price:,.2f} <span style="font-size:1.2rem; color:{'#4ade80' if chg > 0 else '#f87171'};">{chg:+.2f}%</span></h2>
                        <div style="margin-top:20px;">
                            {' '.join([f'<span style="background:rgba(59,130,246,0.1); padding:5px 12px; border-radius:15px; font-size:0.8rem; border:1px solid rgba(59,130,246,0.3); margin-right:10px;">{r}</span>' for r in res])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig = go.Figure(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']))
                        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.subheader("Latest Intelligence")
                        if news:
                            for n in news[:5]:
                                st.write(f"**{n['title']}**")
                                st.caption(f"{n['publisher']} | [Open]({n['link']})")
                                st.divider()
                    data = True
                    break
                except: continue
            
            if not data:
                st.error("No data found. If searching for an Indian stock, ensure it is listed on NSE/BSE.")

    st.divider()
    st.subheader("📊 Market Snapshot")
    df = get_dashboard_data()
    if not df.empty:
        st.dataframe(df.sort_values('Change', ascending=False), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
