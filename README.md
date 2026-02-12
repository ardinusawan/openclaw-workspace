# OpenClaw Setup Guide - Orange Pi 5

## Quick Start

```bash
# 1. Install asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
source ~/.bashrc

# 2. Add Plugins (DO THIS FIRST!)
asdf plugin-add python
asdf plugin-add nodejs
asdf plugin-add rust

# 3. Install Versions
asdf install python latest
asdf install nodejs lts
asdf install rust latest

# 4. Set Global
asdf global python latest nodejs lts rust latest

# 5. Verify
python --version
node --version
rustc --version

# 6. Python Packages
pip install yfinance pandas numpy pyttsx3 duckduckgo-search playwright

# 7. System Packages
sudo apt install espeak-ng tesseract-ocr tesseract-ocr-indo libopusfile0 ffmpeg

# 8. Web Search (Brave API)
openclaw configure --section web
# Follow prompts to enter BRAVE_API_KEY

# 9. Node Pairing
npm install -g @openclaw/node
openclaw-node pair
```

---

## Workspace Structure

```
.openclaw/workspace/
├── docs/              # Documentation
│   ├── AGENTS.md
│   ├── ALTERNATIVE_SEARCH.md
│   ├── BOOTSTRAP.md
│   ├── HEARTBEAT.md
│   ├── IDENTITY.md
│   ├── RESTORE_GUIDE.md
│   └── TOOLS.md
│
├── scripts/            # All Python & Shell scripts
│   ├── trading/      # Trading scripts
│   │   ├── download_stock_data.py
│   │   ├── SWING_TRADING_RESEARCH.md
│   │   ├── analyze_bbri.py
│   │   ├── bmri_analysis.py
│   │   ├── stock_analysis.py
│   │   ├── stock_report.py
│   │   └── comprehensive_analysis.py
│   └── tools/        # Helper tools
│       ├── backup.py
│       ├── fetch.py
│       ├── ocr.py
│       └── tts.py
│
├── playbooks/         # Ansible playbooks
│   ├── playbook-migrate-final.yml
│   ├── playbook-migrate-simple.yml
│   ├── playbook-migrate.yml
│   ├── playbook.yml
│   └── playbook-path-fix.yml
│
├── configs/           # Configuration files
│   └── main.yml
│
├── roles/             # Ansible roles
│   ├── openclaw.backup/
│   ├── openclaw.migrate/
│   ├── openclaw.verify/
│   ├── openclaw.asdf/
│   ├── openclaw.git/
│   ├── openclaw.cron/
│   ├── openclaw.brave_api/
│   ├── openclaw.nodejs/
│   ├── openclaw.python/
│   ├── openclaw.ssh/
│   ├── openclaw.gateway/
│   ├── openclaw.system/
│   └── openclaw.current_state/
│
├── memory/            # Memory files (private-data submodule)
│   └── 2026-02-11-*.md
│
├── private-data/      # Private submodule (gitignored)
│   ├── MEMORY.md
│   ├── config.json
│   ├── media/
│   └── memory/
│
├── .README_PUBLIC.md
├── BOOTSTRAP.md
├── HEARTBEAT.md
├── IDENTITY.md
├── README.md          # Main documentation (THIS FILE)
├── SOUL.md
├── TOOLS.md
├── HYBRID_GIT_SETUP.md
├── USER.md
└── STOCK_REPORT.md
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

### yfinance (Yahoo Finance - Recommended)

```bash
pip install yfinance
python3 -c "import yfinance as yf; print(yf.Ticker('^JKSE').history('5d'))"
```

### Custom Analysis Scripts

**BMRI Analysis:**
```bash
cd scripts/trading
python3 bmri_analysis.py
```

**Stock Data Downloader:**
```bash
cd scripts/trading
python3 download_stock_data.py
```

---

## Git Repository Setup

### Structure

**Public Repository:** `openclaw-workspace` - Scripts, tools, documentation (shareable)
**Private Repository:** `openclaw-private-data` - Personal data, config, media (private)
**Setup:** Private repository is added as a **submodule** to public repository

### Repository Links

- 🔓 Public: https://github.com/ardinusawan/openclaw-workspace
- 🔒 Private: https://github.com/ardinusawan/openclaw-private-data

### Restore (Clone) Workflow

#### Step 1: Clone Public Repository

```bash
# Clone public repository (without submodules initially)
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace

