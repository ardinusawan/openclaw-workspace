# OpenClaw Setup Guide - Orange Pi 5

## Quick Start

```bash
# 1. Install asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
source ~/.bashrc

# 2. Add plugins
asdf plugin add python
asdf plugin add nodejs
asdf plugin add rust

# 3. Install versions
asdf install python latest
asdf install nodejs lts
asdf install rust latest

# 4. Set global
asdf global python latest nodejs lts rust latest

# 5. Python packages
pip install yfinance pandas numpy pyttsx3 duckduckgo-search playwright

# 6. System packages
sudo apt install espeak-ng tesseract-ocr tesseract-ocr-indo libopusfile0 ffmpeg

# 7. Web search (get BRAVE_API_KEY from below)
openclaw configure --section web

# 8. Node pairing
npm install -g @openclaw/node
openclaw-node pair
```

---

## Get BRAVE_API_KEY

**Steps:**

1. Go to: https://brave.com/search/api/ or https://api.brave.com/app/keys
2. Sign up/login (use GitHub/Google for fastest)
3. Click "Create API Key"
4. Name: `OpenClaw-Papa`
5. Type: `Search` or `Browser Search API`
6. Click "Create"
7. **COPY API KEY** (format: `BSAxxxxx` or `BSxxxxx`) - only shown once!

**Setup OpenClaw:**
```bash
openclaw configure --section web
# Paste API key when prompted
```

**Limits:** 2,000 requests/month (free)
**Revoke:** https://github.com/settings/tokens if leaked

**Alternative Options:** See [Alternative Search](#alternative-search) section below for DuckDuckGo, Chrome headless, and more.

---

## Stock Data

```bash
pip install yfinance
python3 -c "import yfinance as yf; print(yf.Ticker('^JKSE').history('5d'))"
```

---

## Alternative Search

### Free Search Options (Besides Brave API)

**Options:**

1. **DuckDuckGo** (Recommended Backup)
   - Unlimited requests
   - No API key needed
   - See `tools/ddg_search.py`
   - Usage: `python3 tools/ddg_search.py "query"`

2. **SerpAPI** (Free: 100/hour)
   - Multiple search engines (Google, Bing, etc.)
   - Get free API key from https://serpapi.com/
   - See detailed guide: `ALTERNATIVE_SEARCH.md`

3. **Bing Web Search API** (Microsoft)
   - Free: 1,000 requests/month
   - Get API key from Azure Portal

4. **Wolfram Alpha** (Math/Science)
   - Free: 2,000 requests/month
   - Get App ID from https://developer.wolframalpha.com/

5. **Google Custom Search API**
   - Free: 100 requests/hour
   - Requires Google Cloud account

6. **Chrome Headless** (Scraping - CAUTION!)
   - Unlimited but:
     - ⚠️ Violates Terms of Service
     - ⚠️ IP can be blocked
     - ⚠️ Unstable, HTML changes often
   - Only use for personal/educational purposes
   - See detailed guide: `ALTERNATIVE_SEARCH.md`

### Comparison

| Service | Free Tier | Best For |
|---------|-----------|----------|
| Brave | 2,000/month | General search |
| DuckDuckGo | Unlimited | Privacy, general |
| SerpAPI | 100/hour | Multiple engines |
| Bing | 1,000/month | General |
| Wolfram Alpha | 2,000/month | Math, science, facts |
| Chrome | Unlimited (risky) | Scraping |

### Recommendation

**For Personal Use:**
1. **Brave API** (2,000/month) - Stable & legal
2. **DuckDuckGo** (Unlimited) - No API key needed

**Avoid Production Scraping:**
- Chrome headless violates ToS
- Use official APIs for production systems
- Scaping only for educational/personal use

**Detailed Guide:**
See `ALTERNATIVE_SEARCH.md` for complete setup instructions for each alternative including helper scripts, API key setup, and security warnings.

---

## Git Repository Setup

**Public:** https://github.com/ardinusawan/openclaw-workspace (scripts, docs)
**Private:** https://github.com/ardinusawan/openclaw-private-data (MEMORY.md, config)

**Restore:**
```bash
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data
```

---

## Daily Backup

```bash
# Private data
cd ~/.openclaw/workspace/private-data
git add . && git commit -m "Backup" && git push

# Public files
cd ~/.openclaw/workspace
git add . && git commit -m "Backup" && git push
```

---

## Troubleshooting

```bash
# Permission issues
pip install --break-system-packages

# Node/python not found
asdf reshim

# Git auth failed
git clone https://<TOKEN>@github.com/...
```

---

**Platform:** Orange Pi 5 (ARM64) | **OS:** Ubuntu-based
**Last Updated:** 2026-02-11 | **Version:** 2.1
