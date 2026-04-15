import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

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
    "TITAN": {"company": "Titan Company Ltd", "industry": "jewellery", "founded": 1984},
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

def get_groww_link(symbol):
    """Generate Groww stock link."""
    name = symbol.upper()
    info = COMPANY_INFO.get(name, {"company": name})
    company_name = info.get("company", name)
    slug = company_name.lower().replace(" ", "-").replace(".", "").replace("&", "and").replace(",", "").replace("ltd", "").replace("-", " ").strip()
    slug = "-".join(slug.split())
    return f"https://groww.in/stocks/{slug}-ltd"

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
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                open_price = hist['Open'].iloc[-1]
                
                if previous_close == 0:
                    previous_close = current_price
                    
                pct_change = ((current_price - previous_close) / previous_close) * 100
                
                day_high = float(hist['High'].max())
                day_low = float(hist['Low'].min())
                
                try:
                    info = ticker.info
                    
                    market_cap = info.get('marketCap')
                    pe_ratio = info.get('trailingPE')
                    ps_ratio = info.get('priceToBook')
                    eps = info.get('trailingEps')
                    dividend_yield = info.get('dividendYield')
                    roe = info.get('returnOnEquity')
                    roa = info.get('returnOnAssets')
                    fifty_two_week_high = info.get('fiftyTwoWeekHigh')
                    fifty_two_week_low = info.get('fiftyTwoWeekLow')
                    beta = info.get('beta')
                    volume = info.get('volume')
                    avg_volume = info.get('averageVolume')
                    fifty_day_avg = info.get('fiftyDayAverage')
                    two_hundred_day_avg = info.get('twoHundredDayAverage')
                    
                    sector = info.get('sector', '')
                    industry = info.get('industry', COMPANY_INFO.get(sym, {}).get('industry', 'N/A'))
                    full_time_employees = info.get('fullTimeEmployees')
                    website = info.get('website')
                    summary = info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else ''
                    
                except:
                    market_cap = pe_ratio = ps_ratio = eps = dividend_yield = roe = roa = None
                    fifty_two_week_high = fifty_two_week_low = beta = volume = avg_volume = None
                    fifty_day_avg = two_hundred_day_avg = None
                    sector = industry = full_time_employees = website = summary = None
                
                data.append({
                    'symbol': sym,
                    'company': COMPANY_INFO.get(sym, {}).get("company", sym),
                    'industry': industry,
                    'nse_symbol': sym,
                    
                    # Price Data
                    'current_price': float(current_price),
                    'previous_close': float(previous_close),
                    'open_price': float(open_price),
                    'per_change': float(pct_change),
                    'change_amount': float(current_price - previous_close),
                    
                    # Performance (Groww format)
                    'todays_high': day_high,
                    'todays_low': day_low,
                    'week_52_high': fifty_two_week_high,
                    'week_52_low': fifty_two_week_low,
                    'open': float(open_price),
                    'prev_close': float(previous_close),
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'lower_circuit': None,
                    'upper_circuit': None,
                    
                    # Intraday
                    'day_high': day_high,
                    'day_low': day_low,
                    'fifty_day_avg': fifty_day_avg,
                    'two_hundred_day_avg': two_hundred_day_avg,
                    
                    # Fundamentals (Groww format)
                    'market_cap': market_cap,
                    'roe': roe,
                    'pe_ratio': pe_ratio,
                    'pb_ratio': ps_ratio,
                    'eps': eps,
                    'dividend_yield': dividend_yield,
                    'beta': beta,
                    
                    # About Company
                    'sector': sector,
                    'founded': COMPANY_INFO.get(sym, {}).get("founded"),
                    'employees': full_time_employees,
                    'website': website,
                    'description': summary,
                    
                    # Links
                    'groww_link': get_groww_link(sym)
                })
            except Exception:
                continue
        
        if not data:
            return None
            
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def format_market_cap(value):
    """Format market cap in Crore/Acre."""
    if not value:
        return "N/A"
    if value >= 1e12:
        return f"₹{value/1e12:.2f}L Cr"
    elif value >= 1e10:
        return f"₹{value/1e10:.2f}K Cr"
    elif value >= 1e8:
        return f"₹{value/1e7:.2f} Cr"
    return str(value)

