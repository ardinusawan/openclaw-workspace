# Alternative Free Search Options

Selain Brave Search API (2,000 requests/bulan gratis), ada beberapa alternatif gratis yang bisa digunakan:

---

## 1. Chrome/Chromium Headless (Scraping)

### Cara Kerja
Jalankan browser Chrome/Chromium dalam mode headless (tanpa GUI) untuk mengakses website dan mengekstrak data.

### Prerequisites
```bash
# Install Chromium
sudo apt install chromium-browser

# Atau gunakan Playwright (lebih mudah)
pip install playwright
playwright install chromium
```

### Script Helper: Chrome Headless

Buat `~/.openclaw/workspace/tools/chrome_search.py`:
```python
from playwright.sync_api import sync_playwright
import sys

def chrome_search(query):
    """
    Search menggunakan Chrome headless
    Ini adalah scraping, bukan API resmi
    """
    url = f"https://www.google.com/search?q={query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate ke Google
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Ekstrak hasil search
        results = []
        elements = page.query_selector_all('div.g')

        for element in elements[:10]:  # Ambil 10 hasil pertama
            try:
                title = element.query_selector('h3').inner_text()
                link = element.query_selector('a').get_attribute('href')
                snippet = element.query_selector('div[style*="line-height"]')

                if title and link:
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet.inner_text() if snippet else ''
                    })
            except:
                continue

        browser.close()

        return results

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    results = chrome_search(query)

    print(f"Hasil Search: {query}")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        if r['snippet']:
            print(f"   {r['snippet'][:100]}")
        print()

# Note: Ini scraping, mungkin melanggar Terms of Service Google
```

### Kelebihan
- Gratis
- Tidak perlu API key
- Bisa akses data real-time dari berbagai website

### Kekurangan
- Melanggar Terms of Service (ToS) sebagian besar
- IP bisa diblokir jika terlalu banyak request
- Tidak stabil, structure HTML bisa berubah kapan saja
- Lambat daripada API
- Perlu maintenance jika website berubah struktur HTML

### Penggunaan
```bash
python3 ~/.openclaw/workspace/tools/chrome_search.py "BMRI hari ini"
```

---

## 2. DuckDuckGo (Already in README)

Gratis, tanpa API key. Lihat section "Web Search" di README.md.

---

## 3. SerpAPI (Free Tier)

### Overview
API wrapper untuk berbagai search engines (Google, Bing, dll).
Free tier: 100 requests/hari.

### Setup
```bash
# Install
pip install google-search-results
```

### Script Helper: SerpAPI

Buat `~/.openclaw/workspace/tools/serp_search.py`:
```python
from serpapi import GoogleSearch
import os
import sys

def serpapi_search(query):
    """
    Search menggunakan SerpAPI (Google)
    Free tier: 100 requests/hari
    """
    api_key = os.environ.get("SERPAPI_KEY")

    if not api_key:
        print("ERROR: SERPAPI_KEY environment variable tidak diset")
        return None

    search = GoogleSearch({
        "q": query,
        "api_key": api_key,
    })

    results = search.get_dict()

    organic_results = results.get("organic_results", [])

    formatted = []
    for r in organic_results[:10]:
        formatted.append({
            'title': r.get('title'),
            'url': r.get('link'),
            'snippet': r.get('snippet')
        })

    return formatted

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    results = serpapi_search(query)

    if results:
        print(f"Hasil Search: {query}")
        print("=" * 60)
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            if r['snippet']:
                print(f"   {r['snippet'][:100]}")
            print()
    else:
        print("No results found")
```

### Get API Key
1. Go to: https://serpapi.com/
2. Sign up (free)
3. Get API key
4. Set environment variable:
```bash
export SERPAPI_KEY="your-api-key-here"
```

### Limits
- Free: 100 requests/hari
- Paid: Mulai dari $50/bulan

---

## 4. Bing Web Search API (Microsoft)

### Overview
Microsoft Bing search API.
Free tier: 1,000 requests/bulan.

### Setup
```bash
# Install
pip install azure-cognitiveservices-search-websearch
```

### Get API Key
1. Go to: https://portal.azure.com/
2. Create "Bing Search v7" resource
3. Get API key

### Limits
- Free: 1,000 requests/bulan
- Paid: Mulai dari $7/bulan

---

## 5. Wolfram Alpha (Free Tier)

