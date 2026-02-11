# Cara Mendapatkan BRAVE_API_KEY

## Langkah-Langkah

### Step 1: Buka Halaman Brave Search API

1. Buka browser: https://brave.com/search/api/
2. atau langsung ke: https://api.brave.com/app/keys

---

### Step 2: Sign Up / Sign In

**Jika belum punya akun Brave:**
1. Klik **"Sign up"** atau **"Create account"**
2. Pilih opsi registrasi:
   - Email + password, ATAU
   - Login dengan GitHub, Google, dll (lebih mudah!)
3. Isi form registrasi
4. Verifikasi email (kalau diminta)

**Jika sudah punya akun Brave:**
1. Klik **"Sign in"**
2. Login dengan email/password atau social login

---

### Step 3: Generate API Key

1. Setelah login, Anda akan melihat halaman **"API Keys"**
2. Klik tombol **"Create API Key"** atau **"New Key"**
3. Isi form:
   - **Name:** Nama untuk API key ini (contoh: `OpenClaw-Papa`)
   - **Type:** Pilih `Search` atau `Browser Search API`
   - **Usage:** Personal / Development (pilih yang sesuai)
   - **Limit:** Tidak perlu diubah (default ok)

4. Klik **"Create"** atau **"Generate"**

---

### Step 4: Copy API Key

1. API Key akan ditampilkan setelah generated
2. **COPY** API key tersebut (format: `BSAxxxxx` atau `BSxxxxx`)
3. **PENTING:** API key hanya muncul sekali! Copy sekarang!

---

### Step 5: Masukkan ke OpenClaw

**Option A: Via Terminal**

```bash
# Run command ini
openclaw configure --section web

# Masukkan API key ketika diminta
# Paste: BSAxxxxx atau BSxxxxx
```

**Option B: Via Config File**

```bash
# Edit config OpenClaw
nano ~/.openclaw/config.json

# Tambahkan atau update:
{
  "web": {
    "braveApiKey": "BSAxxxxx-xxxx-xxxx-xxxx-xxxxx"
  }
}
```

**Option C: Via Environment Variable**

```bash
# Set environment variable
export BRAVE_API_KEY="BSAxxxxx-xxxx-xxxx-xxxx-xxxxx"

# Restart OpenClaw gateway
openclaw gateway restart
```

---

## Penggunaan BRAVE_API_KEY

### Search dengan OpenClaw

Setelah API key terinstall, saya bisa search:

```
User: Cari berita BMRI hari ini
Nara: [mencari menggunakan Brave Search API...]
```

---

## Informasi Penting

### API Limits (Gratis)

- **Gratis:** 2,000 requests per bulan
- **Untuk penggunaan personal:** Biasanya cukup
- **Jika limit habis:** Tunggu reset bulan depan atau upgrade ke paid

### Security

- **JANGAN share API key** dengan orang lain
- **Simpan di tempat aman**
- **Jika bocor:** Revoke dan generate baru
- **Gunakan environment variable** (lebih aman daripada hardcode di file)

### Revoke API Key (jika perlu)

1. Kembali ke: https://api.brave.com/app/keys
2. Temukan API key yang ingin dihapus
3. Klik **"Revoke"** atau **"Delete"**
4. Confirm deletion

---

## Troubleshooting

### Error: "Invalid API Key"

**Problem:** API key salah atau kadaluarsa.

**Solution:**
1. Cek kembali API key yang di-copy
2. Generate API key baru
3. Pastikan tidak ada spasi tambahan

### Error: "Rate Limit Exceeded"

**Problem:** Sudah melebihi 2,000 requests bulan ini.

**Solution:**
1. Tunggu bulan depan (reset tanggal 1)
2. Upgrade ke paid plan (kalau butuh banyak requests)
3. Gunakan opsi DuckDuckGo (gratis tanpa API key)

### Error: "API Key Not Recognized"

**Problem:** OpenClaw tidak mengenali config.

**Solution:**
```bash
# Restart OpenClaw gateway
openclaw gateway restart

# Atau reload config
openclaw configure --section web
# Masukkan ulang API key
```

---

## Alternatif: DuckDuckGo (Tanpa API Key)

Jika tidak mau pakai Brave atau butuh backup tanpa API key:

Gunakan DuckDuckGo (Gratis & Tanpa API Key):
```bash
# Install package
pip install duckduckgo-search

# Search
python3 ~/.openclaw/workspace/tools/ddg_search.py "BMRI hari ini"
```

DuckDuckGo juga ada di README.md section "Web Search".

---

## Summary

1. Buka: https://brave.com/search/api/ atau https://api.brave.com/app/keys
2. Sign up / Sign in (pakai GitHub/Google untuk mudah)
3. Click "Create API Key"
4. Name: `OpenClaw-Papa` (atau nama lain)
5. Copy API key (hanya muncul sekali!)
6. Masukkan ke OpenClaw: `openclaw configure --section web`
7. Paste API key

**Alternatif:** Gunakan DuckDuckGo (gratis tanpa API key)

---

**Last Updated:** 2026-02-11
