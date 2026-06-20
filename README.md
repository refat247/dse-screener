# 🇧🇩 DSEX Pro Screener

**Live Bangladesh Stock Exchange Screener** — Auto-refreshing DSE data with 15 professional features.

## 🌐 Live App

👉 **Open in browser:** `https://YOURNAME.github.io/dse-screener/`

*(Replace YOURNAME with your GitHub username)*

## ✨ Features

| Feature | Description | TradingView Free? |
|---|---|---|
| 🔴 **Live Data** | Auto-refreshes every 5 min from DSEBD | ❌ |
| 📰 **News Ticker** | DSE announcements, dividends, AGMs | ❌ |
| 🌍 **Foreign Activity** | Foreign buy/sell/net flow | ❌ |
| 📦 **Block Deals** | Large institutional trades | ❌ |
| ⚡ **Circuit Proximity** | How close to ±10% limit | ❌ |
| 📊 **Volume Spike** | Volume vs 5-day average | ❌ |
| 📈 **Gap Scanner** | Gap up/down filters | ❌ |
| 🔔 **Push Alerts** | Browser notifications for price targets | ❌ 1 alert only |
| 💼 **Portfolio** | Track P&L in real-time | ❌ Paid only |
| ⭐ **Watchlist** | Save favorite stocks | ❌ |
| 💾 **Filter Presets** | Save scan configurations | ❌ Deleted in TV 2.0 |
| 🔗 **Shareable URLs** | Copy filter setups to share | ❌ |
| 📥 **CSV Export** | Download any filtered result | ❌ $12.95/mo |
| 🌓 **Dark/Light Theme** | Toggle anytime | ✅ |
| 🖨️ **Print Report** | Clean print-friendly table | ❌ |

## 🚀 How to Use

### PC
1. Open the live URL in any browser
2. Bookmark it

### Phone (Install as App)
- **Android:** Chrome → Menu → "Add to Home Screen"
- **iPhone:** Safari → Share → "Add to Home Screen"
- Works offline after first load

## 🔄 Auto-Refresh

Data updates automatically:
- **During market hours:** Every 5 minutes (10:00 AM – 2:30 PM BD Time)
- **After hours:** Last known data stays
- **Scraper runs on:** GitHub Actions (free, cloud)

## 📁 Files

| File | Purpose |
|---|---|
| `index.html` | The screener app |
| `scraper.py` | Python scraper (runs on GitHub Actions) |
| `dse_data.json` | Live stock data (auto-updated) |
| `.github/workflows/scrape.yml` | Auto-scheduler |

## ⚠️ Troubleshooting

| Problem | Fix |
|---|---|
| "Offline" badge | Scraper may be between runs — wait 5 min and refresh |
| Old data | Check [Actions tab](https://github.com/YOURNAME/dse-screener/actions) for scraper status |
| No notifications | Click 🔔 → "Enable Notifications" in the app |

## 🛠️ Built With

- HTML + Vanilla JS (no frameworks)
- Python + BeautifulSoup + Pandas
- GitHub Actions + GitHub Pages (free hosting)

---

*Data source: [DSEBD](https://dsebd.org) | Built for Bangladesh traders*
