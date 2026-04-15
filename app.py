import streamlit as st
import requests
import pandas as pd
from nsepython import nse_get_index_stocks
from datetime import datetime

TRIGGER_PARAM = "manver_agent_8am"

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

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch Nifty 50, 100, 200 stocks data with caching."""
    indices = ["NIFTY 50", "NIFTY 100", "NIFTY 200"]
    all_dfs = []
    
    for index_name in indices:
        try:
            df = nse_get_index_stocks(index_name)
            if df is not None and not df.empty:
                df["index"] = index_name
                all_dfs.append(df)
        except Exception as e:
            st.warning(f"Could not fetch {index_name}: {e}")
    
    if not all_dfs:
        return None
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["symbol"], keep="first")
    
    return combined_df

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
    
    message = f"📊 *Nifty Market Analysis*\n"
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
        for i, row in below_1000.head(10).iterrows():
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