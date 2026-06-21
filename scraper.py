#!/usr/bin/env python3
"""
DSEX Pro Screener — Path B Auto-Refresh Pipeline (FULL EDITION)
All 15 features: news, foreign activity, block deals, volume spike, gap, circuit breaker, top 20, alerts data
Run during market hours (10:00 AM – 2:30 PM BD Time)
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np
import schedule
import time
from datetime import datetime, timedelta
import warnings
import os
import sys
import glob

warnings.filterwarnings('ignore')

# ───────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────
OUTPUT_FILE = "dse_data.json"
MARKET_OPEN = "09:45"
MARKET_CLOSE = "14:45"
REFRESH_INTERVAL = 5

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# ───────────────────────────────────────────────
# DSE SECTOR MAPPING
# ───────────────────────────────────────────────
SECTOR_MAP = {
    'BANK': ['ABBANK', 'ALARABANK', 'BANKASIA', 'BRACBANK', 'CITYBANK', 'DHAKABANK',
             'DUTCHBANGL', 'EBL', 'IFIC', 'JAMUNABANK', 'NCCBANK', 'NRBBANK', 'ONEBANKLTD',
             'PREMIERBAN', 'PRIMEBANK', 'PUBALIBANK', 'RUPALIBANK', 'SHAHJABANK', 'SIBL',
             'SOUTHEASTB', 'TRUSTBANK', 'UNIONBANK', 'UTTARABANK'],
    'NBFI': ['BAYLEASING', 'BDFINANCE', 'DBH', 'FAREASTFIN', 'FASFIN', 'FIRSTFIN',
             'GSPFINANCE', 'IDLC', 'IPDC', 'LANKABAFIN', 'MIDASFIN', 'NHFIL', 'PHOENIXFIN'],
    'INSURANCE': ['ASIAINS', 'ASIAPACINS', 'CENTRALINS', 'CRYSTALINS', 'EASTERNINS',
                  'GLOBALINS', 'ISLAMIINS', 'JANATAINS', 'MERCINS', 'NORTHRNINS',
                  'PEOPLESINS', 'PHENIXINS', 'PIONEERINS', 'PRAGATIINS', 'PRIMELIFE',
                  'PROVATIINS', 'RELIANCINS', 'RUPALIINS', 'SANDHANINS', 'SUNLIFEINS',
                  'TAKAFULINS', 'UNITEDINS'],
    'PHARMA': ['ACMEPL', 'AMBEEPHA', 'BEACONPHAR', 'BXPHARMA', 'BXSYNTH', 'GLAXOSMITH',
               'IBNSINA', 'KEYACOSMET', 'MARICO', 'ORIONPHARM', 'RECKITTBEN', 'RENATA', 'SQURPHARMA'],
    'TEXTILES': ['AL-HAJTEX', 'ANLIMAYARN', 'APEXSPINN', 'ARGONDENIM', 'DELTASPINN', 'DSSL',
                 'HRTEX', 'JUTESPINN', 'KARIMTEXT', 'MATINSPINN', 'METROSPIN', 'MUNNOFEFAB',
                 'NURANI', 'RAHIMTEXT', 'RINGSHINE', 'SAFKOSPINN', 'SAIHAMTEX', 'SONARGAON',
                 'SQUARETEXT', 'TALLUSPIN', 'TOSRIFA', 'UNITEDGEN'],
    'CEMENT': ['ARAMITCEM', 'CROWNCEMNT', 'HEIDELBCEM', 'LAFARGEHOLCIM', 'MEGHNACEM',
               'PREMIERCEM', 'SENACEMENT', 'SHAHCEMENT', 'SPCERAMICS'],
    'ENGINEERING': ['ANWARGALV', 'BDCOM', 'BSRMLTD', 'DESCO', 'GPHISPAT', 'KPCL',
                    'MLDYEING', 'RANFOUNDRY', 'RSRMSTEEL', 'SALAMCRST'],
    'FOOD': ['AAMRANET', 'ACFL', 'AFCAGRO', 'AMANFEED', 'APEXFOODS', 'BANGAS', 'BDTHAIFOOD',
             'FUWANGFOOD', 'KDSALTD', 'NAVANACNG', 'OLYMPIC', 'PRAN', 'RAHIMAFOOD', 'SHURWID'],
    'FUEL_POWER': ['BARKAPOWER', 'DOREENPWR', 'JAMUNAOIL', 'KPCL', 'MPETROLEUM', 'PADMAOIL',
                   'POWERGRID', 'SUMITPOWER', 'TITASGAS', 'UNIQUEGEN'],
    'IT_TELECOM': ['ADNTEL', 'AGNISYSL', 'AOL', 'BDCOM', 'DAFODILCOM', 'ETL', 'ROBI'],
    'MISCELLANEOUS': ['ACI', 'ACIFORMULA', 'AFTABAUTO', 'BSC', 'BSCPLC', 'GP', 'RECKITTBEN']
}

CIRCUIT_LIMITS = {
    'BANK': 10.0, 'NBFI': 10.0, 'INSURANCE': 10.0, 'PHARMA': 10.0,
    'TEXTILES': 10.0, 'CEMENT': 10.0, 'ENGINEERING': 10.0, 'FOOD': 10.0,
    'FUEL_POWER': 10.0, 'IT_TELECOM': 10.0, 'MISCELLANEOUS': 10.0, 'OTHER': 10.0
}

def get_sector(symbol):
    for sector, symbols in SECTOR_MAP.items():
        if symbol in symbols:
            return sector
    return 'OTHER'

def get_circuit_limit(symbol):
    return CIRCUIT_LIMITS.get(get_sector(symbol), 10.0)

# ───────────────────────────────────────────────
# DSEX INDEX SCRAPER
# ───────────────────────────────────────────────
def scrape_dsex_index():
    """Scrape DSEX, DS30, DSES index values"""
    try:
        url = "https://dsebd.org/"
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        indices = {'DSEX': 0, 'DS30': 0, 'DSES': 0, 'DSEX_change': 0, 'DS30_change': 0, 'DSES_change': 0}
        # Try multiple selectors to find index values
        for text in soup.find_all(string=True):
            t = text.strip()
            if 'DSEX' in t and any(c.isdigit() for c in t):
                try:
                    # Look for patterns like "DSEX 5,516.82" or similar
                    parts = t.replace(',', '').split()
                    for i, p in enumerate(parts):
                        if p == 'DSEX' and i+1 < len(parts):
                            indices['DSEX'] = float(parts[i+1])
                        if p == 'DS30' and i+1 < len(parts):
                            indices['DS30'] = float(parts[i+1])
                        if p == 'DSES' and i+1 < len(parts):
                            indices['DSES'] = float(parts[i+1])
                except:
                    continue
        return indices
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARN index scrape failed: {e}")
        return {'DSEX': 0, 'DS30': 0, 'DSES': 0, 'DSEX_change': 0, 'DS30_change': 0, 'DSES_change': 0}

# ───────────────────────────────────────────────
# MARKET STATUS
# ───────────────────────────────────────────────
def get_market_status():
    """Check if BD market is currently open"""
    from datetime import datetime, timezone, timedelta
    bd_time = datetime.now(timezone(timedelta(hours=6)))  # UTC+6
    now = bd_time.strftime('%H:%M')
    weekday = bd_time.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
    # BD market: Sun-Thu, 10:00 AM - 2:30 PM
    is_trading_day = weekday in [6, 0, 1, 2, 3]  # Sun=6, Mon=0, Tue=1, Wed=2, Thu=3
    is_market_hours = '10:00' <= now <= '14:30'
    status = 'OPEN' if (is_trading_day and is_market_hours) else 'CLOSED'
    next_open = None
    if status == 'CLOSED':
        if is_trading_day and now < '10:00':
            next_open = bd_time.strftime('%Y-%m-%d') + ' 10:00'
        else:
            # Next trading day
            days_to_add = 1
            next_weekday = (weekday + 1) % 7
            while next_weekday not in [6, 0, 1, 2, 3]:
                days_to_add += 1
                next_weekday = (next_weekday + 1) % 7
            next_open = (bd_time + timedelta(days=days_to_add)).strftime('%Y-%m-%d') + ' 10:00'
    return {'status': status, 'bd_time': bd_time.strftime('%Y-%m-%d %H:%M'), 'next_open': next_open}

# ───────────────────────────────────────────────
# MAIN SCRAPER
# ───────────────────────────────────────────────
def scrape_dse():
    """Scrape DSEX main data"""
    url = "https://dsebd.org/dseX_share.php"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        stock_data = []
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 10:
                        try:
                            data = {
                                'symbol': cols[1].text.strip(),
                                'ltp': float(cols[2].text.strip().replace(',', '')),
                                'high': float(cols[3].text.strip().replace(',', '')),
                                'low': float(cols[4].text.strip().replace(',', '')),
                                'closep': float(cols[5].text.strip().replace(',', '')),
                                'ycp': float(cols[6].text.strip().replace(',', '')),
                                'change_pct': float(cols[7].text.strip().replace(',', '')),
                                'trade': int(cols[8].text.strip().replace(',', '')),
                                'value_mn': float(cols[9].text.strip().replace(',', '')),
                                'volume': int(cols[10].text.strip().replace(',', '')) if len(cols) > 10 else 0
                            }
                            stock_data.append(data)
                        except:
                            continue
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scraped {len(stock_data)} stocks")
        return stock_data
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR main scrape: {e}")
        return None

# ───────────────────────────────────────────────
# DSE NEWS SCRAPER
# ───────────────────────────────────────────────
def scrape_news():
    """Scrape DSE latest news/announcements"""
    try:
        url = "https://dsebd.org/latest_news.php"
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        news_items = []
        for row in soup.find_all('tr')[1:11]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                try:
                    news_items.append({
                        'date': cols[0].text.strip(),
                        'title': cols[1].text.strip(),
                        'category': cols[2].text.strip() if len(cols) > 2 else 'General',
                        'url': 'https://dsebd.org/' + (cols[1].find('a')['href'] if cols[1].find('a') else '')
                    })
                except:
                    continue
        return news_items[:10]
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARN news scrape failed: {e}")
        return []

# ───────────────────────────────────────────────
# FOREIGN INVESTOR ACTIVITY
# ───────────────────────────────────────────────
def scrape_foreign_activity():
    """Scrape DSE foreign investor daily trading"""
    try:
        url = "https://dsebd.org/foreign_trading.php"
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        foreign_data = {'buy_value_mn': 0, 'sell_value_mn': 0, 'net_value_mn': 0, 'top_buy': [], 'top_sell': []}
        tables = soup.find_all('table')
        for table in tables:
            text = table.get_text()
            if 'Foreign Buy' in text or 'Foreign Sell' in text:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        try:
                            sym = cols[0].text.strip()
                            buy = float(cols[1].text.strip().replace(',', ''))
                            sell = float(cols[2].text.strip().replace(',', ''))
                            net = float(cols[3].text.strip().replace(',', ''))
                            if net > 0:
                                foreign_data['top_buy'].append({'symbol': sym, 'net_buy_mn': round(net, 2)})
                            else:
                                foreign_data['top_sell'].append({'symbol': sym, 'net_sell_mn': round(abs(net), 2)})
                            foreign_data['buy_value_mn'] += buy
                            foreign_data['sell_value_mn'] += sell
                        except:
                            continue
        foreign_data['net_value_mn'] = round(foreign_data['buy_value_mn'] - foreign_data['sell_value_mn'], 2)
        foreign_data['top_buy'] = sorted(foreign_data['top_buy'], key=lambda x: x['net_buy_mn'], reverse=True)[:10]
        foreign_data['top_sell'] = sorted(foreign_data['top_sell'], key=lambda x: x['net_sell_mn'], reverse=True)[:10]
        return foreign_data
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARN foreign scrape failed: {e}")
        return {'buy_value_mn': 0, 'sell_value_mn': 0, 'net_value_mn': 0, 'top_buy': [], 'top_sell': []}

# ───────────────────────────────────────────────
# BLOCK DEALS SCRAPER
# ───────────────────────────────────────────────
def scrape_block_deals():
    """Scrape DSE block/bulk deals"""
    try:
        url = "https://dsebd.org/block_deals.php"
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        deals = []
        for row in soup.find_all('tr')[1:21]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                try:
                    deals.append({
                        'symbol': cols[0].text.strip(),
                        'volume': int(cols[1].text.strip().replace(',', '')),
                        'value_mn': float(cols[2].text.strip().replace(',', '')),
                        'price': float(cols[3].text.strip().replace(',', '')),
                        'type': cols[4].text.strip()
                    })
                except:
                    continue
        return deals[:15]
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARN block deals scrape failed: {e}")
        return []

# ───────────────────────────────────────────────
# TOP 20 SHARES SCRAPER
# ───────────────────────────────────────────────
def scrape_top20():
    """Scrape DSE top 20 gainers, losers, most active"""
    categories = {'top_gainers': [], 'top_losers': [], 'most_active': [], 'top_value': []}
    try:
        urls = {
            'top_gainers': 'https://dsebd.org/top_ten_gainer.php',
            'top_losers': 'https://dsebd.org/top_ten_loser.php',
            'most_active': 'https://dsebd.org/top_ten_volume.php',
            'top_value': 'https://dsebd.org/top_ten_value.php'
        }
        for key, url in urls.items():
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = []
                for row in soup.find_all('tr')[1:11]:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            items.append({
                                'symbol': cols[0].text.strip(),
                                'ltp': float(cols[1].text.strip().replace(',', '')),
                                'change_pct': float(cols[2].text.strip().replace(',', '')),
                                'volume': int(cols[3].text.strip().replace(',', '')) if len(cols) > 3 else 0
                            })
                        except:
                            continue
                categories[key] = items[:10]
            except:
                continue
        return categories
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WARN top20 scrape failed: {e}")
        return categories

# ───────────────────────────────────────────────
# HISTORICAL / VOLUME SPIKE / GAP / CIRCUIT
# ───────────────────────────────────────────────
def load_historical_avg(symbol, days=5):
    """Load N-day average volume from archive"""
    archive_dir = "dse_archive"
    if not os.path.exists(archive_dir):
        return None
    files = sorted(glob.glob(os.path.join(archive_dir, "*.json")))
    volumes = []
    for f in files[-days:]:
        try:
            with open(f) as fp:
                data = json.load(fp)
                for s in data:
                    if s['symbol'] == symbol:
                        volumes.append(s['volume'])
                        break
        except:
            continue
    if len(volumes) >= 2:
        return np.mean(volumes)
    return None

def compute_volume_spike(df):
    """Compute volume vs 5-day average"""
    df['volume_5d_avg'] = df['symbol'].apply(lambda s: load_historical_avg(s, 5))
    df['volume_spike'] = df.apply(lambda r: round(r['volume'] / r['volume_5d_avg'], 2) if r['volume_5d_avg'] and r['volume_5d_avg'] > 0 else None, axis=1)
    return df

def compute_gap(df):
    """Compute gap from yesterday close"""
    df['gap_pct'] = (((df['ltp'] - df['ycp']) / df['ycp']) * 100).round(2)
    return df

def compute_circuit_proximity(df):
    """How close to circuit limit (typically ±10%)"""
    df['circuit_limit'] = df['symbol'].apply(get_circuit_limit)
    df['circuit_proximity_pct'] = df.apply(
        lambda r: round((r['change_pct'] / r['circuit_limit']) * 100, 1) if r['circuit_limit'] else 0, axis=1
    )
    return df

# ───────────────────────────────────────────────
# ANALYTICS ENGINE
# ───────────────────────────────────────────────
def compute_metrics(stock_data):
    df = pd.DataFrame(stock_data)
    df = df.dropna()
    df['intraday_range_pct'] = ((df['high'] - df['low']) / df['low'] * 100).round(2)
    df['dist_from_high_pct'] = ((df['ltp'] - df['high']) / df['high'] * 100).round(2)
    df['dist_from_low_pct'] = ((df['ltp'] - df['low']) / df['low'] * 100).round(2)
    df['value_per_trade'] = (df['value_mn'] * 1000000 / df['trade']).replace([np.inf, -np.inf], 0).round(0).astype(int)
    df['momentum_score'] = (df['change_pct'] * np.log1p(df['volume'])).round(2)
    df['vwap_approx'] = ((df['high'] + df['low'] + df['closep']) / 3).round(2)
    df['sector'] = df['symbol'].apply(get_sector)
    df['price_position'] = (((df['ltp'] - df['ycp']) / (df['high'] - df['low']) * 100)).round(2)
    df['liquidity_score'] = (df['volume'] / (df['value_mn'] * 1000000 / df['ltp'])).replace([np.inf, -np.inf], 0).round(2)
    df = compute_gap(df)
    df = compute_volume_spike(df)
    df = compute_circuit_proximity(df)
    return df

# ───────────────────────────────────────────────
# OUTPUT BUILDER
# ───────────────────────────────────────────────
def build_output(df, news, foreign, block_deals, top20, indices, market_status):
    advancing = len(df[df['change_pct'] > 0])
    declining = len(df[df['change_pct'] < 0])
    unchanged = len(df[df['change_pct'] == 0])
    top_gainer = df.loc[df['change_pct'].idxmax()]
    top_loser = df.loc[df['change_pct'].idxmin()]
    most_active_vol = df.loc[df['volume'].idxmax()]
    most_active_val = df.loc[df['value_mn'].idxmax()]
    most_volatile = df.loc[df['intraday_range_pct'].idxmax()]
    highest_momentum = df.loc[df['momentum_score'].idxmax()]
    highest_spike = df.loc[df['volume_spike'].idxmax()] if df['volume_spike'].notna().any() else None
    near_circuit = df[df['circuit_proximity_pct'].abs() >= 80].sort_values('circuit_proximity_pct', ascending=False).head(5)

    sector_perf = df.groupby('sector').agg({
        'change_pct': 'mean', 'volume': 'sum', 'value_mn': 'sum', 'ltp': 'count'
    }).round(2)
    sector_perf.columns = ['change_pct', 'volume', 'value_mn', 'stock_count']
    sector_perf = sector_perf.sort_values('change_pct', ascending=False)

    # Market breadth: advance-decline ratio
    ad_ratio = round(advancing / declining, 2) if declining > 0 else float('inf')
    ad_ratio = None if ad_ratio == float('inf') else ad_ratio

    output = {
        'meta': {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': len(df),
            'advancing': int(advancing),
            'declining': int(declining),
            'unchanged': int(unchanged),
            'ad_ratio': ad_ratio,
            'total_volume': int(df['volume'].sum()),
            'total_value': round(df['value_mn'].sum(), 2),
            'top_gainer': {'symbol': top_gainer['symbol'], 'change_pct': round(top_gainer['change_pct'], 2), 'ltp': round(top_gainer['ltp'], 2)},
            'top_loser': {'symbol': top_loser['symbol'], 'change_pct': round(top_loser['change_pct'], 2), 'ltp': round(top_loser['ltp'], 2)},
            'most_active_vol': {'symbol': most_active_vol['symbol'], 'volume': int(most_active_vol['volume'])},
            'most_active_val': {'symbol': most_active_val['symbol'], 'value_mn': round(most_active_val['value_mn'], 2)},
            'most_volatile': {'symbol': most_volatile['symbol'], 'intraday_range_pct': round(most_volatile['intraday_range_pct'], 2)},
            'highest_momentum': {'symbol': highest_momentum['symbol'], 'momentum_score': round(highest_momentum['momentum_score'], 2)},
            'highest_spike': {'symbol': highest_spike['symbol'], 'volume_spike': round(highest_spike['volume_spike'], 2)} if highest_spike is not None else None,
            'near_circuit': near_circuit[['symbol', 'change_pct', 'circuit_proximity_pct']].to_dict('records'),
            'indices': indices,
            'market_status': market_status,
            'foreign': foreign,
            'block_deals': block_deals,
            'top20': top20,
            'news': news
        },
        'sector_performance': sector_perf.reset_index().to_dict('records'),
        'stocks': df.to_dict('records')
    }
    return output

import math
def clean_json(obj):
    """Replace Infinity/NaN with None for valid JSON"""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj

# ───────────────────────────────────────────────
# HISTORICAL ARCHIVE
# ───────────────────────────────────────────────
def archive_data(df):
    archive_dir = "dse_archive"
    os.makedirs(archive_dir, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    archive_file = os.path.join(archive_dir, f"{today}.json")
    archive = df[['symbol', 'ltp', 'volume', 'change_pct', 'value_mn']].to_dict('records')
    with open(archive_file, 'w') as f:
        json.dump(clean_json(archive), f, allow_nan=False)
    print(f"   Archived to {archive_file}")

# ───────────────────────────────────────────────
# MAIN JOB
# ───────────────────────────────────────────────
def job():
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DSEX Pro FULL — Running cycle")
    print(f"{'='*60}")

    stock_data = scrape_dse()
    news = scrape_news()
    foreign = scrape_foreign_activity()
    block_deals = scrape_block_deals()
    top20 = scrape_top20()
    indices = scrape_dsex_index()
    market_status = get_market_status()

    if stock_data and len(stock_data) > 50:
        df = compute_metrics(stock_data)
        output = build_output(df, news, foreign, block_deals, top20, indices, market_status)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(clean_json(output), f, indent=2, allow_nan=False)
        archive_data(df)
        print(f"   ✅ Saved {output['meta']['total_stocks']} stocks")
        print(f"   📰 News: {len(news)} items")
        print(f"   🌍 Foreign: Buy ৳{foreign['buy_value_mn']:.1f}M | Sell ৳{foreign['sell_value_mn']:.1f}M | Net ৳{foreign['net_value_mn']:.1f}M")
        print(f"   📦 Block Deals: {len(block_deals)} deals")
        print(f"   📈 Advancing: {output['meta']['advancing']} | 📉 Declining: {output['meta']['declining']}")
        print(f"   🚀 Top Gainer: {output['meta']['top_gainer']['symbol']} (+{output['meta']['top_gainer']['change_pct']}%)")
        if output['meta']['highest_spike']:
            print(f"   💥 Volume Spike: {output['meta']['highest_spike']['symbol']} ({output['meta']['highest_spike']['volume_spike']}x avg)")
        print(f"   📊 DSEX: {indices['DSEX']} | Market: {market_status['status']}")
    else:
        print("   ⚠️  Failed to scrape or insufficient data — keeping previous file")

# ───────────────────────────────────────────────
# SCHEDULER
# ───────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DSEX PRO SCREENER — FULL EDITION (15 FEATURES)")
    print("=" * 60)
    print(f"  Market Hours: {MARKET_OPEN} - {MARKET_CLOSE} (BD Time)")
    print(f"  Refresh: Every {REFRESH_INTERVAL} minutes")
    print(f"  Output: {OUTPUT_FILE}")
    print("  Extras: News | Foreign | Block Deals | Top 20 | Volume Spike | Gap | Circuit")
    print("=" * 60)
    job()
    schedule.every(REFRESH_INTERVAL).minutes.do(job)
    print("\n⏰ Running... Press Ctrl+C to stop")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        sys.exit(0)