cd ~/.openclaw/workspace
```

#### Step 2: Setup Git User (if needed)

```bash
git config user.name "ardinusawan"
git config user.email "ardinusawan@users.noreply.github.com"
```

#### Step 3: Clone Private Submodule

The private submodule requires authentication. You have two options:

**Option A: Using Personal Access Token**

```bash
# Navigate to workspace
cd ~/.openclaw/workspace

# Clone private submodule with token
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Verify
ls private-data/
# Should see: MEMORY.md, config.json, media/, memory/
```

**Replace `<TOKEN>` with your Personal Access Token from GitHub.**

**Option B: Using SSH Keys (Recommended)**

```bash
# Setup SSH keys (if not already)
ssh-keygen -t ed25519 -C "ardinusawan@ardi-desktop"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: https://github.com/settings/keys

# Then clone submodule
cd ~/.openclaw/workspace
git submodule init
git submodule update
```

---

## Daily Backup with Cron

### Setup Cron Job

Cara setup cron job untuk auto backup setiap hari:

```bash
# 1. Buka crontab editor
crontab -e

# 2. Tambah baris berikut (paste di bagian bawah):

# Backup setiap hari jam 10:00 pagi (UTC+7 berarti jam 10:00)
0 10 * * * cd /home/ardinusawan/.openclaw/workspace && python3 scripts/tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1

# Backup alternatif setiap hari jam 10:30 pagi (UTC+7 berarti jam 10:30)
30 10 * * * cd /home/ardinusawan/.openclaw/workspace && python3 scripts/tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1
```

Cron time format:
```
* * * * command
│ │ │ │ │ └─── Day of week (0-6, 0=Sunday)
│ │ │ │ └────── Month (1-12)
│ │ └────────── Hour (0-23)
└─────────────── Minute (0-59)
```

### Verifikasi Cron Job

```bash
# List cron jobs
crontab -l | grep backup

# Cek log cron
tail -f /home/ardinusawan/cron_backup.log

# Cek log terakhir
cat /home/ardinusawan/cron_backup.log
```

---

## Brave Search API Integration

### Overview

Brave Search API telah diintegrasikan ke sistem backup Anda.

### Get Brave API Key

1. Buka: https://brave.com/search/api/ atau https://api.brave.com/app/keys
2. Sign up/login (pakai GitHub/Google untuk tercepat!)
3. Click "Create API Key"
4. Name: `OpenClaw-Papa`
5. Type: `Search` atau `Browser Search API`
6. Click "Create"
7. **COPY API KEY** (format: `BSAxxxxx` atau `BSxxxxx`) - hanya muncul sekali!

### Setup OpenClaw

```bash
openclaw configure --section web
# Masukkan API key ketika diminta
```

### Limits

- **Gratis:** 2,000 requests/bulan
- **Untuk penggunaan personal:** Biasanya cukup

### Security Notes

⚠️ **Important:**

- **Personal Access Tokens** are like passwords - treat them as secrets
- Never commit tokens to repositories
- Never share tokens in public channels
- Revoke tokens when no longer needed
- Use SSH keys instead of tokens for better security

### Revoke Old Token

```bash
# Go to: https://github.com/settings/tokens
# Find old token and click "Delete"
```

---

## Web Search (Alternative Options)

### DuckDuckGo (No API Key Required)

```bash
# Install package
pip install duckduckgo-search
```

Usage:
```bash
python3 scripts/tools/backup.py  # Backup script uses duckduckgo-search for fallback
```

---

## Voice/TTS

### espeak-ng (Very Lightweight)

```bash
sudo apt install espeak-ng
```

Usage:
```bash
espeak-ng "Halo ini tes" -w output.wav
```

---

## OCR (Text Recognition)

### Tesseract Setup

```bash
# Install Tesseract
sudo apt install tesseract-ocr

