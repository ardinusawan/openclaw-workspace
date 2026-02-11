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

# Backup setiap jam 10 pagi setiap hari
0 10 * * * cd /home/ardinusawan/.openclaw/workspace && python3 tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1

# Backup alternatif setiap jam 2 pagi setiap hari
0 2 * * * cd /home/ardinusawan/.openclaw/workspace && python3 tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1
```

Cron time format:
```
* * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-6, 0=Sunday)
│ │ │ └────── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └────────── Hour (0-23)
```

### Verifikasi Cron Job

```bash
# List cron jobs
crontab -l

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
4. Name: `OpenClaw-Papa` atau nama lain
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
- **Untuk personal use:** Biasanya cukup

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
python3 ~/.openclaw/workspace/tools/ddg_search.py "IHSG hari ini"
```

---

## Stock Market Data

### yfinance (Yahoo Finance - Recommended)

```bash
# Install package
pip install yfinance
```

Usage:
```bash
# IHSG
python3 ~/.openclaw/workspace/tools/ihsg_data.py "^JKSE"

# Stock
python3 ~/.openclaw/workspace/tools/ihsg_data.py "BBRI.JK"
python3 ~/.openclaw/workspace/tools/ihsg_data.py "BMRI.JK"
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

## pyttsx3 (Python-based)

```bash
pip install pyttsx3
```

Create helper script `~/.openclaw/workspace/tools/tts.py`:
```python
import pyttsx3
import sys

engine = pyttsx3.init()
text = " ".join(sys.argv[1:])
engine.save_to_file(text, "output.wav")
engine.runAndWait()
print(f"Saved: {text} -> output.wav")
```

Usage:
```bash
python3 ~/.openclaw/workspace/tools/tts.py "Halo ini tes"
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

Create helper script `~/.openclaw/workspace/tools/ocr.py`:
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
python3 ~/.openclaw/workspace/tools/ocr.py "/path/to/image.jpg"
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

Create helper script `~/.openclaw/workspace/tools/fetch.py`:
```python
from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=30000)
    
    # Extract text
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
python3 ~/.openclaw/workspace/tools/fetch.py "https://finance.yahoo.com/quote/%5EJKSE"
```

---

## Troubleshooting

### Permission Issues

```bash
# Use --break-system-packages for system-wide pip install
python3 /tmp/get-pip.py --user --break-system-packages

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
mkdir -p ~/.openclaw/workspace/tools
cd ~/.openclaw/workspace/tools
```

Recommended scripts:
- `backup.py` - Auto daily backup script (NEW!)
- `ddg_search.py` - DuckDuckGo search
- `ihsg_data.py` - IHSG & stock data
- `fetch.py` - Web fetch with Playwright
- `tts.py` - Text-to-speech
- `ocr.py` - Text recognition

---

## Summary Command List

```bash
# Core setup (run in order)
asdf plugin-add python
asdf plugin-add nodejs
asdf plugin-add rust
asdf install python latest
asdf install nodejs lts
asdf install rust latest
asdf global python latest nodejs lts rust latest

# Python packages
pip install yfinance pandas numpy pyttsx3 duckduckgo-search playwright pytesseract Pillow

# System packages
sudo apt install espeak-ng tesseract-ocr tesseract-ocr-indo libopusfile0 ffmpeg

# Web search
openclaw configure --section web

# Node pairing
npm install -g @openclaw/node

# Helper scripts directory
mkdir -p ~/.openclaw/workspace/tools
cd ~/.openclaw/workspace/tools

# Restore workspace (with token)
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Daily backup (manual)
cd ~/.openclaw/workspace
python3 tools/backup.py

# Setup cron job (auto backup daily at 10:00)
crontab -e
# Paste: 0 10 * * * cd /home/ardinusawan/.openclaw/workspace && python3 tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1
```

---

## Quick Start

```bash
# 1. Core setup (run in order)
asdf plugin-add python
asdf plugin-add nodejs
asdf plugin-add rust
asdf install python latest nodejs lts rust latest
asdf global python latest nodejs lts rust latest

# 2. Install essential packages
pip install yfinance duckduckgo-search playwright
sudo apt install espeak-ng tesseract-ocr

# 3. Configure web search (Brave API)
openclaw configure --section web

# 4. Create tools directory
mkdir -p ~/.openclaw/workspace/tools
cd ~/.openclaw/workspace/tools

# 5. Setup cron job (auto backup daily)
crontab -e
# Paste: 0 10 * * * cd /home/ardinusawan/.openclaw/workspace && python3 tools/backup.py >> /home/ardinusawan/cron_backup.log 2>&1
```

---

## Support

If you need help with setup, ask Nara (OpenClaw assistant) and specify which section you need help with.

---

**Last Updated:** 2026-02-11
**Version:** 2.0 (Final - Setup Perfection)
**Platform:** Orange Pi 5 (ARM64)
**OS:** Ubuntu-based Linux
