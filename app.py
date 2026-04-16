import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
import math
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

@st.cache_data(ttl=300)
def get_nifty50_data():
    """Stable dashboard fetch with 15-minute tolerance."""
    data = []
    columns = ['symbol', 'price', 'change', 'sector']
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
    return pd.DataFrame(data, columns=columns) if data else pd.DataFrame(columns=columns)

def analyze_sentiment(news):
    if not news: return 0
    pos = ['growth', 'profit', 'surge', 'buy', 'dividend', 'deal', 'expansion', 'up', 'order', 'win']
    neg = ['loss', 'drop', 'slump', 'sell', 'debt', 'down', 'negative', 'layoff', 'crisis', 'fraud']
    score = 0
    for n in news[:5]:
        txt = n.get('title', '').lower()
        score += sum(1 for w in pos if w in txt)
        score -= sum(1 for w in neg if w in txt)
    return score

def get_prediction_engine(s, news_sent=0):
    """Predictive logic with Support/Resistance and Targets."""
    score = 0
    reasons = []
    
    rsi = s.get('rsi', 50)
    if rsi < 35: score += 3; reasons.append("Aggressive Accumulation Zone (RSI)")
    elif rsi > 70: score -= 3; reasons.append("Strict Overbought (Expect Mean Reversion)")
    elif rsi < 55: score += 1; reasons.append("Bullish Trend Continuity")
    
    change = s.get('change', 0)
    if change > 3: score += 2; reasons.append("Momentum Breakout Detected")
    elif change < -3: score -= 2; reasons.append("Support Breakdown / Correction")
    
    if news_sent > 0: score += 2; reasons.append("High Positive Sentiment Flow")
    elif news_sent < -0: score -= 2; reasons.append("Negative News Impacting Price")
    
    # Financial Health heuristic
    pe = s.get('pe', 0)
    if pe and pe < 20 and pe > 0: score += 1; reasons.append("Value Level Valuation")
    
    if score >= 4: res = "🚀 STRONG BUY", score, reasons
    elif score >= 1: res = "📈 BUY", score, reasons
    elif score <= -4: res = "📉 STRONG SELL", score, reasons
    elif score <= -1: res = "⚠️ SELL", score, reasons
    else: res = "⚪ HOLD", score, reasons
    
    # Calculate Targets
    curr = s['price']
    support = curr * 0.95
    target = curr * 1.10
    return res, support, target

def apply_terminal_style():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; color: #f1f5f9; font-family: 'Inter', sans-serif; }
        .p-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; padding: 2.5rem; border-left: 6px solid #3b82f6; box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative; }
        .target-box { background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 15px; margin-top: 20px; display: flex; justify-content: space-around; }
        .live-tag { position: absolute; top: 1.5rem; right: 1.5rem; background: #ef4444; color: white; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; }
        .header { background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 900; text-align: center; margin-bottom: 0px; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Manver Insights LIVE", page_icon="📈", layout="wide")
    apply_terminal_style()
    
    st.markdown('<h1 class="header">Manver Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 2rem;">Next-Gen Integrated Predictive Stock Intelligence</p>', unsafe_allow_html=True)

    # Global Live Search
    query = st.text_input("🔮 Predictive Universal Search", placeholder="Any Ticker (e.g. NCC, RVNL, PAYTM, NVDA)...").strip().upper()
    
    if query:
        with st.spinner(f"AI Fetching LIVE Markets for {query}..."):
            data_found = False
            for s_ticker in [query, f"{query}.NS", f"{query}.BO"]:
                try:
                    ticker = yf.Ticker(s_ticker)
                    # Absolute Live Price
                    live = ticker.history(period="1d", interval="1m")
                    if live.empty: continue
                    hist = ticker.history(period="1y")
                    inf = ticker.info
                    news = ticker.get_news()
                    
                    price = float(live['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else price
                    change = ((price - prev) / prev) * 100
                    
                    # Technicals
                    cls = hist['Close'].dropna()
                    dt = cls.diff()
                    gn, ls = (dt.where(dt>0,0)).rolling(14).mean(), (-dt.where(dt<0,0)).rolling(14).mean()
                    rsi = float((100-(100/(1+(gn/ls)))).iloc[-1]) if not (gn/ls).empty else 50
                    
                    sent = analyze_sentiment(news)
                    (pr, sc, re), sup, tar = get_prediction_engine({'price': price, 'rsi': rsi, 'change': change, 'pe': inf.get('trailingPE')}, sent)
                    
                    st.divider()
                    st.markdown(f"""
                    <div class="p-card">
                        <span class="live-tag">LIVE MARKET</span>
                        <h2 style="margin:0;">{inf.get('longName', query)}</h2>
                        <h1 style="color:{'#4ade80' if 'BUY' in pr else '#f87171' if 'SELL' in pr else '#94a3b8'}; margin: 15px 0; font-size: 3rem;">{pr}</h1>
                        <h2 style="margin:0;">₹{price:,.2f} <span style="font-size:1.2rem; color:{'#4ade80' if change > 0 else '#f87171'};">{change:+.2f}%</span></h2>
                        
                        <div class="target-box">
                            <div style="text-align:center;"><div style="color:#94a3b8; font-size:0.8rem;">STOP LOSS</div><div style="color:#f87171; font-weight:bold;">₹{sup:,.2f}</div></div>
                            <div style="text-align:center;"><div style="color:#94a3b8; font-size:0.8rem;">ENTRY ZONE</div><div style="font-weight:bold;">₹{price:,.2f}</div></div>
                            <div style="text-align:center;"><div style="color:#94a3b8; font-size:0.8rem;">PROFIT TARGET</div><div style="color:#4ade80; font-weight:bold;">₹{tar:,.2f}</div></div>
                        </div>

                        <div style="margin-top:20px;">{''.join([f'<span style="background:rgba(59,130,246,0.15); padding:6px 15px; border-radius:20px; font-size:0.85rem; border:1px solid rgba(59,130,246,0.3); margin-right:10px; margin-top:10px; display:inline-block;">{ri}</span>' for ri in re])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1.8, 1])
                    with c1:
                        st.subheader("Interactive Forecast Chart")
                        hp = hist.iloc[-126:]
                        hp['MA50'] = hist['Close'].rolling(50).mean()
                        fig = make_subplots(rows=1, cols=1)
                        fig.add_trace(go.Candlestick(x=hp.index, open=hp['Open'], high=hp['High'], low=hp['Low'], close=hp['Close'], name="Price"))
                        fig.add_trace(go.Scatter(x=hp.index, y=hp['MA50'], line=dict(color='#fbbf24', width=2), name="Breakout Trend (50 DMA)"))
                        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.subheader("Intelligence Feed")
                        if news:
                            for i in news[:5]:
                                st.write(f"**{i['title']}**")
                                st.caption(f"{i['publisher']} | [Open News]({i['link']})")
                                st.divider()
                        else: st.info("No recent news events found.")
                    data_found = True
                    break
                except: continue
            if not data_found: st.error("Stock not found. Try a different ticker format.")

    # Dashboard Snapshot
    st.divider()
    st.subheader("🌐 Indian Market Snapshot (Nifty 50)")
    df = get_nifty50_data()
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top Gainers**")
            st.dataframe(df.sort_values('change', ascending=False).head(5), hide_index=True, use_container_width=True)
        with col2:
            st.markdown("**Top Losers**")
            st.dataframe(df.sort_values('change').head(5), hide_index=True, use_container_width=True)
    else:
        st.warning("Market Snapshot unavailable. Global Search is active.")

if __name__ == "__main__":
    main()
