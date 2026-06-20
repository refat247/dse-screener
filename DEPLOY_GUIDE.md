# DSEX Pro — Cloud Deployment Guide
## Fully Automated, No PC Running

---

## 🎯 What This Setup Does

1. **GitHub Actions** runs `scraper.py` every 5 minutes during BD market hours
2. The scraper saves `dse_data.json` to the repo
3. **GitHub Pages** serves the HTML + JSON to any device worldwide
4. You access it from **phone, PC, tablet** — no PC running required

---

## 📋 Step-by-Step Setup (10 minutes)

### Step 1: Create a GitHub Account
- Go to [github.com](https://github.com)
- Sign up (free)

### Step 2: Create a New Repository
1. Click **+** → **New repository**
2. Name: `dse-screener` (or anything)
3. Make it **Public**
4. Check **"Add a README file"**
5. Click **Create repository**

### Step 3: Upload These Files
Upload ALL files from this folder to your repo:

```
├── index.html           ← The screener app
├── scraper.py           ← The scraper engine
├── manifest.json        ← PWA support
├── dse_data.json        ← Demo data (will be overwritten by scraper)
└── .github/workflows/
    └── scrape.yml       ← Auto-scheduler
```

**How to upload:**
1. In your repo, click **"Add file"** → **"Upload files"**
2. Drag and drop all files
3. Click **"Commit changes"**

### Step 4: Enable GitHub Pages
1. Go to **Settings** (top of repo)
2. Click **Pages** (left sidebar)
3. Under **Source**, select **Deploy from a branch**
4. Select **main** branch, **/ (root)** folder
5. Click **Save**
6. Wait 2-3 minutes for the green checkmark
7. Your URL will be: `https://YOURNAME.github.io/dse-screener/`

### Step 5: Enable GitHub Actions
1. Go to **Actions** tab (top of repo)
2. Click **"I understand my workflows, go ahead and enable them"**
3. The scraper will start running automatically!

### Step 6: Test It
- Open your URL: `https://YOURNAME.github.io/dse-screener/`
- You should see the screener with live data
- On your phone: open the same URL → Chrome menu → **"Add to Home Screen"**

---

## ⏰ Scraping Schedule

The scraper runs **every 5 minutes** during BD market hours:

- **BD Time:** 10:00 AM – 2:30 PM (Sunday–Thursday)
- **UTC Time:** 4:00 AM – 8:30 AM (Sunday–Thursday)
- **GitHub Actions uses UTC**, so the schedule is: `*/5 4-8 * * 0-4`

**Outside market hours:** The scraper runs but DSEBD may return old data or fail. That's fine — it keeps the last known data.

---

## 📱 Daily Usage (From Anywhere)

| Device | How to Open | Notes |
|--------|-------------|-------|
| **PC** | Bookmark `https://YOURNAME.github.io/dse-screener/` | Works in any browser |
| **Android** | Chrome → open URL → Menu → "Add to Home Screen" | Installs as app |
| **iPhone** | Safari → open URL → Share → "Add to Home Screen" | Installs as app |
| **Tablet** | Same as phone | Works perfectly |

**Your watchlist, portfolio, alerts, and presets are saved in your browser's `localStorage`** — they survive restarts, but are device-specific.

---

## 🔄 What Happens Automatically

| Time | What Happens |
|------|-------------|
| **9:45 AM BD** | GitHub Actions starts scraper |
| **Every 5 min** | Scraper fetches live DSE data, commits `dse_data.json` |
| **10:00 AM BD** | Market opens — data starts flowing |
| **2:30 PM BD** | Market closes — scraper continues with last data |
| **You open app** | HTML fetches latest `dse_data.json` from GitHub Pages |

---

## ⚠️ Important Notes

### 1. GitHub Actions Free Limits
- **2,000 minutes/month** (more than enough for this)
- Our scraper uses ~30 minutes/day = **~660 minutes/month**

### 2. DSEBD May Block GitHub IPs
If DSEBD blocks GitHub's servers, the scraper will fail and keep the previous data. Solutions:
- Use a **proxy** (advanced)
- Fall back to **local scraper** on your PC
- Use a **paid VPS** ($5/month on DigitalOcean/Linode)

### 3. Data Freshness
- The data you see is **at most 5 minutes old**
- During market hours, it refreshes every 5 minutes
- After market close, the last data stays until next session

---

## 🛠️ Troubleshooting

### "Scraper shows failed in Actions tab"
→ DSEBD might be blocking GitHub's IP. Check the error log. If it says connection timeout or 403, that's the issue.

### "Page shows offline"
→ `dse_data.json` might be missing. Check that GitHub Actions committed it. Go to your repo → check if `dse_data.json` exists.

### "I want to run scraper manually"
→ Go to **Actions** → **DSEX Auto-Scraper** → **Run workflow** → click **Run workflow**

### "I want to change the refresh interval"
→ Edit `.github/workflows/scrape.yml` → change `*/5` to `*/10` (every 10 min) or `*/15` (every 15 min)

---

## 🚀 Upgrade: Paid VPS (If GitHub Is Blocked)

If DSEBD blocks GitHub, rent a $5/month VPS:

1. **DigitalOcean** / **Linode** / **Vultr** — $5/month
2. Install Python + dependencies
3. Run `scraper.py` with `nohup`
4. The VPS runs 24/7, scrapes every 5 minutes
5. Host the HTML on the same VPS or keep using GitHub Pages

**This is only needed if GitHub Actions fails consistently.**

---

## 📂 File Structure (Final)

```
YOUR_GITHUB_REPO/
├── index.html              ← Screener app (Cloud Edition)
├── scraper.py              ← Scraper (runs on GitHub Actions)
├── dse_data.json           ← Live data (auto-updated by Actions)
├── manifest.json           ← PWA install support
├── dse_archive/            ← Daily snapshots (if enabled)
├── .github/
│   └── workflows/
│       └── scrape.yml      ← GitHub Actions schedule
└── README.md               ← This guide
```

---

## ✅ Quick Checklist

- [ ] Created GitHub account
- [ ] Created public repo
- [ ] Uploaded all files
- [ ] Enabled GitHub Pages
- [ ] Enabled GitHub Actions
- [ ] Tested URL on phone + PC
- [ ] Added to Home Screen on phone
- [ ] Set up alerts + watchlist

**Once done, your screener runs 24/7 without your PC. Access it from anywhere.**
