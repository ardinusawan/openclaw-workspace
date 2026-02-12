# OpenClaw Tools

Helper scripts untuk OpenClaw menggunakan API key yang tersimpan di `~/.openclaw/.env`.

## Setup

### 1. API Key File
API key tersimpan di `~/.openclaw/.env` (tidak di-commit ke git).

Format `.env`:
```
# Weather API Keys
WEATHERBIT_API_KEY=eaaebe9b89c54d2aabf6525da9861672

# Web Search API Keys
BRAVE_API_KEY=your_brave_search_api_key_here
```

### 2. .gitignore
File `.env` sudah ditambahkan ke `.gitignore` untuk keamanan.

---

## Tools

### Weatherbit.py - Cuaca

Gunakan untuk mendapatkan data cuaca dari Weatherbit.io.

**Usage:**
```bash
python3 ~/.openclaw/workspace/tools/weatherbit.py <lat> <lon> [--units C|F]
```

**Examples:**
```bash
# Cawang, Jakarta
python3 ~/.openclaw/workspace/tools/weatherbit.py -6.25 106.875

# Gianyar, Bali (Fahrenheit)
python3 ~/.openclaw/workspace/tools/weatherbit.py -8.5 115.3 --units F
```

**Output:**
```
Weather for Jakarta, ID
Temperature: 26°C
Feels Like: 28°C
Condition: Cloudy
Humidity: 81%
Wind: 7.4 km/h from West
Pressure: 1012 hPa
UV Index: 5
Last Updated: 2026-02-12T14:00
```

---

### Brave Search - Web Search

Gunakan untuk web search menggunakan Brave Search API.

**Setup dulu:**
1. Buka https://brave.com/search/api/
2. Sign up (gratis)
3. Copy API key
4. Tambah ke `.env`: `BRAVE_API_KEY=your_key_here`

**Usage:**
```bash
python3 ~/.openclaw/workspace/tools/brave_search.py <query> [--results N]
```

**Examples:**
```bash
# Search simple
python3 ~/.openclaw/workspace/tools/brave_search.py "IHSG hari ini"

# Search dengan 10 results
python3 ~/.openclaw/workspace/tools/brave_search.py "crypto news" --results 10
```

**Output:**
```
Search results for: IHSG hari ini

1. IHSG Menguat di Sesi Pertama
   https://example.com/ihsg-hari-ini
   IHSG menguat 0.5% di sesi pertama perdagangan...

2. Rekomendasi Saham Hari Ini
   https://example.com/saham-rekomendasi
   Berikut rekomendasi saham untuk trading hari ini...

Total: 2 results
```

---

### Run with Environment

Gunakan script ini untuk menjalankan command dengan environment variables yang sudah diload.

**Usage:**
```bash
~/.openclaw/workspace/tools/run_with_env.sh <command>
```

**Examples:**
```bash
# Jalankan python script dengan env vars
~/.openclaw/workspace/tools/run_with_env.sh python3 myscript.py

# Jalankan curl dengan env vars
~/.openclaw/workspace/tools/run_with_env.sh curl -H "Authorization: $API_KEY" https://api.example.com
```

---

## Penggunaan dari OpenClaw

Dari chat dengan OpenClaw, panggil script menggunakan `exec`:

**Cuaca:**
```
python3 ~/.openclaw/workspace/tools/weatherbit.py -6.25 106.875
```

**Web Search:**
```
python3 ~/.openclaw/workspace/tools/brave_search.py "IHSG hari ini"
```

---

## Security Notes

- ✅ API key disimpan di `~/.openclaw/.env` (tidak di-commit)
- ✅ `.env` sudah di `.gitignore`
- ✅ Tools membaca API key dari `.env`
- ❌ Jangan pernah commit `.env` ke repository

---

## Troubleshooting

### "Error: WEATHERBIT_API_KEY not set"
- Pastikan API key sudah ditambahkan ke `~/.openclaw/.env`
- Format harus: `WEATHERBIT_API_KEY=your_key_here`

### "API Error: API key not valid"
- API key Weatherbit butuh **30 menit** untuk aktif setelah dibuat
- Tunggu 30 menit lalu coba lagi

### "Error: .env file not found"
- Pastikan file `~/.openclaw/.env` sudah dibuat
- File harus berisi API key yang valid

---

## Next Steps

1. Setup Brave Search API key (opsional tapi recommended untuk web search)
2. Test tools dari command line
3. Panggil dari OpenClaw via `exec` atau chat
