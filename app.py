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
    per_change = s.get('per_change', 0) or 0
    
    # Positive daily momentum
    if per_change > 1:
        signals.append((" Strong Positive ", 2))
        score += 2
    elif per_change > 0:
        signals.append((" Positive ", 1))
        score += 1
    
    # Negative daily momentum
    if per_change < -1:
        signals.append((" Negative ", -1))
        score -= 1
    elif per_change < 0:
        signals.append((" Slight Negative ", -1))
        score -= 1
    
    # Price vs 52W analysis
    if s['current_price'] and s['week_52_low'] and s['week_52_high']:
        price_range = s['week_52_high'] - s['week_52_low']
        if price_range > 0:
            price_position = (s['current_price'] - s['week_52_low']) / price_range
            if price_position < 0.35:
                signals.append((" Near 52W Low - Upside Potential ", 2))
                score += 2
            elif price_position > 0.75:
                signals.append((" Near 52W High - Limited Upside ", -1))
                score -= 1
    
    # Price vs Moving Averages
    if s.get('fifty_day_avg') and s.get('two_hundred_day_avg'):
        if s['current_price'] > s['fifty_day_avg']:
            signals.append((" Above 50 DMA ", 1))
            score += 1
        if s['fifty_day_avg'] > s['two_hundred_day_avg']:
            signals.append((" Golden Cross Signal ", 2))
            score += 2
        if s['current_price'] < s['fifty_day_avg']:
            signals.append((" Below 50 DMA ", -1))
            score -= 1
        if s['fifty_day_avg'] < s['two_hundred_day_avg']:
            signals.append((" Death Cross Signal ", -2))
            score -= 2
    
    # Volume analysis
    vol = s.get('volume', 0) or 0
    avg_vol = s.get('avg_volume', 0) or 0
    if avg_vol and vol > avg_vol * 1.5:
        signals.append((" High Volume ", 1 if per_change > 0 else -1))
        score += 1 if per_change > 0 else -1
    elif avg_vol and vol < avg_vol * 0.3:
        signals.append((" Low Volume ", 0))
    
    # Fundamental checks - positive
    pe = s.get('pe_ratio') or 0
    if 0 < pe < 20:
        signals.append((" Reasonable PE ", 1))
        score += 1
    elif 0 < pe < 15:
        signals.append((" Cheap Valuation ", 2))
        score += 2
    
    roe = s.get('roe') or 0
    if roe > 0.15:
        signals.append((" Good ROE ", 1))
        score += 1
    elif roe > 0.20:
        signals.append((" Excellent ROE ", 2))
        score += 2
    
    # Fundamental checks - negative
    if pe > 35:
        signals.append((" Expensive ", -1))
        score -= 1
    elif pe < 0:
        signals.append((" Loss Making ", -2))
        score -= 2
    
    beta = s.get('beta') or 1
    if 0.8 < beta < 1.2:
        signals.append((" Stable ", 1))
        score += 1
    elif beta > 1.3:
        signals.append((" High Volatility ", -1))
        score -= 1
    
    # Final action determination
    if score >= 2:
        action = "🟢 BUY"
        target = s['current_price'] * 1.12
        stop = s['current_price'] * 0.96
        timeframe = "2-4 weeks"
    elif score <= -2:
        action = "🔴 SELL"
        target = s['current_price'] * 0.90
        stop = s['current_price'] * 1.05
        timeframe = "1-3 weeks"
    else:
        action = "⚪ HOLD"
        target = s['current_price'] * 1.05
        stop = s['current_price'] * 0.97
        timeframe = "3-4 weeks"
    
    return {
        "action": action,
        "target": target,
        "stop_loss": stop,
        "timeframe": timeframe,
        "score": score,
        "signals": signals,
        "reasoning": "; ".join([s[0] for s in signals]) if signals else "Neutral"
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
        bot_token = st.secrets.get("BOT_TOKEN", "")
        chat_id = st.secrets.get("CHAT_ID", "")
        
        if not bot_token or not chat_id:
            return {"success": False, "error": "No credentials"}
        
        if "your_" in bot_token or "your_" in chat_id:
            return {"success": False, "error": "Invalid credentials"}
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=30)
        
        if debug:
            st.write(f"TG Response: {response.status_code} - {response.text[:200]}")
        
        if response.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_prediction_alerts(df):
    """Create prediction-based telegram alerts with full details."""
    if df is None or df.empty:
        return []
    
    messages = []
    df_sorted = df.sort_values(by=["per_change"], ascending=False).reset_index(drop=True)
    
    # Get predictions for all stocks
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
            'reasoning': rec['reasoning'],
            'todays_high': row.get('todays_high'),
            'todays_low': row.get('todays_low'),
            'week_52_high': row.get('week_52_high'),
            'week_52_low': row.get('week_52_low'),
            'volume': row.get('volume'),
            'market_cap': row.get('market_cap'),
            'pe_ratio': row.get('pe_ratio'),
            'roe': row.get('roe'),
            'eps': row.get('eps'),
            'industry': row.get('industry')
        })
    
    pred_df = pd.DataFrame(predictions)
    
    # Header with market summary
    avg_change = df_sorted["per_change"].mean()
    bullish_stocks = pred_df[pred_df['action'] == '🟢 BUY']
    bearish_stocks = pred_df[pred_df['action'] == '🔴 SELL']
    
    header = f"📊 *MANVERINSIGHT - STOCK PREDICTIONS*\n"
    header += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')} IST_\n\n"
    header += f"📈 *Market:* Nifty 50 | *Avg:* {avg_change:+.2f}%\n"
    header += f"🟢 Bullish: {len(bullish_stocks)} | 🔴 Bearish: {len(bearish_stocks)}\n"
    messages.append(header)
    
    # BULLISH STOCKS with full details
    if not bullish_stocks.empty:
        bullish = bullish_stocks.sort_values('score', ascending=False).head(10)
        msg = f"🟢 *BULLISH STOCKS (May Go Up)* - Top {len(bullish)}\n"
        msg += "━" * 28 + "\n"
        for _, s in bullish.iterrows():
            target_pct = ((s['target']/s['current_price'])-1)*100
            stop_pct = ((s['stop_loss']/s['current_price'])-1)*100
            pe = f"P/E:{s['pe_ratio']:.1f}" if s.get('pe_ratio') else "P/E:N/A"
            roe_str = f"ROE:{s['roe']*100:.0f}%" if s.get('roe') else ""
            
            msg += f"■ *{s['symbol']}* ₹{s['current_price']:.0f} ({s['per_change']:+.2f}%)\n"
            msg += f"  🎯 Target: ₹{s['target']:.0f} (+{target_pct:.0f}%)\n"
            msg += f"  🛡️ Stop: ₹{s['stop_loss']:.0f} ({stop_pct:.0f}%)\n"
            msg += f"  ⏱️ {s['timeframe']} | {pe} {roe_str}\n"
            msg += f"  📊 {s['reasoning'][:60]}...\n\n"
        messages.append(msg)
    
    # BEARISH STOCKS with full details
    if not bearish_stocks.empty:
        bearish = bearish_stocks.sort_values('score', ascending=False).head(10)
        msg = f"🔴 *BEARISH STOCKS (May Go Down)* - Top {len(bearish)}\n"
        msg += "━" * 28 + "\n"
        for _, s in bearish.iterrows():
            target_pct = ((s['target']/s['current_price'])-1)*100
            stop_pct = ((s['stop_loss']/s['current_price'])-1)*100
            pe = f"P/E:{s['pe_ratio']:.1f}" if s.get('pe_ratio') else "P/E:N/A"
            roe_str = f"ROE:{s['roe']*100:.0f}%" if s.get('roe') else ""
            
            msg += f"■ *{s['symbol']}* ₹{s['current_price']:.0f} ({s['per_change']:+.2f}%)\n"
            msg += f"  🎯 Target: ₹{s['target']:.0f} ({target_pct:.0f}%)\n"
            msg += f"  🛡️ Stop: ₹{s['stop_loss']:.0f} (+{stop_pct:.0f}%)\n"
            msg += f"  ⏱️ {s['timeframe']} | {pe} {roe_str}\n"
            msg += f"  📊 {s['reasoning'][:60]}...\n\n"
        messages.append(msg)
    
    # TOP MOVERS for context
    msg = f"📈 *TOP MOVERS Today*\n"
    msg += "━" * 28 + "\n"
    msg += f"🟢 *Top Gainers:*\n"
    for _, s in df_sorted.head(3).iterrows():
        msg += f"  {s['symbol']}: +{s['per_change']:.2f}% ₹{s['current_price']:.0f}\n"
    msg += f"\n🔴 *Top Losers:*\n"
    for _, s in df_sorted.tail(3).iterrows():
        msg += f"  {s['symbol']}: {s['per_change']:.2f}% ₹{s['current_price']:.0f}\n"
    messages.append(msg)
    
    # Budget stocks
    below = df_sorted[df_sorted["current_price"] < 1000]
    if not below.empty:
        msg = f"💰 *BUDGET STOCKS (<₹1000)*\n"
        for _, s in below.head(5).iterrows():
            msg += f"  {s['symbol']}: ₹{s['current_price']:.0f} ({s['per_change']:+.2f}%)\n"
        messages.append(msg)
    
    return messages

