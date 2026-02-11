# OpenClaw Technical Guide - Orange Pi 5

## Setup Overview

This guide covers all technical setup needed to overcome OpenClaw limitations on Orange Pi 5 with Ubuntu-based system.

---

## Quick Reference

```bash
# Core installations (run in order)
asdf install python latest  # Python
asdf install nodejs lts   # Node.js LTS
asdf global python latest nodejs lts

# Python packages
pip install yfinance pandas numpy pyttsx3 duckduckgo-search playwright

# System packages
sudo apt install espeak-ng tesseract-ocr tesseract-ocr-indo libopusfile0

# Setup web search
openclaw configure --section web  # Enter BRAVE_API_KEY

# Node pairing (on target device)
npm install -g @openclaw/node
openclaw-node pair
```

---

## Table of Contents

1. [Core Installations](#core-installations)
2. [Web Search](#web-search)
3. [Stock Market Data](#stock-market-data)
4. [Voice/TTS](#voicetts)
5. [Vision/Image Generation](#visionimage-generation)
6. [Hardware Control](#hardware-control)
7. [Web Fetch](#web-fetch)
8. [OCR (Text Recognition)](#ocr-text-recognition)
9. [Git Repository Setup](#git-repository-setup)
10. [Priority Setup](#priority-setup)

---

## Core Installations

### Install Python with asdf

```bash
# Install asdf if not already installed
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
source ~/.bashrc

# Install Python plugin
asdf plugin add python

# Install latest Python
asdf install python latest

# Set as global
asdf global python latest

# Verify
python --version
which python
```

---

### Install Node.js LTS with asdf

```bash
# Install Node.js plugin
asdf plugin add nodejs

# Install LTS version
asdf install nodejs lts

# Set as global
asdf global nodejs lts

# Verify
node --version
npm --version

# Setup for OpenClaw Node
sudo ln -sf $(which node) /usr/bin/node
sudo ln -sf $(which npm) /usr/bin/npm
```

---

### Install pip (if missing)

```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py

# Install pip
python3 /tmp/get-pip.py --user --break-system-packages

# Verify
python3 -m pip --version
```

---

## Web Search

### Option A: Brave Search API (Recommended)

1. Go to: https://brave.com/search/api/
2. Sign up (free)
3. Copy API key (2,000 requests/month free)

Setup OpenClaw:
```bash
openclaw configure --section web
# Enter your BRAVE_API_KEY when prompted
```

---

### Option B: DuckDuckGo (Opensource)

```bash
# Install package
pip install duckduckgo-search
```

Create helper script `~/.openclaw/workspace/tools/ddg_search.py`:
```python
from duckduckgo_search import DDGS
import sys

query = " ".join(sys.argv[1:])
results = DDGS().text(query, max_results=5)

for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}\n   {r['href']}\n   {r['body']}\n")
```

Usage:
```bash
python3 ~/.openclaw/workspace/tools/ddg_search.py "IHSG hari ini"
```

---

## Stock Market Data

### Option A: yfinance (Yahoo Finance - Recommended)

```bash
# Install package
pip install yfinance
```

Create helper script `~/.openclaw/workspace/tools/ihsg_data.py`:
```python
import yfinance as yf
import sys
from datetime import datetime, timedelta

ticker = sys.argv[1] if len(sys.argv) > 1 else "^JKSE"
period = sys.argv[2] if len(sys.argv) > 2 else "5d"

data = yf.Ticker(ticker).history(period=period)
print(f"\n{ticker} - {data.index[-1].strftime('%Y-%m-%d')}")
print("=" * 50)
print(data[['Open', 'High', 'Low', 'Close', 'Volume']])
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

### Option B: InvestPy (Indonesia-specific)

```bash
pip install investpy
```

Script:
```python
import investpy as inv
df = inv.get_stock_historical_data('BBRI', 'indonesia', '01/01/2026', '11/02/2026')
print(df)
```

---

## Voice/TTS

### Option A: espeak-ng (Very Lightweight)

```bash
sudo apt install espeak-ng
```

Usage:
```bash
espeak-ng "Halo ini tes" -w output.wav
```

---

### Option B: pyttsx3 (Python-based)

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

### Option C: Piper TTS (Neural TTS, Best Quality)

```bash
# Install dependencies
sudo apt install libopusfile0

# Clone and build
git clone https://github.com/rhasspy/piper.git
cd piper
./build.sh

# Download Indonesian model
wget https://huggingface.co/rhasspy/piper-voices/raw/v1.0.0/id/id/medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/raw/v1.0.0/id/id/medium.onnx.json
```

Usage:
```bash
./piper-tts --model medium.onnx --output_file output.wav "Halo ini tes"
```

---

## Vision/Image Generation

### Option A: Stable Diffusion (Best Quality, Opensource)

```bash
# Install dependencies
sudo apt install git python3-venv

# Clone repository
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# Install Python environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install torch torchvision torchaudio
pip install -r requirements.txt

# Run web interface
./webui.sh --listen --port 7860
```

Access: http://localhost:7860

API Integration:
Create script that calls SD WebUI API, then call from OpenClaw via `exec`.

---

### Option B: OpenDalle (Lightweight)

```bash
pip install opendalle
```

Create helper script `~/.openclaw/workspace/tools/image_gen.py`:
```python
import sys
from opendalle import OpenDalle

# Load model
generator = OpenDalle.from_pretrained("model")

# Generate image
prompt = " ".join(sys.argv[1:])
image = generator(prompt)
image.save("output.png")
print(f"Generated: {prompt} -> output.png")
```

Usage:
```bash
python3 ~/.openclaw/workspace/tools/image_gen.py "beautiful sunset landscape"
```

---

## Hardware Control

### Option A: OpenClaw Node Pairing (Built-in, Recommended)

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

### Option B: FFmpeg (Opensource)

```bash
sudo apt install ffmpeg
```

Usage:
```bash
# Screen record
ffmpeg -f x11grab -r 30 -s 1920x1080 -i :0.0 output.mp4

# Camera capture
ffmpeg -f v4l2 -i /dev/video0 output.mp4
```

---

## Web Fetch (Bypass Cloudflare)

### Option A: Playwright (Python - Can Bypass Cloudflare)

```bash
pip install playwright
playwright install
```

Create helper script `~/.openclaw/workspace/tools/fetch.py`:
```python
from playwright.sync_api import sync_playwright
import sys
import json

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

### Option B: curl with User-Agent

```bash
curl -A "Mozilla/5.0 (X11; Linux armv8l) AppleWebKit/537.36" https://example.com
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

## Git Repository Setup

### Repository Structure

This workspace uses a **Hybrid Git Setup**:

- **Public Repository:** `openclaw-workspace` - Scripts, tools, documentation (shareable)
- **Private Repository:** `openclaw-private-data` - Personal data, config, media (private)
- **Setup:** Private repository is added as a **submodule** to public repository

**Repository Links:**
- 🔓 Public: https://github.com/ardinusawan/openclaw-workspace
- 🔒 Private: https://github.com/ardinusawan/openclaw-private-data

---

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

### Daily Backup Workflow

#### Backup Private Data

```bash
cd ~/.openclaw/workspace/private-data
git add .
git commit -m "Daily backup $(date +%Y-%m-%d)"
git push
```

#### Backup Public Files

```bash
cd ~/.openclaw/workspace
git add .
git commit -m "Daily backup scripts $(date +%Y-%m-%d)"
git push
```

---

### Complete Restore Script

Automate entire restore process:

```bash
#!/bin/bash
# restore-openclaw.sh

# Step 1: Clone public repo
git clone https://github.com/ardinusawan/openclaw-workspace.git ~/.openclaw/workspace

# Step 2: Setup git user
cd ~/.openclaw/workspace
git config user.name "ardinusawan"
git config user.email "ardinusawan@users.noreply.github.com"

# Step 3: Clone private submodule (replace <TOKEN>)
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data

# Step 4: Verify
echo "✅ Restore complete!"
ls -la
echo "✅ Private data:"
ls private-data/
```

Save as `restore-openclaw.sh`, make executable: `chmod +x restore-openclaw.sh`

---

### Troubleshooting

#### Submodule Empty After Clone

**Problem:** `private-data/` directory exists but empty.

**Solution:** Private submodule needs authentication.

```bash
cd ~/.openclaw/workspace
rm -rf private-data
git clone https://<TOKEN>@github.com/ardinusawan/openclaw-private-data.git private-data
```

#### Submodule Detached HEAD

**Problem:** Submodule is in detached state.

**Solution:** Checkout main branch.

```bash
cd ~/.openclaw/workspace/private-data
git checkout main
```

#### Token Not Working

**Problem:** Authentication fails with token.

**Solution:** Generate new Personal Access Token.

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Ensure `repo` permission is checked
4. Use new token

---

### Security Notes

⚠️ **Important Security Information:**

- **Personal Access Tokens** are like passwords - treat them as secrets
- Never commit tokens to repositories
- Never share tokens in public channels
- Revoke tokens when no longer needed
- Use SSH keys instead of tokens for better security

#### Token Management

**Generate New Token:**
```bash
# Go to: https://github.com/settings/tokens
# Generate new token (classic)
# Permissions: repo
# Copy token (only shown once!)
```

**Revoke Old Token:**
```bash
# Go to: https://github.com/settings/tokens
# Find old token and click "Delete"
```

---

## Priority Setup

### 1. Brave Search API ⭐⭐⭐
- **Setup time:** 5 minutes
- **Benefit:** Stock news, real-time data, general search
- **Command:**
  ```bash
  openclaw configure --section web
  ```

---

### 2. yfinance ⭐⭐⭐
- **Setup time:** 2 minutes
- **Benefit:** Real-time IHSG & Indonesian stock data
- **Command:**
  ```bash
  pip install yfinance
  ```

---

### 3. espeak-ng ⭐⭐
- **Setup time:** 1 minute
- **Benefit:** Basic TTS for voice output
- **Command:**
  ```bash
  sudo apt install espeak-ng
  ```

---

### 4. Node Pairing ⭐⭐
- **Setup time:** 5 minutes
- **Benefit:** Control camera/screen on other devices
- **Command:**
  ```bash
  # On target device
  npm install -g @openclaw/node
  openclaw-node pair
  
  # On main device
  openclaw nodes approve <id>
  ```

---

### 5. Stable Diffusion ⭐
- **Setup time:** 10-15 minutes
- **Benefit:** High-quality image generation
- **Optional:** Only if frequently needed

---

## Workflow Integration

1. Install tools on system
2. Create helper scripts in `~/.openclaw/workspace/tools/`
3. Call from OpenClaw via `exec` tool or directly in chat

**Example:**
- Run: `python3 ~/.openclaw/workspace/tools/ihsg_data.py "^JKSE"`
- Result appears in this chat

---

## Helper Scripts Structure

Create directory:
```bash
mkdir -p ~/.openclaw/workspace/tools
cd ~/.openclaw/workspace/tools
```

Recommended scripts:
- `ddg_search.py` - DuckDuckGo search
- `ihsg_data.py` - IHSG & stock data
- `fetch.py` - Web fetch with Playwright
- `tts.py` - Text-to-speech
- `ocr.py` - Text recognition
- `image_gen.py` - Image generation

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

---

## Notes

- All options above are **opensource** and **free**
- Can be integrated into OpenClaw workflow
- Use for stock analysis, automation, and more
- Helper scripts make repeated tasks easier

---

## Summary Command List

```bash
# Core setup
asdf install python latest && asdf global python latest
asdf install nodejs lts && asdf global nodejs lts

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

# Daily backup
cd ~/.openclaw/workspace/private-data && git add . && git commit -m "Daily backup" && git push
cd ~/.openclaw/workspace && git add . && git commit -m "Daily backup" && git push
```

---

## Quick Start

```bash
# 1. Core setup (run once)
asdf install python latest nodejs lts
asdf global python latest nodejs lts

# 2. Install essential packages
pip install yfinance duckduckgo-search playwright
sudo apt install espeak-ng tesseract-ocr

# 3. Configure web search
openclaw configure --section web

# 4. Create tools directory
mkdir -p ~/.openclaw/workspace/tools
cd ~/.openclaw/workspace/tools

# 5. Copy helper scripts (from this README)
```

---

## Support

If you need help with setup, ask Nara (OpenClaw assistant) and specify which section you need help with.

---

**Last Updated:** 2026-02-11
**Version:** 1.1
**Platform:** Orange Pi 5 (ARM64)
**OS:** Ubuntu-based Linux
