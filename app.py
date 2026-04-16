import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Secret Keys
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

@st.cache_data(ttl=300)
def get_nifty50_data():
    """Cached for dashboard stability but limited to 5 mins."""
    data = []
    for s in NIFTY50_TICKERS:
        try:
            t = yf.Ticker(s)
            h = t.history(period="5d")
            if h.empty: continue
            inf = t.info
            cp = float(h['Close'].iloc[-1])
            pp = float(h['Close'].iloc[-2])
            data.append({
                'symbol': s.replace('.NS',''),
                'price': cp,
                'change': ((cp-pp)/pp)*100,
                'sector': inf.get('sector', 'N/A')
            })
        except: continue
    return pd.DataFrame(data)

def analyze_sentiment(news):
    if not news: return 0
    pos = ['growth', 'profit', 'surge', 'buy', 'dividend', 'deal', 'expansion', 'up']
    neg = ['loss', 'drop', 'slump', 'sell', 'debt', 'down', 'negative', 'crisis']
    score = 0
    for n in news[:5]:
        txt = n.get('title', '').lower()
        score += sum(1 for w in pos if w in txt)
        score -= sum(1 for w in neg if w in txt)
    return score

def get_prediction(s, sent=0):
    score = 0
    reasons = []
    rsi = s.get('rsi', 50)
    if rsi < 35: score += 3; reasons.append("Oversold (RSI)")
    elif rsi > 70: score -= 3; reasons.append("Overbought (RSI)")
    
    change = s.get('change', 0)
    if change > 2: score += 2; reasons.append("Price Breakthrough")
    elif change < -2: score -= 2; reasons.append("Price Correction")
    
    if sent > 0: score += 2; reasons.append("Positive Sentiment")
    elif sent < 0: score -= 2; reasons.append("Negative News")
    
    if score >= 3: return "🚀 STRONG BUY", score, reasons
    elif score >= 1: return "📈 BUY", score, reasons
    elif score <= -3: return "📉 STRONG SELL", score, reasons
    elif score <= -1: return "⚠️ SELL", score, reasons
    else: return "⚪ HOLD", score, reasons

def apply_style():
    st.markdown("""
        <style>
        .stApp { background: #0b0f19; color: #f8fafc; font-family: 'Inter', sans-serif; }
        .p-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; border-left: 5px solid #3b82f6; margin-top: 10px; }
        .live-badge { background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-left: 10px; }
        .header { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 3rem; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Manver Insights LIVE", page_icon="📈", layout="wide")
    apply_style()
    
    st.markdown('<h1 class="header">Manver Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">High-Frequency Predictive Stock Analysis</p>', unsafe_allow_html=True)

    # Search Bar - NO CACHE for Search
    q = st.text_input("🔍 Search any Stock (e.g. NCC, RECLTD, ZOMATO, AAPL)", "").strip().upper()
    
    if q:
        with st.spinner(f"Fetching LIVE Data for {q}..."):
            found = False
            for sym in [q, f"{q}.NS", f"{q}.BO"]:
                try:
                    ticker = yf.Ticker(sym)
                    # Use period="1d", interval="1m" for the absolute latest price
                    latest = ticker.history(period="1d", interval="1m")
                    if latest.empty: continue
                    
                    hist = ticker.history(period="6mo") # For logic
                    inf = ticker.info
                    news = ticker.get_news()
                    
                    price = float(latest['Close'].iloc[-1])
                    prev_c = float(hist['Close'].iloc[-2]) if len(hist) > 1 else price
                    change = ((price - prev_c) / prev_c) * 100
                    
                    # Sentiment & RSI
                    sent = analyze_sentiment(news)
                    cls = hist['Close'].dropna()
                    dt = cls.diff()
                    gn, ls = (dt.where(dt>0,0)).rolling(14).mean(), (-dt.where(dt<0,0)).rolling(14).mean()
                    rsi = float((100-(100/(1+(gn/ls)))).iloc[-1]) if not (gn/ls).empty else 50
                    
                    pr, sc, re = get_prediction({'rsi': rsi, 'change': change}, sent)
                    
                    st.divider()
                    st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; align-items:center;">
                            <h2 style="margin:0;">{inf.get('longName', q)}</h2>
                            <span class="live-badge">LIVE DATA</span>
                        </div>
                        <h1 style="color:{'#4ade80' if 'BUY' in pr else '#f87171' if 'SELL' in pr else '#94a3b8'}; margin:10px 0;">{pr}</h1>
                        <h3>₹{price:,.2f} <span style="font-size:1rem; color:{'#4ade80' if change > 0 else '#f87171'};">{change:+.2f}%</span></h3>
                        <div style="margin-top:10px;">{' '.join([f'<span style="background:rgba(255,255,255,0.1); padding:4px 10px; border-radius:10px; font-size:0.8rem; margin-right:5px;">{r}</span>' for r in re])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig = go.Figure(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="History"))
                        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.subheader("📰 Recent Headlines")
                        for n in news[:4]:
                            st.write(f"**{n['title']}**")
                            st.caption(f"{n['publisher']} | [Open News]({n['link']})")
                            st.divider()
                    found = True
                    break
                except: continue
            if not found: st.error("Stock not found or Market data delayed.")

    # Dashboard Snapshot
    st.divider()
    st.subheader("🌐 Indian Market Snapshot")
    df = get_nifty50_data()
    if df is not None:
        col1, col2 = st.columns(2)
        col1.dataframe(df.sort_values('change', ascending=False).head(5), hide_index=True, use_container_width=True)
        col2.dataframe(df.sort_values('change').head(5), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