def create_telegram_alerts(df):
    """Legacy function - just call new prediction alerts."""
    return create_prediction_alerts(df)

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
        st.info("🔔 Trigger Mode: Sending predictions...")
        df = fetch_market_data()
        
        if df is not None:
            # Generate prediction messages
            messages = create_prediction_alerts(df)
            
            # Show preview
            for i, msg in enumerate(messages):
                st.code(msg[:500], language="markdown")
            
            # Try sending
            bot_token = st.secrets.get("BOT_TOKEN", "")
            chat_id = st.secrets.get("CHAT_ID", "")
            
            sent = 0
            failed = 0
            
            if bot_token and chat_id and len(bot_token) > 20:
                for msg in messages:
                    result = send_telegram_msg(msg)
                    if result.get("success"):
                        sent += 1
                    else:
                        failed += 1
            else:
                st.warning(f"⚠️ Telegram not configured. Add BOT_TOKEN and CHAT_ID to secrets.")
                st.json({"bot_configured": False, "preview_count": len(messages)})
            
            st.success(f"✅ Sent: {sent}/{len(messages)} | Failed: {failed}")
            return {"sent": sent, "failed": failed, "total": len(messages)}
    
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
        col1, col2 = st.columns([2, 1])
        with col1:
            custom_symbol = st.text_input("Enter Stock Symbol (e.g., INFY, SBIN, RELIANCE)", "").upper().strip()
        with col2:
            st.write("")
            st.write("")
            use_custom = st.button("Fetch Details")
        
        selected = None
        custom_data = None
        
        if custom_symbol and use_custom:
            with st.spinner(f"Fetching {custom_symbol}..."):
                try:
                    ticker = yf.Ticker(f"{custom_symbol}.NS")
                    hist = ticker.history(period="2d")
                    info = ticker.info
                    
                    if hist.empty:
                        st.error(f"Stock not found: {custom_symbol}")
                    else:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        pct = ((current - prev) / prev) * 100
                        
                        custom_data = {
                            'symbol': custom_symbol,
                            'company': info.get('longName', info.get('shortName', custom_symbol)),
                            'current_price': current,
                            'per_change': pct,
                            'change_amount': current - prev,
                            'open': float(hist['Open'].iloc[-1]),
                            'prev_close': prev,
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
                            'founded': None
                        }
                        selected = custom_symbol
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if not selected and not custom_data:
            selected = st.selectbox("Or select from Nifty 50", [""] + df_sorted['symbol'].tolist())
            if selected:
                custom_data = df_sorted[df_sorted['symbol'] == selected].iloc[0].to_dict()
        
        if custom_data:
            s = custom_data
            
            # Price & Prediction
            st.metric("Price", f"₹{s['current_price']:.2f}", delta=f"{s['per_change']:+.2f}%")
            rec = get_recommendation(s)
            
            if "BUY" in rec.get('action', ''):
                st.success(f"🟢 {rec['action']} - Predicted UP ({rec['timeframe']})")
            elif "SELL" in rec.get('action', ''):
                st.error(f"🔴 {rec['action']} - Predicted DOWN ({rec['timeframe']})")
            else:
                st.warning(f"⚪ HOLD ({rec.get('timeframe', '2-4 weeks')})")
            
            c1, c2 = st.columns(2)
            c1.info(f"🎯 Target: ₹{rec['target']:.0f} (+{((rec['target']/s['current_price']-1)*100):.0f}%)")
            c2.warning(f"🛡️ Stop: ₹{rec['stop_loss']:.0f} ({((rec['stop_loss']/s['current_price']-1)*100):.0f}%)")
            
            with st.expander("📊 Analysis"):
                st.write(f"**Score:** {rec.get('score', 0)}")
                for sig in rec.get('signals', []):
                    st.write(f"  {'🟢' if sig[1] > 0 else '🔴'} {sig[0]}")
            
