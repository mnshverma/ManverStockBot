import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import math

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
    "APOLLOTYRE.NS", "BANKBARODA.NS", "INDUSINDBK.NS", "IDEA.NS", "GAIL.NS",
    "NAVINFLUOR.NS", "M&M.NS", "CHOLAFIN.NS", "IOC.NS", "ABB.NS"
]

COMPANY_INFO = {
    "RELIANCE": {"company": "Reliance Industries Ltd", "industry": "Conglomerate", "founded": 1960},
    "TCS": {"company": "Tata Consultancy Services Ltd", "industry": "IT Services", "founded": 1968},
    "HDFCBANK": {"company": "HDFC Bank Ltd", "industry": "Banks", "founded": 1994},
    "BHARTIARTL": {"company": "Bharti Airtel Ltd", "industry": "Telecom", "founded": 1995},
    "ICICIBANK": {"company": "ICICI Bank Ltd", "industry": "Banks", "founded": 1994},
    "LTV": {"company": "Larsen & Toubro Ltd", "industry": "Construction", "founded": 1946},
    "SBIN": {"company": "State Bank of India", "industry": "Banks", "founded": 1806},
    "HINDUNILVR": {"company": "Hindustan Unilever Ltd", "industry": "FMCG", "founded": 1933},
    "BAJFINANCE": {"company": "Bajaj Finance Ltd", "industry": "NBFC", "founded": 1992},
    "NTPC": {"company": "NTPC Ltd", "industry": "Power", "founded": 1975},
    "KOTAKBANK": {"company": "Kotak Mahindra Bank Ltd", "industry": "Banks", "founded": 1985},
    "ITC": {"company": "ITC Ltd", "industry": "FMCG", "founded": 1910},
    "ONGC": {"company": "Oil & Natural Gas Corporation Ltd", "industry": "Oil & Gas", "founded": 1956},
    "LT": {"company": "Larsen & Toubro Ltd", "industry": "Construction", "founded": 1946},
    "AXISBANK": {"company": "Axis Bank Ltd", "industry": "Banks", "founded": 1993},
    "ADANIPORTS": {"company": "Adani Ports and SEZ Ltd", "industry": "Services", "founded": 1997},
    "MARUTI": {"company": "Maruti Suzuki India Ltd", "industry": "Automobile", "founded": 1981},
    "TITAN": {"company": "Titan Company Ltd", "industry": "Jewellery", "founded": 1984},
    "SUNPHARMA": {"company": "Sun Pharmaceutical Industries Ltd", "industry": "Pharma", "founded": 1983},
    "ULTRACEMCO": {"company": "UltraTech Cement Ltd", "industry": "Cement", "founded": 2000},
    "NESTLEIND": {"company": "Nestle India Ltd", "industry": "FMCG", "founded": 1866},
    "POWERGRID": {"company": "Power Grid Corporation of India Ltd", "industry": "Power", "founded": 1989},
    "COALINDIA": {"company": "Coal India Ltd", "industry": "Mining", "founded": 1973},
    "GRASIM": {"company": "Grasim Industries Ltd", "industry": "Cement", "founded": 1947},
    "ASIANPAINT": {"company": "Asian Paints Ltd", "industry": "Chemicals", "founded": 1942},
    "HDFCLIFE": {"company": "HDFC Life Insurance Company Ltd", "industry": "Insurance", "founded": 2000},
    "DIVISLAB": {"company": "Divi's Laboratories Ltd", "industry": "Pharma", "founded": 1990},
    "ADANIENSOL": {"company": "Adani Energy Solutions Ltd", "industry": "Power", "founded": 2006},
    "WIPRO": {"company": "Wipro Ltd", "industry": "IT Services", "founded": 1945},
    "CIPLA": {"company": "Cipla Ltd", "industry": "Pharma", "founded": 1935},
    "TATASTEEL": {"company": "Tata Steel Ltd", "industry": "Metal & Mining", "founded": 1907},
    "DRREDDY": {"company": "Dr. Reddy's Laboratories Ltd", "industry": "Pharma", "founded": 1984},
    "TECHM": {"company": "Tech Mahindra Ltd", "industry": "IT Services", "founded": 1986},
    "SHREECEM": {"company": "Shree Cement Ltd", "industry": "Cement", "founded": 1970},
    "BPCL": {"company": "Bharat Petroleum Corporation Ltd", "industry": "Oil & Gas", "founded": 1952},
    "TATAMOTORS": {"company": "Tata Motors Ltd", "industry": "Automobile", "founded": 1945},
    "BRITANNIA": {"company": "Britannia Industries Ltd", "industry": "FMCG", "founded": 1892},
    "EICHERMOT": {"company": "Eicher Motors Ltd", "industry": "Automobile", "founded": 1948},
    "ADANIGREEN": {"company": "Adani Green Energy Ltd", "industry": "Power", "founded": 2015},
    "SBILIFE": {"company": "SBI Life Insurance Company Ltd", "industry": "Insurance", "founded": 2001},
    "APOLLOTYRE": {"company": "Apollo Tyres Ltd", "industry": "Automobile", "founded": 1959},
    "BANKBARODA": {"company": "Bank of Baroda", "industry": "Banks", "founded": 1908},
    "INDUSINDBK": {"company": "IndusInd Bank Ltd", "industry": "Banks", "founded": 1994},
    "IDEA": {"company": "Vodafone Idea Ltd", "industry": "Telecom", "founded": 1995},
    "GAIL": {"company": "GAIL India Ltd", "industry": "Oil & Gas", "founded": 1984},
    "NAVINFLUOR": {"company": "Navin Fluorine International Ltd", "industry": "Chemicals", "founded": 1983},
    "M&M": {"company": "Mahindra & Mahindra Ltd", "industry": "Automobile", "founded": 1945},
    "CHOLAFIN": {"company": "Cholamandalam Investment and Finance Ltd", "industry": "NBFC", "founded": 1978},
    "IOC": {"company": "Indian Oil Corporation Ltd", "industry": "Oil & Gas", "founded": 1964},
    "ABB": {"company": "ABB India Ltd", "industry": "Capital Goods", "founded": 1949}
}

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch Nifty 50 stocks data using Yahoo Finance."""
    try:
        data = []
        for symbol in NIFTY50_TICKERS:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if hist.empty:
                    continue
                
                sym = symbol.replace('.NS', '')
                current_price = float(hist['Close'].iloc[-1])
                previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                pct_change = ((current_price - previous_close) / previous_close) * 100
                day_high = float(hist['High'].max())
                day_low = float(hist['Low'].min())
                
                try:
                    info = ticker.info
                    market_cap = info.get('marketCap')
                    pe_ratio = info.get('trailingPE')
                    pb_ratio = info.get('priceToBook')
                    roe = info.get('returnOnEquity')
                    eps = info.get('trailingEps')
                    beta = info.get('beta')
                    fifty_two_week_high = info.get('fiftyTwoWeekHigh')
                    fifty_two_week_low = info.get('fiftyTwoWeekLow')
                    volume = info.get('volume')
                    avg_volume = info.get('averageVolume')
                    fifty_day_avg = info.get('fiftyDayAverage')
                    two_hundred_day_avg = info.get('twoHundredDayAverage')
                    sector = info.get('sector', '')
                    industry = info.get('industry', COMPANY_INFO.get(sym, {}).get('industry', 'N/A'))
                except:
                    market_cap = pe_ratio = pb_ratio = roe = eps = beta = None
                    fifty_two_week_high = fifty_two_week_low = volume = avg_volume = None
                    fifty_day_avg = two_hundred_day_avg = None
                    sector = industry = None
                
                data.append({
                    'symbol': sym,
                    'company': COMPANY_INFO.get(sym, {}).get("company", sym),
                    'industry': industry,
                    'current_price': current_price,
                    'per_change': pct_change,
                    'change_amount': current_price - previous_close,
                    'open': float(hist['Open'].iloc[-1]),
                    'prev_close': previous_close,
                    'todays_high': day_high,
                    'todays_low': day_low,
                    'week_52_high': fifty_two_week_high,
                    'week_52_low': fifty_two_week_low,
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'fifty_day_avg': fifty_day_avg,
                    'two_hundred_day_avg': two_hundred_day_avg,
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'pb_ratio': pb_ratio,
                    'roe': roe,
                    'eps': eps,
                    'beta': beta,
                    'sector': sector
                })
            except:
                continue
        
        if not data:
            return None
        return pd.DataFrame(data)
    except:
        return None

def format_market_cap(value):
    if not value:
        return "N/A"
    if value >= 1e12:
        return f"₹{value/1e12:.1f}L Cr"
    elif value >= 1e10:
        return f"₹{value/1e10:.1f}K Cr"
    return str(value)

def format_volume(value):
    if not value:
        return "N/A"
    if value >= 1e7:
        return f"{value/1e7:.1f} Cr"
    elif value >= 1e5:
        return f"{value/1e5:.1f} L"
    return str(value)

def get_recommendation(s):
    signals = []
    score = 0
    per_change = s.get('per_change', 0) or 0
    
    if per_change > 1:
        signals.append(("Positive", 2))
        score += 2
    elif per_change > 0:
        signals.append(("Positive", 1))
        score += 1
    elif per_change < -1:
        signals.append(("Negative", -1))
        score -= 1
    
    if s.get('current_price') and s.get('week_52_low') and s.get('week_52_high'):
        price_range = s['week_52_high'] - s['week_52_low']
        if price_range > 0:
            price_position = (s['current_price'] - s['week_52_low']) / price_range
            if price_position < 0.35:
                signals.append(("Near 52W Low", 2))
                score += 2
            elif price_position > 0.75:
                signals.append(("Near 52W High", -1))
                score -= 1
    
    if s.get('fifty_day_avg') and s.get('two_hundred_day_avg'):
        if s['current_price'] > s['fifty_day_avg']:
            signals.append(("Above 50 DMA", 1))
            score += 1
        if s['fifty_day_avg'] > s['two_hundred_day_avg']:
            signals.append(("Golden Cross", 2))
            score += 2
    
    pe = s.get('pe_ratio') or 0
    if 0 < pe < 20:
        signals.append(("Reasonable PE", 1))
        score += 1
    
    roe = s.get('roe') or 0
    if roe > 0.15:
        signals.append(("Good ROE", 1))
        score += 1
    
    if score >= 2:
        action = "🟢 BUY"
    elif score <= -2:
        action = "🔴 SELL"
    else:
        action = "⚪ HOLD"
    
    return {
        "action": action,
        "score": score,
        "signals": signals,
        "reasoning": "; ".join([s[0] for s in signals]) if signals else "Neutral"
    }

@st.cache_data(ttl=1800)
def fetch_stock_news(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        try:
            news = ticker.news
            if news and len(news) > 0:
                return news
        except:
            pass
        try:
            info = ticker.info
        except:
            info = {}
        company_name = info.get('longName', info.get('shortName', symbol))
        return [{
            'title': f"{company_name} - NSE:{symbol}",
            'summary': f"Company: {company_name}",
            'link': f"https://groww.in/stocks/{symbol.lower()}-ltd"
        }]
    except:
        return []

def send_telegram_msg(message, debug=False):
    try:
        bot_token = str(st.secrets.get("BOT_TOKEN", "")).strip()
        chat_id = str(st.secrets.get("CHAT_ID", "")).strip()
        
        if not bot_token or not chat_id:
            return {"success": False, "error": "Credentials missing"}
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=30)
        
        if debug:
            st.write(f"Response: {response.status_code}")
        
        if response.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": response.text[:100]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_prediction_alerts(df):
    """Create ONE compact prediction message."""
    if df is None or df.empty:
        return []
    
    df_sorted = df.sort_values(by=["per_change"], ascending=False).reset_index(drop=True)
    
    predictions = []
    for _, row in df_sorted.iterrows():
        rec = get_recommendation(row)
        symbol = row['symbol']
        current_price = row.get('current_price', 0) or 0
        per_change = row.get('per_change', 0) or 0
        pe = row.get('pe_ratio') or 0
        roe = row.get('roe') or 0
        
        if current_price and current_price > 0 and not math.isnan(current_price):
            if "BUY" in rec['action']:
                target = current_price * 1.1
                stop = current_price * 0.97
            elif "SELL" in rec['action']:
                target = current_price * 0.9
                stop = current_price * 1.03
            else:
                target = current_price * 1.02
                stop = current_price * 0.98
        else:
            target = 0
            stop = 0
        
        predictions.append({
            'symbol': symbol,
            'current_price': current_price,
            'per_change': per_change,
            'action': rec['action'],
            'score': rec.get('score', 0),
            'target': target,
            'stop': stop,
            'pe': pe,
            'roe': roe,
            'signals': rec.get('reasoning', '')
        })
    
    pred_df = pd.DataFrame(predictions)
    bullish = pred_df[pred_df['action'] == '🟢 BUY'].sort_values('score', ascending=False)
    bearish = pred_df[pred_df['action'] == '🔴 SELL'].sort_values('score', ascending=False)
    
    avg_change = df_sorted["per_change"].mean()
    now = datetime.now().strftime('%d-%m-%Y %H:%M')
    
    avg_change = 0 if (math.isnan(avg_change) if isinstance(avg_change, float) else False) else avg_change
    
    msg = f"📊 MANVER INSIGHT - {now}\n\n"
    
    if not bearish.empty:
        msg += f"Bearish\n"
        msg += f"-----------\n\n"
        for _, s in bearish.head(10).iterrows():
            price = s.get('current_price', 0)
            pct = s.get('per_change', 0)
            target = s.get('target', 0)
            stop = s.get('stop', 0)
            pe = s.get('pe', 0)
            roe = s.get('roe', 0)
            signals = s.get('signals', '')
            
            if price and price > 0 and not math.isnan(price):
                msg += f"  🎯 Target: ₹{int(target)} ({((target-price)/price)*100:+-.1f}%)\n"
                msg += f"  🛡️ Stop: ₹{int(stop)} ({((stop-price)/price)*100:+.1f}%)\n"
                msg += f"  ⏱️ 2-4 weeks"
                if pe and not math.isnan(pe) and pe > 0:
                    msg += f" | P/E:{pe:.1f}"
                else:
                    msg += f" | P/E:N/A"
                if roe and not math.isnan(roe) and roe > 0:
                    msg += f" ROE:{roe*100:.0f}%"
                else:
                    msg += f" ROE:N/A"
                msg += f"\n"
                if signals:
                    msg += f"  📊 {signals}\n"
            else:
                msg += f"■ {s['symbol']} (N/A)\n"
    
    if not bullish.empty:
        msg += f"\nBullish\n"
        msg += f"-----------\n\n"
        for _, s in bullish.head(10).iterrows():
            price = s.get('current_price', 0)
            pct = s.get('per_change', 0)
            target = s.get('target', 0)
            stop = s.get('stop', 0)
            pe = s.get('pe', 0)
            roe = s.get('roe', 0)
            signals = s.get('signals', '')
            
            if price and price > 0 and not math.isnan(price):
                msg += f"■ {s['symbol']} ₹{int(price)} ({pct:+.1f}%)\n"
                msg += f"  🎯 Target: ₹{int(target)} ({((target-price)/price)*100:+-.1f}%)\n"
                msg += f"  🛡️ Stop: ₹{int(stop)} ({((stop-price)/price)*100:+.1f}%)\n"
                msg += f"  ⏱️ 2-4 weeks"
                if pe and not math.isnan(pe) and pe > 0:
                    msg += f" | P/E:{pe:.1f}"
                else:
                    msg += f" | P/E:N/A"
                if roe and not math.isnan(roe) and roe > 0:
                    msg += f" ROE:{roe*100:.0f}%"
                else:
                    msg += f" ROE:N/A"
                msg += f"\n"
                if signals:
                    msg += f"  📊 {signals}\n"
            else:
                msg += f"■ {s['symbol']} (N/A)\n"
    
    return [msg]

def create_telegram_alerts(df):
    return create_prediction_alerts(df)

def create_market_news(df):
    """Create market weather news message."""
    if df is None or df.empty:
        return None
    
    avg_change = df["per_change"].mean()
    if math.isnan(avg_change):
        avg_change = 0
    
    gainers = len(df[df['per_change'] > 0])
    losers = len(df[df['per_change'] < 0])
    
    pred_msgs = []
    for _, row in df.iterrows():
        rec = get_recommendation(row)
        pred_msgs.append({
            'symbol': row['symbol'],
            'action': rec['action'],
            'score': rec.get('score', 0)
        })
    
    pred_df = pd.DataFrame(pred_msgs)
    bullish_count = len(pred_df[pred_df['action'] == '🟢 BUY'])
    bearish_count = len(pred_df[pred_df['action'] == '🔴 SELL'])
    
    if bullish_count > bearish_count:
        weather = "BULLISH"
    elif bearish_count > bullish_count:
        weather = "BEARISH"
    else:
        weather = "NEUTRAL"
    
    now = datetime.now().strftime('%d-%m-%Y %H:%M')
    
    msg = f"\n📰 MARKET WEATHER\n"
    msg += f"Date/Time: {now}\n"
    msg += f"Status: {weather}"
    
    return msg

def main():
    st.set_page_config(page_title="ManverInsight", page_icon="📈", layout="wide")
    st.title("📈 ManverInsight")
    
    query_params = st.query_params
    is_triggered = query_params.get("trigger", "") == TRIGGER_PARAM
    
    if is_triggered:
        st.info("🔔 Trigger Mode: Sending predictions...")
        df = fetch_market_data()
        
        if df is not None:
            messages = create_prediction_alerts(df)
            market_news = create_market_news(df)
            
            if market_news and messages:
                messages[0] = messages[0] + "\n\n" + market_news
            
            for i, msg in enumerate(messages):
                st.code(msg[:800], language="markdown")
            
            bot_token = str(st.secrets.get("BOT_TOKEN", "")).strip()
            chat_id = str(st.secrets.get("CHAT_ID", "")).strip()
            
            st.json({"token_len": len(bot_token), "chat_id": chat_id})
            
            sent = 0
            failed = 0
            
            if len(bot_token) > 30 and chat_id.isdigit():
                for msg in messages:
                    result = send_telegram_msg(msg, debug=True)
                    if result.get("success"):
                        sent += 1
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown')}")
                        failed += 1
            else:
                st.warning("⚠️ Check credentials")
            
            st.success(f"✅ Sent: {sent} | Failed: {failed}")
        return
    
    df = fetch_market_data()
    
    if df is None or df.empty:
        st.error("Unable to fetch market data")
        return
    
    df_sorted = df.sort_values(by=["per_change"], ascending=False).reset_index(drop=True)
    
    # Predictions
    predictions = []
    for _, row in df_sorted.iterrows():
        rec = get_recommendation(row)
        predictions.append({
            'symbol': row['symbol'],
            'company': row['company'],
            'current_price': row['current_price'],
            'per_change': row['per_change'],
            'action': rec['action'],
            'score': rec.get('score', 0),
            'target': row['current_price'] * 1.1,
            'stop_loss': row['current_price'] * 0.97,
            'timeframe': '2-4 weeks'
        })
    
    pred_df = pd.DataFrame(predictions)
    pred_bullish = pred_df[pred_df['action'] == '🟢 BUY'].sort_values('score', ascending=False)
    pred_bearish = pred_df[pred_df['action'] == '🔴 SELL'].sort_values('score', ascending=False)
    
    # Main UI
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Stock Detail", "🔔 Alerts"])
    
    with tab1:
        st.subheader("📈 Top Gainers of the Day")
        st.dataframe(df_sorted.head(5)[['symbol', 'company', 'current_price', 'per_change']], use_container_width=True, hide_index=True)
        
        st.subheader("📉 Top Losers of the Day")
        st.dataframe(df_sorted.tail(5)[['symbol', 'company', 'current_price', 'per_change']], use_container_width=True, hide_index=True)
        
        st.subheader("🟢 Predicted BULLISH (May Go Up)")
        if not pred_bullish.empty:
            st.dataframe(pred_bullish[['symbol', 'current_price', 'per_change', 'target', 'timeframe']], hide_index=True)
        
        st.subheader("🔴 Predicted BEARISH (May Go Down)")
        if not pred_bearish.empty:
            st.dataframe(pred_bearish[['symbol', 'current_price', 'per_change', 'target', 'timeframe']], hide_index=True)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        with col1:
            custom_symbol = st.text_input("Enter Stock Symbol (e.g., INFY, SBIN)", "").upper().strip()
        with col2:
            st.write("")
            st.write("")
            use_custom = st.button("Fetch Details", disabled=not custom_symbol)
        
        selected_stock = None
        stock_data = None
        
        if custom_symbol and use_custom:
            with st.spinner("Loading..."):
                try:
                    import time
                    time.sleep(0.3)
                    ticker = yf.Ticker(f"{custom_symbol}.NS")
                    hist = ticker.history(period="2d", timeout=15)
                    
                    if hist.empty:
                        st.error("Stock not found")
                    else:
                        info = ticker.info
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        pct = ((current - prev) / prev) * 100
                        
                        stock_data = {
                            'symbol': custom_symbol,
                            'company': info.get('longName', info.get('shortName', custom_symbol)),
                            'current_price': float(current),
                            'per_change': float(pct),
                            'change_amount': float(current - prev),
                            'open': float(hist['Open'].iloc[-1]),
                            'prev_close': float(prev),
                            'todays_high': float(hist['High'].max()),
                            'todays_low': float(hist['Low'].min()),
                            'week_52_high': info.get('fiftyTwoWeekHigh'),
                            'week_52_low': info.get('fiftyTwoWeekLow'),
                            'volume': info.get('volume'),
                            'avg_volume': info.get('averageVolume'),
                            'fifty_day_avg': info.get('fiftyDayAverage'),
                            'two_hundred_day_avg': info.get('twoHundredDayAverage'),
                            'market_cap': info.get('marketCap'),
                            'pe_ratio': info.get('trailingPE'),
                            'pb_ratio': info.get('priceToBook'),
                            'roe': info.get('returnOnEquity'),
                            'eps': info.get('trailingEps'),
                            'beta': info.get('beta'),
                            'sector': info.get('sector'),
                            'industry': info.get('industry')
                        }
                        selected_stock = custom_symbol
                except Exception as e:
                    err_msg = str(e)[:80]
                    st.error(f"Error: {err_msg}")
        
        if not selected_stock and not stock_data:
            nifty_choice = st.selectbox("Or select from Nifty 50", df_sorted['symbol'].tolist())
            if nifty_choice:
                stock_data = df_sorted[df_sorted['symbol'] == nifty_choice].iloc[0].to_dict()
                selected_stock = nifty_choice
        
        if stock_data:
            s = stock_data
            
            st.metric("Price", f"₹{s['current_price']:.2f}", delta=f"{s['per_change']:+.2f}%")
            rec = get_recommendation(s)
            
            if "BUY" in rec['action']:
                st.success(f"🟢 {rec['action']} - Predicted UP")
            elif "SELL" in rec['action']:
                st.error(f"🔴 {rec['action']} - Predicted DOWN")
            else:
                st.warning(f"⚪ HOLD")
            
            p_tab, f_tab, a_tab, n_tab = st.tabs(["⚡ Performance", "💼 Fundamentals", "🏢 About", "📰 News"])
            
            with p_tab:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**High:**")
                    st.markdown("**52W High:**")
                    st.markdown("**Open:**")
                with c2:
                    st.markdown(f"₹{s.get('todays_high', 0):.2f}")
                    st.markdown(f"₹{s.get('week_52_high', 0):.2f}" if s.get('week_52_high') else "N/A")
                    st.markdown(f"₹{s.get('open', 0):.2f}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Low:**")
                    st.markdown("**52W Low:**")
                    st.markdown("**Prev Close:**")
                with c2:
                    st.markdown(f"₹{s.get('todays_low', 0):.2f}")
                    st.markdown(f"₹{s.get('week_52_low', 0):.2f}" if s.get('week_52_low') else "N/A")
                    st.markdown(f"₹{s.get('prev_close', 0):.2f}")
            
            with f_tab:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Market Cap:**")
                    st.markdown("**P/E:**")
                    st.markdown("**P/B:**")
                with c2:
                    st.markdown(format_market_cap(s.get('market_cap')))
                    st.markdown(f"{s.get('pe_ratio', 'N/A')}")
                    st.markdown(f"{s.get('pb_ratio', 'N/A')}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**ROE:**")
                    st.markdown("**EPS:**")
                with c2:
                    st.markdown(f"{s.get('roe', 0)*100:.1f}%" if s.get('roe') else "N/A")
                    st.markdown(f"₹{s.get('eps', 0):.2f}" if s.get('eps') else "N/A")
            
            with a_tab:
                st.markdown(f"**{s.get('company', s.get('symbol'))}**")
                st.markdown(f"Industry: {s.get('industry', 'N/A')}")
                st.markdown(f"Sector: {s.get('sector', 'N/A')}")
            
            with n_tab:
                if selected_stock:
                    news = fetch_stock_news(selected_stock)
                    if news:
                        for idx, item in enumerate(news[:5]):
                            title = str(item.get("title", ""))[:60] if item.get("title") else "News"
                            summary = str(item.get("summary", ""))[:100] if item.get("summary") else ""
                            st.markdown(f"**{idx+1}.** {title}")
                            if summary:
                                st.caption(summary)
    
    with tab3:
        st.subheader("🔔 Telegram Alerts")
        st.info("Add '?trigger=manver_agent_8am' to URL to send alerts")

if __name__ == "__main__":
    main()
