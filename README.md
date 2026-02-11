# OpenClaw Setup Guide - Orange Pi 5

## Quick Start

```bash
# 1. Install asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
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

**Alternative:** DuckDuckGo (no API key needed)

---

## Stock Data

```bash
pip install yfinance
python3 -c "import yfinance as yf; print(yf.Ticker('^JKSE').history('5d'))"
```

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
**Last Updated:** 2026-02-11 | **Version:** 2.0 (Ringkas)
