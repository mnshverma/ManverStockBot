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

COMPANY_INFO = {
    "ADANIENT": {"company": "Adani Enterprises Ltd", "industry": "Conglomerate", "founded": 1988},
    "ADANIPORTS": {"company": "Adani Ports and SEZ Ltd", "industry": "Services", "founded": 1998},
    "APOLLOHOSP": {"company": "Apollo Hospitals Enterprise Ltd", "industry": "Healthcare", "founded": 1983},
    "ASIANPAINT": {"company": "Asian Paints Ltd", "industry": "Chemicals", "founded": 1942},
    "AXISBANK": {"company": "Axis Bank Ltd", "industry": "Banks", "founded": 1993},
    "BAJAJ-AUTO": {"company": "Bajaj Auto Ltd", "industry": "Automobile", "founded": 1945},
    "BAJFINANCE": {"company": "Bajaj Finance Ltd", "industry": "NBFC", "founded": 1987},
    "BAJAJFINSV": {"company": "Bajaj Finserv Ltd", "industry": "NBFC", "founded": 2007},
    "BPCL": {"company": "Bharat Petroleum Corporation Ltd", "industry": "Oil & Gas", "founded": 1952},
    "BHARTIARTL": {"company": "Bharti Airtel Ltd", "industry": "Telecom", "founded": 1995},
    "BRITANNIA": {"company": "Britannia Industries Ltd", "industry": "FMCG", "founded": 1892},
    "CIPLA": {"company": "Cipla Ltd", "industry": "Pharma", "founded": 1935},
    "COALINDIA": {"company": "Coal India Ltd", "industry": "Mining", "founded": 1975},
    "DIVISLAB": {"company": "Divi's Laboratories Ltd", "industry": "Pharma", "founded": 1990},
    "DRREDDY": {"company": "Dr. Reddy's Laboratories Ltd", "industry": "Pharma", "founded": 1984},
    "EICHERMOT": {"company": "Eicher Motors Ltd", "industry": "Automobile", "founded": 1948},
    "GRASIM": {"company": "Grasim Industries Ltd", "industry": "Cement", "founded": 1947},
    "HCLTECH": {"company": "HCL Technologies Ltd", "industry": "IT Services", "founded": 1991},
    "HDFCBANK": {"company": "HDFC Bank Ltd", "industry": "Banks", "founded": 1994},
    "HDFCLIFE": {"company": "HDFC Life Insurance Ltd", "industry": "Insurance", "founded": 2000},
    "HEROMOTOCO": {"company": "Hero MotoCorp Ltd", "industry": "Automobile", "founded": 1984},
    "HINDALCO": {"company": "Hindalco Industries Ltd", "industry": "Metals", "founded": 1958},
    "HINDUNILVR": {"company": "Hindustan Unilever Ltd", "industry": "FMCG", "founded": 1933},
    "ICICIBANK": {"company": "ICICI Bank Ltd", "industry": "Banks", "founded": 1994},
    "INDUSINDBK": {"company": "IndusInd Bank Ltd", "industry": "Banks", "founded": 1994},
    "INFY": {"company": "Infosys Ltd", "industry": "IT Services", "founded": 1981},
    "ITC": {"company": "ITC Ltd", "industry": "FMCG", "founded": 1910},
    "JSWSTEEL": {"company": "JSW Steel Ltd", "industry": "Metals", "founded": 1982},
    "KOTAKBANK": {"company": "Kotak Mahindra Bank Ltd", "industry": "Banks", "founded": 1985},
    "LT": {"company": "Larsen & Toubro Ltd", "industry": "Construction", "founded": 1938},
    "LTIM": {"company": "LTIMindtree Ltd", "industry": "IT Services", "founded": 1996},
    "M&M": {"company": "Mahindra & Mahindra Ltd", "industry": "Automobile", "founded": 1945},
    "MARUTI": {"company": "Maruti Suzuki India Ltd", "industry": "Automobile", "founded": 1981},
    "NESTLEIND": {"company": "Nestle India Ltd", "industry": "FMCG", "founded": 1959},
    "NTPC": {"company": "NTPC Ltd", "industry": "Power", "founded": 1975},
    "ONGC": {"company": "Oil & Natural Gas Corporation Ltd", "industry": "Oil & Gas", "founded": 1956},
    "POWERGRID": {"company": "Power Grid Corporation of India Ltd", "industry": "Power", "founded": 1989},
    "RELIANCE": {"company": "Reliance Industries Ltd", "industry": "Conglomerate", "founded": 1958},
    "SBILIFE": {"company": "SBI Life Insurance Company Ltd", "industry": "Insurance", "founded": 2001},
    "SHRIRAMFIN": {"company": "Shriram Finance Ltd", "industry": "NBFC", "founded": 1979},
    "SBIN": {"company": "State Bank of India", "industry": "Banks", "founded": 1806},
    "SUNPHARMA": {"company": "Sun Pharmaceutical Industries Ltd", "industry": "Pharma", "founded": 1983},
    "TCS": {"company": "Tata Consultancy Services Ltd", "industry": "IT Services", "founded": 1968},
    "TATACONSUM": {"company": "Tata Consumer Products Ltd", "industry": "FMCG", "founded": 1962},
    "TATAMOTORS": {"company": "Tata Motors Ltd", "industry": "Automobile", "founded": 1945},
    "TATASTEEL": {"company": "Tata Steel Ltd", "industry": "Metals", "founded": 1907},
    "TECHM": {"company": "Tech Mahindra Ltd", "industry": "IT Services", "founded": 1986},
    "TITAN": {"company": "Titan Company Ltd", "industry": "Jewellery", "founded": 1984},
    "ULTRACEMCO": {"company": "UltraTech Cement Ltd", "industry": "Cement", "founded": 1983},
    "WIPRO": {"company": "Wipro Ltd", "industry": "IT Services", "founded": 1945}
}

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch Nifty 50 stocks data using Yahoo Finance."""
    try:
        data = []
        for symbol in NIFTY50_TICKERS:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo", timeout=15)
                if hist.empty or len(hist) < 2:
                    continue
                
                close_vals = hist['Close'].dropna()
                if close_vals.empty:
                    continue
                
                # Calculate RSI (14-day)
                rsi = None
                if len(close_vals) >= 15:
                    delta = close_vals.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi_series = 100 - (100 / (1 + rs))
                    rsi = float(rsi_series.iloc[-1])

                sym = symbol.replace('.NS', '')
                current_price = float(close_vals.iloc[-1])
                previous_close = float(close_vals.iloc[-2])
                pct_change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                day_high = float(hist['High'].iloc[-5:].max()) # Last 5 days high
                day_low = float(hist['Low'].iloc[-5:].min())  # Last 5 days low
                
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
                    'todays_high': float(hist['High'].iloc[-1]),
                    'todays_low': float(hist['Low'].iloc[-1]),
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
                    'sector': sector,
                    'rsi': rsi
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
    
    if s.get('fifty_day_avg') and s.get('two_hundred_day_avg') and s.get('current_price'):
        if s['current_price'] > s['fifty_day_avg']:
            signals.append(("Above 50 DMA", 1))
            score += 1
        if s['fifty_day_avg'] > s['two_hundred_day_avg']:
            signals.append(("Golden Cross", 2))
            score += 2
    
    rsi = s.get('rsi')
    if rsi:
        if rsi < 30:
            signals.append(("Oversold (RSI)", 2))
            score += 2
        elif rsi > 70:
            signals.append(("Overbought (RSI)", -2))
            score -= 2
        elif rsi < 45:
            signals.append(("Bullish RSI", 1))
            score += 1
            
    vol = s.get('volume')
    avg_vol = s.get('avg_volume')
    if vol and avg_vol and vol > avg_vol * 1.5:
        if per_change > 0:
            signals.append(("Volume Breakout", 1))
            score += 1
        else:
            signals.append(("High Selling Vol", -1))
            score -= 1
    
    pe = s.get('pe_ratio') or 0
    if 0 < pe < 20:
        signals.append(("Reasonable PE", 1))
        score += 1
    
    roe = s.get('roe') or 0
    if roe > 0.15:
        signals.append(("Good ROE", 1))
        score += 1
    
    if score > 0:
        action = "🟢 BUY"
    elif score < 0:
        action = "🔴 SELL"
    else:
        action = "⚪ HOLD"
    
    return {
        "action": action,
        "score": score,
        "signals": signals,
        "reasoning": "; ".join([s[0] for s in signals]) if signals else "Neutral"
    }

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
    seen_symbols = set()
    for _, row in df_sorted.iterrows():
        rec = get_recommendation(row)
        symbol = str(row.get('symbol', ''))
        
        if symbol in seen_symbols:
            continue
        seen_symbols.add(symbol)
        
        current_price = float(row.get('current_price', 0) or 0)
        per_change = float(row.get('per_change', 0) or 0)
        pe = float(row.get('pe_ratio') or 0)
        roe = float(row.get('roe') or 0)
        
        if current_price > 0:
            if "BUY" in rec['action']:
                target = current_price * 1.15
                stop = current_price * 0.95
            elif "SELL" in rec['action']:
                target = current_price * 0.85
                stop = current_price * 1.05
            else:
                target = current_price * 1.05
                stop = current_price * 0.97
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
    now = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d-%m-%Y %H:%M')
    
    avg_change = 0 if (math.isnan(avg_change) if isinstance(avg_change, float) else False) else avg_change
    
    msg = f"📊 MANVER INSIGHT - {now}\n\n"
    
    if not bearish.empty:
        msg += f"Bearish\n"
        msg += f"-----------\n\n"
        for _, s in bearish.head(10).iterrows():
            price = float(s.get('current_price', 0) or 0)
            pct = float(s.get('per_change', 0) or 0)
            target = float(s.get('target', 0) or 0)
            stop = float(s.get('stop', 0) or 0)
            pe = float(s.get('pe', 0) or 0)
            roe = float(s.get('roe', 0) or 0)
            signals = s.get('signals', '')
            sym = s.get('symbol', 'N/A')
            
            if price > 0 and not math.isnan(price):
                msg += f"■ {sym} ₹{int(price)} ({pct:+.1f}%)\n"
                try:
                    if target > 0 and target != price:
                        tgt_pct = ((target-price)/price)*100
                        if not math.isnan(tgt_pct):
                            msg += f"  🎯 Target: ₹{int(target)} ({tgt_pct:+.1f}%)\n"
                except:
                    pass
                try:
                    if stop > 0 and stop != price:
                        stp_pct = ((stop-price)/price)*100
                        if not math.isnan(stp_pct):
                            msg += f"  🛡️ Stop: ₹{int(stop)} ({stp_pct:+.1f}%)\n"
                except:
                    pass
                msg += f"  ⏱️ 2-4 weeks"
                if pe > 0 and not math.isnan(pe):
                    msg += f" | P/E:{pe:.1f}"
                if roe > 0 and not math.isnan(roe):
                    msg += f" ROE:{roe*100:.0f}%"
                msg += f"\n"
                if signals:
                    msg += f"  📊 {signals}\n"
    
    if not bullish.empty:
        msg += f"\nBullish\n"
        msg += f"-----------\n\n"
        for _, s in bullish.head(10).iterrows():
            price = float(s.get('current_price', 0) or 0)
            pct = float(s.get('per_change', 0) or 0)
            target = float(s.get('target', 0) or 0)
            stop = float(s.get('stop', 0) or 0)
            pe = float(s.get('pe', 0) or 0)
            roe = float(s.get('roe', 0) or 0)
            signals = s.get('signals', '')
            sym = s.get('symbol', 'N/A')
            
            if price > 0 and not math.isnan(price):
                msg += f"■ {sym} ₹{int(price)} ({pct:+.1f}%)\n"
                try:
                    if target > 0 and target != price:
                        tgt_pct = ((target-price)/price)*100
                        if not math.isnan(tgt_pct):
                            msg += f"  🎯 Target: ₹{int(target)} ({tgt_pct:+.1f}%)\n"
                except:
                    pass
                try:
                    if stop > 0 and stop != price:
                        stp_pct = ((stop-price)/price)*100
                        if not math.isnan(stp_pct):
                            msg += f"  🛡️ Stop: ₹{int(stop)} ({stp_pct:+.1f}%)\n"
                except:
                    pass
                msg += f"  ⏱️ 2-4 weeks"
                if pe > 0 and not math.isnan(pe):
                    msg += f" | P/E:{pe:.1f}"
                if roe > 0 and not math.isnan(roe):
                    msg += f" ROE:{roe*100:.0f}%"
                msg += f"\n"
                if signals:
                    msg += f"  📊 {signals}\n"
    
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
    
    now = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d-%m-%Y %H:%M')
    
    msg = f"\n📰 MARKET WEATHER\n"
    msg += f"Date/Time: {now}\n"
    msg += f"Status: {weather}"
    
    return msg

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            color: #38bdf8;
        }
        
        .stButton>button {
            border-radius: 12px;
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }
        
        .stock-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }
        
        .header-title {
            background: linear-gradient(90deg, #60a5fa 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="ManverInsight | Premium Stocks", page_icon="📈", layout="wide")
    apply_custom_style()
    st.markdown('<h1 class="header-title">📈 ManverInsight Pro</h1>', unsafe_allow_html=True)
    
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
                st.code(msg[:4000], language="markdown")
            
            bot_token = str(st.secrets.get("BOT_TOKEN", "")).strip()
            chat_id = str(st.secrets.get("CHAT_ID", "")).strip()
            
            st.json({"token_len": len(bot_token), "chat_id": chat_id})
            
            sent = 0
            failed = 0
            
            if len(bot_token) > 30 and (chat_id.isdigit() or (chat_id.startswith('-') and chat_id[1:].isdigit())):
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
        df_display = df_sorted[['symbol', 'company', 'current_price', 'per_change']].copy()
        df_display['change_pct'] = df_display['per_change'].apply(lambda x: f"{x:+.2f}%")
        
        st.subheader("📈 Top Gainers of the Day")
        st.dataframe(df_display.head(5)[['symbol', 'company', 'current_price', 'change_pct']], use_container_width=True, hide_index=True)
        
        st.subheader("📉 Top Losers of the Day")
        st.dataframe(df_display.tail(5)[['symbol', 'company', 'current_price', 'change_pct']], use_container_width=True, hide_index=True)
        
        st.subheader("🟢 Predicted BULLISH (May Go Up)")
        if not pred_bullish.empty:
            pred_display = pred_bullish[['symbol', 'current_price', 'per_change']].copy()
            pred_display['change_pct'] = pred_display['per_change'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(pred_display[['symbol', 'current_price', 'change_pct']], hide_index=True)
        
        st.subheader("🔴 Predicted BEARISH (May Go Down)")
        if not pred_bearish.empty:
            pred_display = pred_bearish[['symbol', 'current_price', 'per_change']].copy()
            pred_display['change_pct'] = pred_display['per_change'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(pred_display[['symbol', 'current_price', 'change_pct']], hide_index=True)
            
        st.subheader("🏢 Sector Performance")
        if not df.empty:
            sector_perf = df.groupby('sector')['per_change'].mean().sort_values(ascending=False).reset_index()
            sector_perf['Performance'] = sector_perf['per_change'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(sector_perf[['sector', 'Performance']], use_container_width=True, hide_index=True)

        st.subheader("🌡️ Market Sentiment")
        bull_pct = len(pred_bullish) / len(pred_df) * 100 if not pred_df.empty else 0
        st.progress(bull_pct / 100, text=f"Bullish Sentiment: {bull_pct:.1f}%")
    
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
                    hist = ticker.history(period="5d", timeout=15)
                    
                    if hist.empty:
                        st.error("Stock not found")
                    else:
                        close_vals = hist['Close'].dropna()
                        if close_vals.empty:
                            st.error("No price data")
                        else:
                            current = float(close_vals.iloc[-1])
                            prev = float(close_vals.iloc[-2]) if len(close_vals) > 1 else current
                            pct = ((current - prev) / prev) * 100 if prev > 0 else 0
                            
                            info = ticker.info
                            stock_data = {
                                'symbol': custom_symbol,
                                'company': info.get('longName', info.get('shortName', custom_symbol)),
                                'current_price': current,
                                'per_change': pct,
                                'change_amount': current - prev,
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
                            'industry': info.get('industry'),
                            'history': hist
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
                st.success(f"🟢 {rec['action']} - Strong Momentum")
            elif "SELL" in rec['action']:
                st.error(f"🔴 {rec['action']} - Weak Trend")
            else:
                st.warning(f"⚪ HOLD - Consolidation")
            
            # Interactive Chart
            if 'history' in s:
                chart_df = s['history']
            else:
                ticker = yf.Ticker(f"{s['symbol']}.NS")
                chart_df = ticker.history(period="6mo")
                
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.03, subplot_titles=(f'{s["symbol"]} Price', 'Volume'), 
                               row_width=[0.2, 0.7])

            fig.add_trace(go.Candlestick(x=chart_df.index,
                            open=chart_df['Open'],
                            high=chart_df['High'],
                            low=chart_df['Low'],
                            close=chart_df['Close'], name='Price'), row=1, col=1)

            fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['Volume'], name='Volume', marker_color='rgba(100, 149, 237, 0.6)'), row=2, col=1)

            fig.update_layout(template="plotly_dark", height=500, showlegend=False, 
                            xaxis_rangeslider_visible=False,
                            margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            p_tab, f_tab, a_tab = st.tabs(["⚡ Performance", "💼 Fundamentals", "🏢 About"])
            
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
    
    with tab3:
        st.subheader("🔔 Telegram Alerts")
        st.info("Add '?trigger=manver_agent_8am' to URL to send alerts")

if __name__ == "__main__":
    main()