# Install Indonesian language data
sudo apt install tesseract-ocr-indo

# Verify
tesseract --version
```

Create helper script `scripts/tools/ocr.py`:
```python
import sys
import pytesseract
from PIL import Image

image_path = sys.argv[1]
image = Image.open(image_path)

# OCR with Indonesian language
text = pytesseract.image_to_string(image, lang='ind')

print(text)
```

Python dependencies:
```bash
pip install pytesseract Pillow
```

Usage:
```bash
python3 scripts/tools/ocr.py "/path/to/image.jpg"
```

---

## Hardware Control

### OpenClaw Node Pairing (Built-in, Recommended)

**On target device (laptop/phone):**
```bash
npm install -g @openclaw/node
openclaw-node pair
```

**On Orange Pi 5 (main device):**
```bash
openclaw nodes pending
openclaw nodes approve <device-id>
```

**Use from OpenClaw:**
```bash
openclaw nodes camera-snap
openclaw nodes screen-record
openclaw nodes location-get
```

---

## Web Fetch (Bypass Cloudflare)

### Playwright (Python - Can Bypass Cloudflare)

```bash
pip install playwright
playwright install
```

Create helper script `scripts/tools/fetch.py`:
```python
from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate ke Google
    page.goto(url, wait_until="networkidle", timeout=30000)
    
    # Ekstrak text
    text = page.inner_text("body")
    
    # Extract structured data if needed
    try:
        title = page.title()
        print(f"Title: {title}")
        print(f"\nContent:\n{text[:5000]}")
    except:
        print(text)
    
    browser.close()
```

Usage:
```bash
python3 scripts/tools/fetch.py "https://finance.yahoo.com/quote/%5EJKSE"
```

---

## Troubleshooting

### Permission Issues

```bash
# Use --break-system-packages for system-wide pip install
pip install --break-system-packages

# Or use virtual environment
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip install <package>
```

### Node.js Command Not Found

```bash
# Ensure asdf is loaded
source ~/.bashrc
which node
which npm

# Reinstall if needed
asdf reshim nodejs
```

### Python Command Not Found

```bash
# Ensure asdf is loaded
source ~/.bashrc
which python
python --version

# Reinstall if needed
asdf reshim python
```

### Tesseract Language Not Found

```bash
# Install additional languages
sudo apt install tesseract-ocr-<lang-code>

# Example for English
sudo apt install tesseract-ocr-eng

# List available languages
apt-cache search tesseract-ocr
```

### Git Authentication Issues

```bash
# For private submodule cloning
# Option A: Use Personal Access Token
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Option B: Use SSH Keys
ssh-keygen -t ed25519 -C "ardinusawan@ardi-desktop"
# Add public key to: https://github.com/settings/keys
```

---

## Helper Scripts

Create directory:
```bash
mkdir -p scripts/tools
cd scripts/tools
```

Recommended scripts:
- `backup.py` - Auto daily backup script (NEW!)
- `fetch.py` - Web fetch with Playwright
- `ocr.py` - Text recognition
- `tts.py` - Text-to-speech

---

## Summary Command List

```bash
# Core setup (run in order)
# Step 1: Add plugins
asdf plugin-add python
asdf plugin-add nodejs
asdf plugin-add rust

# Step 2: Install versions
asdf install python latest
asdf install nodejs lts
asdf install rust latest

# Step 3: Set as global
asdf global python latest nodejs lts rust latest

# Python packages
pip install yfinance pandas numpy pyttsx3 duckduckgo-search playwright

# System packages
sudo apt install espeak-ng tesseract-ocr tesseract-ocr-indo libopusfile0 ffmpeg

# Web search
openclaw configure --section web

# Node pairing
npm install -g @openclaw/node
```

---

**Platform:** Orange Pi 5 (ARM64) | **OS:** Ubuntu-based Linux
**Last Updated:** 2026-02-12 | **Version:** 2.2 (Workspace Reorganized)