def format_volume(value):
    """Format volume with Indian notation."""
    if not value:
        return "N/A"
    if value >= 1e7:
        return f"{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"{value/1e5:.2f} L"
    elif value >= 1e3:
        return f"{value/1e3:.2f} K"
    return str(value)

def get_recommendation(s):
    """Generate buy/sell/hold recommendation based on technical and fundamental analysis."""
    signals = []
    score = 0
    
    # Price vs 52W analysis
    if s['current_price'] and s['week_52_low'] and s['week_52_high']:
        price_range = s['week_52_high'] - s['week_52_low']
        if price_range > 0:
            price_position = (s['current_price'] - s['week_52_low']) / price_range
            if price_position < 0.25:
                signals.append((" Oversold - Potential Buy ", 2))
                score += 2
            elif price_position > 0.85:
                signals.append((" Overbought - Wait ", -1))
                score -= 1
    
    # Daily change analysis
    if s['per_change']:
        if s['per_change'] > 3:
            signals.append((" Strong Momentum ", 1))
            score += 1
        elif s['per_change'] > 1.5:
            signals.append((" Gap Up ", 1))
            score += 1
        elif s['per_change'] < -3:
            signals.append((" Heavy Sell ", -1))
            score -= 1
        elif s['per_change'] < -1.5:
            signals.append((" Gap Down - Potential Bottom ", 1))
            score += 1
    
    # Volume analysis
    if s.get('volume') and s.get('avg_volume'):
        if s['volume'] > s['avg_volume'] * 2:
            signals.append((" High Volume ", 1 if s['per_change'] > 0 else -1))
            score += 1 if s['per_change'] > 0 else -1
    
    # Fundamental checks
    if s.get('pe_ratio'):
        if 10 < s['pe_ratio'] < 25:
            signals.append((" Reasonable PE ", 1))
            score += 1
        elif s['pe_ratio'] > 40:
            signals.append((" High PE - Risky ", -1))
            score -= 1
        elif s['pe_ratio'] < 0:
            signals.append((" Negative Earnings ", -1))
            score -= 1
    
    if s.get('roe') and s['roe'] > 0.15:
        signals.append((" Good ROE ", 1))
        score += 1
    
    # Moving average check
    if s.get('fifty_day_avg') and s.get('two_hundred_day_avg'):
        if s['current_price'] > s['fifty_day_avg'] > s['two_hundred_day_avg']:
            signals.append((" Above MA - Bullish ", 2))
            score += 2
        elif s['current_price'] < s['fifty_day_avg'] < s['two_hundred_day_avg']:
            signals.append((" Below MA - Bearish ", -2))
            score -= 2
    
    if score >= 3:
        action = "🟢 BUY"
        target = s['current_price'] * 1.10
        stop = s['current_price'] * 0.97
        timeframe = "1-4 weeks"
    elif score <= -2:
        action = "🔴 SELL"
        target = s['current_price'] * 0.95
        stop = s['current_price'] * 1.03
        timeframe = "1-2 weeks"
    else:
        action = "⚪ HOLD"
        target = s['current_price'] * 1.03
        stop = s['current_price'] * 0.98
        timeframe = "2-4 weeks"
    
    return {
        "action": action,
        "target": target,
        "stop_loss": stop,
        "timeframe": timeframe,
        "score": score,
        "signals": signals,
        "reasoning": "; ".join([s[0] for s in signals]) if signals else "No clear signals"
    }