# Tabs
            p_tab, f_tab, a_tab, n_tab = st.tabs(["⚡ Performance", "💼 Fundamentals", "🏢 About", "📰 News"])
            
            with p_tab:
                st.markdown("### 📊 Price Information")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Today's High:**")
                    st.markdown("**52W High:**")
                    st.markdown("**Open:**")
                    st.markdown("**Avg Volume:**")
                with c2:
                    high = s.get('todays_high', 0)
                    st.markdown(f"₹{high:,.2f}")
                    w52h = s.get('week_52_high', 0)
                    st.markdown(f"₹{w52h:,.2f}" if w52h else "N/A")
                    st.markdown(f"₹{s.get('open', 0):,.2f}")
                    st.markdown(format_volume(s.get('avg_volume')))
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Today's Low:**")
                    st.markdown("**52W Low:**")
                    st.markdown("**Prev Close:**")
                    st.markdown("**Volume:**")
                with c2:
                    low = s.get('todays_low', 0)
                    st.markdown(f"₹{low:,.2f}")
                    w52l = s.get('week_52_low', 0)
                    st.markdown(f"₹{w52l:,.2f}" if w52l else "N/A")
                    st.markdown(f"₹{s.get('prev_close', 0):,.2f}")
                    st.markdown(format_volume(s.get('volume')))
            
            with f_tab:
                st.markdown("### 💰 Valuation")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Market Cap:**")
                    st.markdown("**P/E Ratio:**")
                    st.markdown("**P/B Ratio:**")
                with c2:
                    mc = s.get('market_cap')
                    st.markdown(format_market_cap(mc) if mc else "N/A")
                    pe = s.get('pe_ratio', 0)
                    st.markdown(f"{pe:.2f}" if pe else "N/A")
                    pb = s.get('pb_ratio', 0)
                    st.markdown(f"{pb:.2f}" if pb else "N/A")
                
                st.markdown("### 📈 Profitability")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**ROE:**")
                    st.markdown("**EPS:**")
                    st.markdown("**Beta:**")
                with c2:
                    roe = s.get('roe', 0)
                    st.markdown(f"{roe*100:.1f}%" if roe else "N/A")
                    eps = s.get('eps', 0)
                    st.markdown(f"₹{eps:.2f}" if eps else "N/A")
                    beta = s.get('beta', 0)
                    st.markdown(f"{beta:.2f}" if beta else "N/A")
            
            with a_tab:
                st.markdown("### 🏢 Company Information")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Company:**")
                    st.markdown("**Industry:**")
                    st.markdown("**Sector:**")
                with c2:
                    st.markdown(f"**{s.get('company', s.get('symbol'))}**")
                    st.markdown(s.get('industry', 'N/A'))
                    st.markdown(s.get('sector', 'N/A'))
                
                st.markdown("### 📊 Moving Averages")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**50 Day Avg:**")
                    st.markdown("**200 Day Avg:**")
                with c2:
                    dma50 = s.get('fifty_day_avg', 0)
                    st.markdown(f"₹{dma50:,.2f}" if dma50 else "N/A")
                    dma200 = s.get('two_hundred_day_avg', 0)
                    st.markdown(f"₹{dma200:,.2f}" if dma200 else "N/A")
            
            with n_tab:
                st.subheader(f"📰 News for {selected}")
                if selected:
                    news = fetch_stock_news(selected)
                    if news:
                        for item in news[:5]:
                            with st.expander(item.get("title", "No title")[:80]):
                                st.write(item.get("content", ""))
                                if item.get("link"):
                                    st.markdown(f"[Read more]({item['link']})")
                    else:
                        st.info("No recent news available")
                else:
                    st.info("Select a stock to view news")
    
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