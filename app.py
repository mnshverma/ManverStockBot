import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

TRIGGER_PARAM = "manver_agent_8am"

NIFTY50_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS",
    "LTV.NS", "SBIN.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "NTPC.NS",
    "KOTAKBANK.NS", "ITC.NS", "ONGC.NS", "LT.NS", "AXISBANK.NS",
    "ADANIPORTS.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "POWERGRID.NS", "COALINDIA.NS", "GRASIM.NS", "ASIANPAINT.NS",
    "HDFCLIFE.NS", "DIVISLAB.NS", "ADANIENSOL.NS", "WIPRO.NS", "CIPLA.NS",
    "TATASTEEL.NS", "DRREDDY.NS", "TECHM.NS", "SHREECEM.NS", "BPCL.NS",
    "TATAMOTORS.NS", "BRITANNIA.NS", "EICHERMOT.NS", "ADANIGREEN.NS", "SBILIFE.NS",
    "SRTYRE.NS", "BANKBARODA.NS", "INDUSINDBK.NS", "IDEA.NS", "GAIL.NS",
    "NAVINFLUOR.NS", "M&M.NS", "CHOLAFIN.NS", "IOC.NS", "ABB.NS"
]

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch Nifty 50 stocks data using Yahoo Finance."""
    try:
        tickers = yf.Tickers(NIFTY50_TICKERS)
        
        data = []
        for symbol in NIFTY50_TICKERS:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPreviousClose')
                previous_close = info.get('regularMarketPreviousClose')
                
                if current_price and previous_close:
                    pct_change = ((current_price - previous_close) / previous_close) * 100
                else:
                    pct_change = 0
                
                data.append({
                    'symbol': symbol.replace('.NS', ''),
                    'lastPrice': current_price,
                    'previousClose': previous_close,
                    'perChange': pct_change,
                    'dayHigh': info.get('dayHigh'),
                    'dayLow': info.get('dayLow'),
                    'volume': info.get('volume'),
                    'marketCap': info.get('marketCap')
                })
            except Exception:
                continue
        
        df = pd.DataFrame(data)
        df = df.dropna(subset=['lastPrice', 'perChange'])
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def send_telegram_msg(message):
    """Send Markdown-formatted alert to Telegram."""
    try:
        bot_token = st.secrets.get("BOT_TOKEN")
        chat_id = st.secrets.get("CHAT_ID")
        if not bot_token or not chat_id:
            st.error("Telegram credentials not configured in secrets.toml")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to send Telegram message: {e}")
        return False

def analyze_market(df):
    """Analyze market and generate alerts."""
    if df is None or df.empty:
        return None
    
    df_sorted = df.sort_values(by=["perChange"], ascending=False).reset_index(drop=True)
    
    top_gainers = df_sorted.head(10)
    top_losers = df_sorted.tail(10).iloc[::-1]
    
    avg_change = df_sorted["perChange"].mean()
    
    gap_up_stocks = df_sorted[df_sorted["perChange"] > 1.5]
    gap_down_stocks = df_sorted[df_sorted["perChange"] < -1.5]
    
    below_1000 = df_sorted[df_sorted["lastPrice"] < 1000].sort_values(by=["perChange"], ascending=False)
    
    if avg_change > 0.5:
        sentiment = "Bullish"
    elif avg_change < -0.5:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"
    
    signal = "Buy" if avg_change > 0.5 else "Sell" if avg_change < -0.5 else "Hold"
    
    message = f"📊 *Nifty 50 Market Analysis*\n"
    message += f"_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
    
    message += f"*Market Sentiment:* {sentiment}\n"
    message += f"*Signal:* {signal}\n"
    message += f"*Avg Change:* {avg_change:.2f}%\n\n"
    
    message += f"🟢 *Top 10 Gainers:*\n"
    for i, row in top_gainers.iterrows():
        message += f"  {i+1}. {row['symbol']}: +{row['perChange']:.2f}%\n"
    
    message += f"\n🔴 *Top 10 Losers:*\n"
    for i, row in top_losers.iterrows():
        message += f"  {i+1}. {row['symbol']}: {row['perChange']:.2f}%\n"
    
    if not below_1000.empty:
        message += f"\n💰 *Stocks Below ₹1000:*\n"
        for idx, row in below_1000.head(10).iterrows():
            message += f"  {row['symbol']}: ₹{row['lastPrice']:.2f} ({row['perChange']:.2f}%)\n"
    
    if not gap_up_stocks.empty:
        message += f"\n🚀 *Gap Up >1.5%:* {len(gap_up_stocks)} stocks\n"
    if not gap_down_stocks.empty:
        message += f"\n📉 *Gap Down >1.5%:* {len(gap_down_stocks)} stocks\n"
    
    return message

def main():
    st.set_page_config(page_title="Nifty Monitor", page_icon="📈", layout="wide")
    st.title("📈 Nifty Stock Monitoring Agent")
    
    query_params = st.experimental_get_query_params()
    is_triggered = query_params.get("trigger", [""])[0] == TRIGGER_PARAM
    
    if is_triggered:
        st.info(f"🔔 Running in trigger mode: {TRIGGER_PARAM}")
        
        df = fetch_market_data()
        if df is not None:
            message = analyze_market(df)
            if message:
                success = send_telegram_msg(message)
                if success:
                    st.success("✅ Alert sent successfully to Telegram!")
                else:
                    st.error("❌ Failed to send alert to Telegram.")
            st.text(message)
        else:
            st.error("❌ Could not fetch market data.")
        st.stop()
    
    df = fetch_market_data()
    
    if df is not None:
        df_sorted = df.sort_values(by=["perChange"], ascending=False).reset_index(drop=True)
        
        st.subheader("📊 Nifty 50 Stocks (Sorted by % Change)")
        st.dataframe(
            df_sorted,
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🟢 Top 10 Gainers")
            st.dataframe(df_sorted.head(10), use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("🔴 Top 10 Losers")
            losers = df_sorted.tail(10).iloc[::-1]
            st.dataframe(losers, use_container_width=True, hide_index=True)
        
        with col3:
            avg_change = df_sorted["perChange"].mean()
            sentiment = "Bullish" if avg_change > 0.5 else "Bearish" if avg_change < -0.5 else "Neutral"
            st.metric("Market Sentiment", sentiment, f"{avg_change:.2f}%")
        
        st.subheader("💰 Stocks Below ₹1000")
        below_1000 = df_sorted[df_sorted["lastPrice"] < 1000].sort_values(by=["perChange"], ascending=False)
        st.dataframe(below_1000, use_container_width=True, hide_index=True)
        
        st.subheader("🔔 Manual Trigger")
        if st.button("Send Test Alert to Telegram"):
            message = analyze_market(df)
            if message:
                success = send_telegram_msg(message)
                if success:
                    st.success("✅ Test alert sent successfully!")
                else:
                    st.error("❌ Failed to send test alert.")
    else:
        st.error("Unable to fetch market data. Please try again later.")

if __name__ == "__main__":
    main()