@st.cache_data(ttl=1800)
def fetch_stock_news(symbol):
    """Fetch news for a stock using Yahoo Finance."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        news = ticker.news
        return news if news else []
    except:
        return []

@st.cache_data(ttl=1800)
def fetch_market_news():
    """Fetch general market news."""
    try:
        url = "https://newsdata.io/api/1/news"
        api_key = st.secrets.get("NEWSDATA_IO_KEY")
        if api_key:
            params = {
                "apikey": api_key,
                "q": "NSE India OR stock market OR sensex OR nifty",
                "language": "en",
                "category": "business"
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])[:5]
        return []
    except:
        return []

def send_telegram_msg(message, debug=False):
    """Send Markdown-formatted alert to Telegram."""
    try:
        bot_token = st.secrets.get("BOT_TOKEN")
        chat_id = st.secrets.get("CHAT_ID")
        
        if not bot_token or not chat_id:
            st.error("Telegram credentials not configured")
            return False
        
        if bot_token == "your_bot_token_here":
            st.error("Please update secrets.toml with actual credentials")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=30)
        
        if debug:
            st.write(f"Response: {response.status_code}")
        
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def create_telegram_alerts(df):
    """Create multiple Telegram messages for better formatting."""
    if df is None or df.empty:
        return []
    
    messages = []
    df_sorted = df.sort_values(by=["per_change"], ascending=False).reset_index(drop=True)
    
    # Header
    avg_change = df_sorted["per_change"].mean()
    sentiment = "🟢 Bullish" if avg_change > 0.5 else "🔴 Bearish" if avg_change < -0.5 else "⚪ Neutral"
    signal = "📈 BUY" if avg_change > 0.5 else "📉 SELL" if avg_change < -0.5 else "⏸️ HOLD"
    
    header = f"📊 *Nifty 50 Market Analysis*\n"
    header += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')} IST_\n\n"
    header += f"*{sentiment}* | {signal}\n"
    header += f"Avg Change: *{avg_change:+.2f}%*\n"
    header += f"Stocks: {len(df_sorted)}\n"
    messages.append(header)
    
    # Top Gainers
    gainers = df_sorted.head(10)
    gainers_msg = f"🟢 *Top 10 Gainers*\n"
    for i, row in gainers.iterrows():
        gainers_msg += f"{i+1}. {row['symbol']}: +{row['per_change']:.2f}% ₹{row['current_price']:.0f}\n"
    messages.append(gainers_msg)
    
    # Top Losers
    losers = df_sorted.tail(10).iloc[::-1]
    losers_msg = f"🔴 *Top 10 Losers*\n"
    for i, row in losers.iterrows():
        losers_msg += f"{i+1}. {row['symbol']}: {row['per_change']:.2f}% ₹{row['current_price']:.0f}\n"
    messages.append(losers_msg)
    
    # Budget Stocks
    below_1000 = df_sorted[df_sorted["current_price"] < 1000].sort_values(by=["per_change"], ascending=False)
    if not below_1000.empty:
        budget_msg = f"💰 *Budget (<₹1000)* - {len(below_1000)} stocks\n"
        for _, row in below_1000.head(8).iterrows():
            budget_msg += f"• {row['symbol']}: ₹{row['current_price']:.0f} ({row['per_change']:+.2f}%)\n"
        messages.append(budget_msg)
    
    return messages

def main():
    st.set_page_config(
        page_title="ManverInsight",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 ManverInsight")
    
    # Check for trigger mode
    query_params = st.query_params
    is_triggered = query_params.get("trigger", "") == TRIGGER_PARAM
    
    if is_triggered:
        st.info(f"🔔 Trigger Mode: {TRIGGER_PARAM}")
        df = fetch_market_data()
        if df is not None:
            messages = create_telegram_alerts(df)
            st.write("### Messages Preview:")
            for i, msg in enumerate(messages):
                st.text_area(f"Message {i+1}", msg, height=150)
            
            # Try to send to Telegram if credentials exist
            bot_token = st.secrets.get("BOT_TOKEN", "")
            chat_id = st.secrets.get("CHAT_ID", "")
            
            if bot_token and chat_id and "your_" not in bot_token:
                for msg in messages:
                    send_telegram_msg(msg)
                st.success(f"✅ Sent {len(messages)} messages!")
            else:
                st.warning("⚠️ Telegram not configured - showing preview only")
                return {"status": "preview", "messages": messages}
        else:
            st.error("❌ Failed to fetch data")
        st.stop()
        return
    
    df = fetch_market_data()
    
    if df is None or df.empty:
        st.error("Unable to fetch market data")
        return
    
    df_sorted = df.sort_values(by=["per_change"], ascending=False).reset_index(drop=True)
    
    # Summary at top
    avg = df_sorted["per_change"].mean()
    
    c1, c2 = st.columns(2)
    c1.metric("Nifty 50 Avg Change", f"{avg:+.2f}%")
    c2.metric("Total Stocks", len(df_sorted))
    
    st.divider()
    
    # Get Bullish and Bearish predictions for all stocks
    predictions = []
    for _, row in df_sorted.iterrows():
        rec = get_recommendation(row)
        predictions.append({
            'symbol': row['symbol'],
            'company': row['company'],
            'current_price': row['current_price'],
            'per_change': row['per_change'],
            'action': rec['action'],
            'score': rec['score'],
            'target': rec['target'],
            'stop_loss': rec['stop_loss'],
            'timeframe': rec['timeframe'],
            'reasoning': rec['reasoning']
        })
    
    pred_df = pd.DataFrame(predictions)
    pred_bullish = pred_df[pred_df['action'] == '🟢 BUY'].sort_values('score', ascending=False)
    pred_bearish = pred_df[pred_df['action'] == '🔴 SELL'].sort_values('score', ascending=False)
    
    # Main UI
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Stock Detail", "🔔 Alerts"])
    
    with tab1:
        # Market Overview
        st.subheader("📈 Top Gainers of the Day")
        st.dataframe(
            df_sorted.head(5)[['symbol', 'company', 'current_price', 'per_change']],
            use_container_width=True,
            hide_index=True
        )
        
        st.subheader("📉 Top Losers of the Day")
        st.dataframe(
            df_sorted.tail(5)[['symbol', 'company', 'current_price', 'per_change']],
            use_container_width=True,
            hide_index=True
        )
        
        st.subheader("💰 Stocks Below ₹1000")
        below = df_sorted[df_sorted["current_price"] < 1000][['symbol', 'current_price', 'per_change']]
        if not below.empty:
            st.dataframe(below, use_container_width=True, hide_index=True)
        else:
            st.info("No stocks below ₹1000")
        
# Predicted Bullish stocks (expected to go up)
        st.subheader("🟢 Predicted BULLISH (May Go Up)")
        if not pred_bullish.empty:
            st.dataframe(
                pred_bullish[['symbol', 'company', 'current_price', 'per_change', 'target', 'timeframe']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No bullish stocks detected")
        
        # Predicted Bearish stocks (expected to go down)
        st.subheader("🔴 Predicted BEARISH (May Go Down)")
        if not pred_bearish.empty:
            st.dataframe(
                pred_bearish[['symbol', 'company', 'current_price', 'per_change', 'target', 'timeframe']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No bearish stocks detected")
    
    with tab2:
        selected = st.selectbox("Select Stock", df_sorted['symbol'].tolist())
        
        if selected:
            s = df_sorted[df_sorted['symbol'] == selected].iloc[0]
            
            # Price Header
            price_change = s['change_amount']
            pct_change = s['per_change']
            st.metric("Price", f"₹{s['current_price']:.2f}", delta=f"{price_change:+.2f} ({pct_change:+.2f}%)")
            
            # Get recommendation
            rec = get_recommendation(s)
            
            # Bullish/Bearish header
            if "BUY" in rec['action']:
                st.success(f"🟢 {rec['action']} - Predicted to GO UP in {rec['timeframe']}")
            elif "SELL" in rec['action']:
                st.error(f"🔴 {rec['action']} - Predicted to go DOWN in {rec['timeframe']}")
            else:
                st.warning(f"⚪ {rec['action']} - Hold for {rec['timeframe']}")
            
            # Target and Stop Loss
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"🎯 Target: ₹{rec['target']:.2f} (+{((rec['target']/s['current_price']-1)*100):.1f}%)")
            with c2:
                st.warning(f"🛡️ Stop Loss: ₹{rec['stop_loss']:.2f} ({((rec['stop_loss']/s['current_price']-1)*100):.1f}%)")
            
            # Detailed Analysis
            with st.expander("📊 Analysis Breakdown", expanded=True):
                st.write(f"**Signal Score:** {rec['score']}")
                st.write("**Reasons:**")
                for sig in rec['signals']:
                    emoji = "🟢" if sig[1] > 0 else "🔴"
                    st.write(f"  {emoji} {sig[0]}")
            
            # Tabs
            p_tab, f_tab, a_tab, n_tab = st.tabs(["Performance", "Fundamentals", "About", "📰 News"])
            
            with p_tab:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Today's High**", f"₹{s['todays_high']:.2f}")
                    st.write("**52W High**", f"₹{s['week_52_high']:.2f}" if s['week_52_high'] else "N/A")
                    st.write("**Open**", f"₹{s['open']:.2f}")
                with c2:
                    st.write("**Today's Low**", f"₹{s['todays_low']:.2f}")
                    st.write("**52W Low**", f"₹{s['week_52_low']:.2f}" if s['week_52_low'] else "N/A")
                    st.write("**Prev Close**", f"₹{s['prev_close']:.2f}")
                
                st.write("**Volume**", format_volume(s['volume']))
                st.write("**Avg Volume**", format_volume(s['avg_volume']))
                st.write("**50 Day Avg**", f"₹{s['fifty_day_avg']:.2f}" if s['fifty_day_avg'] else "N/A")
            
            with f_tab:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Market Cap**", format_market_cap(s['market_cap']) if s['market_cap'] else "N/A")
                    st.write("**P/E Ratio**", f"{s['pe_ratio']:.2f}" if s['pe_ratio'] else "N/A")
                    st.write("**P/B Ratio**", f"{s['pb_ratio']:.2f}" if s['pb_ratio'] else "N/A")
                with c2:
                    st.write("**ROE**", f"{s['roe']*100:.2f}%" if s['roe'] else "N/A")
                    st.write("**EPS**", f"₹{s['eps']:.2f}" if s['eps'] else "N/A")
                    st.write("**Beta**", f"{s['beta']:.2f}" if s['beta'] else "N/A")
            
            with a_tab:
                st.write("**Company**", s['company'])
                st.write("**Industry**", s['industry'])
                st.write("**NSE Symbol**", s['nse_symbol'])
                if s.get('founded'):
                    st.write("**Founded**", s['founded'])
            
            with n_tab:
                news = fetch_stock_news(selected)
                if news:
                    for item in news[:5]:
                        with st.expander(item.get("title", "No title")[:80]):
                            st.write(item.get("content", ""))
                            if item.get("link"):
                                st.markdown(f"[Read more]({item['link']})")
                else:
                    st.info("No recent news available")
    
    with tab3:
        st.subheader("🔔 Telegram Alerts")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            msg_type = st.radio("Message Type", ["Full Report", "Top Gainers", "Top Losers", "Budget Stocks"])
        with col2:
            debug = st.checkbox("Debug")
        
        if st.button("Send to Telegram"):
            if msg_type == "Full Report":
                messages = create_telegram_alerts(df)
            elif msg_type == "Top Gainers":
                messages = [create_telegram_alerts(df)[1]]
            elif msg_type == "Top Losers":
                messages = [create_telegram_alerts(df)[2]]
            else:
                below = df_sorted[df_sorted["current_price"] < 1000].sort_values("per_change", ascending=False)
                msg = f"💰 *Budget Stocks (<₹1000)*\n"
                for _, r in below.head(10).iterrows():
                    msg += f"• {r['symbol']}: ₹{r['current_price']:.0f} ({r['per_change']:+.2f}%)\n"
                messages = [msg]
            
            for m in messages:
                send_telegram_msg(m, debug=debug)
            st.success(f"✅ Sent {len(messages)} message(s)!")

if __name__ == "__main__":
    main()