### Overview
Computational knowledge engine, bisa menjawab pertanyaan kompleks.
Free tier: 2,000 requests/bulan.

### Setup
```bash
# Install
pip install wolframalpha
```

### Script Helper: Wolfram Alpha

Buat `~/.openclaw/workspace/tools/wolfram_search.py`:
```python
import wolframalpha
import os
import sys

def wolfram_search(query):
    """
    Search menggunakan Wolfram Alpha
    Free tier: 2,000 requests/bulan
    Good for: Math, science, facts
    """
    app_id = os.environ.get("WOLFRAM_APP_ID")

    if not app_id:
        print("ERROR: WOLFRAM_APP_ID tidak diset")
        return None

    client = wolframalpha.Client(app_id)
    res = client.query(query)

    return res

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    result = wolfram_search(query)

    if result:
        print(f"Query: {query}")
        print("=" * 60)
        print(result)
        print("=" * 60)
    else:
        print("No results found")
```

### Get App ID
1. Go to: https://developer.wolframalpha.com/
2. Sign up (free)
3. Get App ID
4. Set environment variable:
```bash
export WOLFRAM_APP_ID="your-app-id-here"
```

### Limits
- Free: 2,000 requests/bulan
- Paid: Mulai dari $2/bulan

---

## 6. Google Custom Search API (Free Tier)

### Overview
Google Custom Search JSON API.
Free tier: 100 requests/hari.

### Setup
```bash
# Install
pip install google-api-python-client
```

### Get API Key
1. Go to: https://console.cloud.google.com/
2. Create "Custom Search API" credential
3. Get API key

### Limits
- Free: 100 requests/hari
- Paid: Mulai dari $5 per 1,000 queries

---

## Comparison Summary

| Service | Free Tier | Best For | Setup Complexity |
|---------|-----------|-----------|------------------|
| Brave Search API | 2,000/bulan | General search | Low |
| DuckDuckGo | Unlimited | Privacy, general | Low |
| Chrome Headless | Unlimited (risky) | Scraping | High |
| SerpAPI | 100/hari | Multiple engines | Medium |
| Bing Search | 1,000/bulan | General | Medium |
| Wolfram Alpha | 2,000/bulan | Math, science, facts | Medium |
| Google Custom Search | 100/hari | General | High |

---

## Recommendation

### Untuk Penggunaan Personal

**Pilihan Terbaik:**
1. **Brave Search API** (2,000/bulan) - Sudah setup di README.md
2. **DuckDuckGo** (unlimited) - Sudah setup di README.md

Keduanya:
- Gratis
- Mudah setup
- Tidak melanggar ToS
- Stabil
- Cepat

### Untuk Web Scraping (Hati-hati!)

**Chrome Headless:**
- ⚠️ Melanggar ToS sebagian besar
- ⚠️ IP bisa diblokir
- ⚠️ Tidak stabil
- ⚠️ Perlu maintenance

Gunakan HANYA jika:
- Data tidak tersedia di API
- Situs tidak melarang scraping di robots.txt
- Volume request rendah (bukan untuk production)

---

## Setup OpenClaw dengan Alternatif

### Opsi A: Brave (Default, Recommended)
```bash
openclaw configure --section web
# Enter BRAVE_API_KEY
```

### Opsi B: DuckDuckGo (No API Key)
```bash
# Tidak perlu setup
# Langsung pakai:
python3 ~/.openclaw/workspace/tools/ddg_search.py "query"
```

### Opsi C: SerpAPI (Free 100/hari)
```bash
# Set environment variable
export SERPAPI_KEY="your-key"

# Jalankan script
python3 ~/.openclaw/workspace/tools/serp_search.py "query"
```

### Opsi D: Chrome Headless (Scraping - Hati-hati!)
```bash
# Install dependencies
pip install playwright
playwright install chromium

# Jalankan script
python3 ~/.openclaw/workspace/tools/chrome_search.py "query"
```

---

## Notes

- **Scraping** (Chrome headless) melanggar Terms of Service sebagian besar
- Gunakan dengan bijak dan untuk penggunaan personal saja
- Untuk production, gunakan API resmi (Brave, SerpAPI, dll)
- Beberapa API (Google Custom Search) butuh credit card untuk daftar (meskipun free tier)

---

**Last Updated:** 2026-02-11
**Recommendation:** Gunakan Brave API atau DuckDuckGo (paling stabil & legal)
