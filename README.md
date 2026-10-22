# Telegram Mağaza Botu

Python 3.12+ ve `aiogram` 3.x ile yazılmış, sürekli polling yapan tek örnekli bir Telegram mağaza botu. SQLite üzerinde çalışır.

> **Not:** Bu README, depodaki `main.py` ve `bot_extensions.py` dosyalarının **gerçek içeriğine** göre yazılmıştır. Eski sürümdeki `/addservice`, `/addbalance`, `/promoadd`, `/export` gibi komutlar kodda **yoktur** — admin işlemleri tamamen buton (inline menü) ile yürür.

---

## Proje yapısı

| Dosya | İş |
| --- | --- |
| `main.py` | Çekirdek bot: DB, menü, market, siparişler, oyunlar, banka, VIP, yıldız yükleme, admin paneli, arka plan görevleri, `main()` giriş noktası |
| `bot_extensions.py` | Ek komutlar: `/transfer`, `/ticket`, `/tickets`, `/ticketreply`, `/ticketclose`, `/ban`, `/unban`, `/userinfo`, `/leaderboard`. `main.py` bunu alt yönlendirici olarak yükler |
| `test/test_bot.py` | `unittest` testleri |
| `requirements.txt` | `aiogram>=3.13,<4`, `aiosqlite>=0.20,<1` |
| `railway.json` | Railway başlangıç komutu (`python main.py`) |

Toplam **110 handler** (99 çekirdek + 11 ek).

---

## Ortam değişkenleri

Kodun gerçekten okuduğu değişkenler bunlar — başkası yok:

| Değişken | Gerekli | Varsayılan | Açıklama |
| --- | --- | --- | --- |
| `BOT_TOKEN` | **Evet** | — | BotFather tokeni. Boşsa bot `HATA: BOT_TOKEN eksik!` yazıp çıkar |
| `ADMIN_IDS` | **Evet** | — | Admin Telegram ID'leri, virgülle. Boşsa admin paneli hiç açılmaz |
| `DB_PATH` | Hayır | `bot.db` | SQLite dosya yolu. Kalıcı disk bağladıysan `/data/bot.db` yap |
| `FORCE_JOIN_CHANNEL` | Hayır | — | Zorunlu katılım kanalı: `@kanal` veya `-100...` |
| `JOIN_CHANNEL_URL` | Sayısal kanalda evet | — | Davet linki (`FORCE_JOIN_CHANNEL` `@` ile başlamıyorsa gerekir) |
| `LOG_CHANNEL_ID` | Hayır | — | İşlem loglarının gideceği kanalın `-100...` ID'si |
| `PROMO_CHANNEL_ID` | Hayır | — | Promo/hazine duyurularının gideceği kanal (bot orada yönetici olmalı) |
| `STAR_TOPUP_TIERS` | Hayır | `50:25,100:50,250:125,500:250` | Yıldız paketleri: `Yıldız:TL` biçiminde, virgülle |
| `VIP_PRICE_TL` | Hayır | `500` | VIP bedeli (TL) |
| `VIP_DURATION_DAYS` | Hayır | `30` | VIP süresi (gün) |
| `REFERRAL_BONUS_TL` | Hayır | `5` | Davet ödülü (TL) |

**Kodda olmayan, README'ye eskiden yazılmış değişkenler:** `WELCOME_BONUS_TL`, `BANK_TRANSFER_ENABLED`, `PAYMENT_INSTRUCTIONS`. Bunlar hiçbir yerde okunmuyor — tanımlamanın bir etkisi yok.

---

## Kullanıcı tarafı

`/start` dışında komut yok; her şey aşağıdaki buton menüsünden yürür.

| Buton | İş |
| --- | --- |
| 🛍️ Market | Hizmet → ülke → satın al, favori, sepete ekle |
| 💰 Bakiyem | Bakiye ve yıldız yükleme kısayolu |
| 📦 Siparişlerim | Sipariş listesi ve durumu |
| 🎯 Günlük | Günlük ödül (`500 / 1000 / 2000 / 3500 / 5000 / 7500 / 15000` kuruş, 7 günlük seri) |
| 🎮 Oyunlar | Çark, Slot, Zar, Yazı Tura, Sandık, Düello |
| 🏆 Liderlik | Davet liderlik tablosu (ilk 10) |
| 👤 Profilim / 📊 İstatistikler | Kullanıcı ve oyun özeti |
| ⭐ Yıldız Yükle | Telegram Stars (XTR) ile bakiye yükleme |
| 💎 VIP | VIP satın al (bakiye ile, %20 indirim) |
| 🎯 Görevler / 🏆 Başarımlar | Haftalık görevler ve başarımlar |
| 💼 Banka | Vadeli yatırım: 24 Saat %5, 7 Gün %15, 30 Gün %30 (min 50 TL) |
| 🤝 Transfer | Kullanıcılar arası bakiye transferi (onay ekranlı) |
| 👥 Davet | Referans linki ve kazanç |
| 🎁 Fırsatlar | Aktif promo ve hazineler |
| 🎫 Kod Takip / 📞 Kod Geçmişi | Sipariş kodu takibi |
| 🛒 Sepetim / ⭐ Favoriler | Sepet ve favoriler |
| 📜 İşlem Geçmişi | Bakiye hareketleri |
| 💬 Destek | Destek talebi (min 5 karakter) |
| ℹ️ Yardım | Kısa yardım |
| 🛠️ Admin Paneli | Sadece `ADMIN_IDS` |

Komutlar: `/start` (menü), `/cancel` (akış iptali), `/transfer ID TUTAR`, `/ticket MESAJ`, `/leaderboard`.
Kanal zorunluysa bot "📣 Katıl" / "✅ Kontrol Et" ekranı gösterir.

---

## Admin paneli

`ADMIN_IDS` içindeki hesaplarda menüde "🛠️ Admin Paneli" butonu çıkar:

| Buton | İş |
| --- | --- |
| 📈 Dashboard | Özet sayılar |
| 👥 Kullanıcılar | Tüm kullanıcıların listesi `.txt` olarak |
| ➕ / ➖ Bakiye | Kullanıcıya bakiye ekle / sil |
| 📦 Hizmet Ekle / 🛒 Ürün Ekle | Katalog yönetimi |
| ✨ Özel Hizmet Aç | Kontenjanlı, süreli özel hizmet |
| 🎁 Promo Ekle / 💰 Hazine Dağıt | Promo kodu ve hazine |
| 📋 Promolar / Hazineler / Özel Hizmetler | Aktif kayıtları listele, iptal et |
| 🔄 Kanal Sync | Promo/hazine kanal mesajlarını eşitle |
| ⚙️ Ayarlar | `VIP Sistemi` aç/kapat, `Referans: İlk Sipariş Şartı` aç/kapat |
| 📢 Duyuru | Onaylı toplu mesaj (bloklayanları işaretler) |

**Sipariş akışı:** Yeni sipariş gelince admin'e bildirim düşer. "📱 Numara" → ülke kodu → telefon → "🔑 Kod Gir" → kod girilince sipariş `completed` olur ve numara/kod kullanıcıya gider. "❌ İade" siparişi iptal edip bakiyeyi geri yükler. Ödeme yapılan sipariş **6 dakika** içinde tamamlanmazsa arka plan görevi otomatik iade eder.

**Komutla çalışan admin araçları** (`bot_extensions.py`): `/userinfo ID|@kullanıcı` (davet sayısı, referans kazancı, yüklediği yıldız ve tutar, aldığı numara, VIP durumu, oyun istatistikleri), `/ban`, `/unban`, `/tickets`, `/ticketreply ID YANIT`, `/ticketclose ID`.

---

## Log kanalı

`LOG_CHANNEL_ID` tanımlıysa şu olaylar kanala yazılır: yeni kullanıcı, sipariş verildi, sipariş tamamlandı, iade, yıldız yükleme, promo kullanımı, hazine payı, VIP alımı, transfer, destek talebi, ban. Tanımlı değilse loglar sessizce atlanır.

---

## Yerel çalıştırma

```bash
python -m pip install -r requirements.txt
BOT_TOKEN="..." ADMIN_IDS="123456789" python main.py
```

Testler:

```bash
python -m unittest discover -s test -v
```

---

## Nerede çalıştırılır?

Bot **sürekli açık** kalmalı (Telegram polling tek örnek ister). Uygun seçenekler:

| Ortam | Nasıl | Not |
| --- | --- | --- |
| **Kendi VPS'in** | `screen`/`systemd` ile `python main.py` | En ucuz ve en kontrollü. Kalıcı disk zaten var |
| **Fly.io** | `fly launch` + volume | Volume'ü `/data`'ya bağla, `DB_PATH=/data/bot.db` |
| **Render** | Background Worker | Ücretsiz katmanda disk kalıcı değil; ücretli disk gerekir |
| **Koyeb / Northflank** | Worker servisi | Uzun süren işler için uygun |
| **Oracle Cloud / Google Cloud e2-micro** | Ücretsiz VM + `systemd` | Ücretsiz katman, kalıcı disk |
| **Docker (herhangi bir yerde)** | `python:3.12-slim` imajı + volume | Aşağıdaki Dockerfile hazır |

Aşağıdakiler bot gibi sürekli işler için **uygun değil**: Vercel, Netlify, Cloudflare Workers, AWS Lambda, GitHub Actions — hepsi fonksiyon/istek bazlı çalışır ve kalıcı SQLite diski yoktur.

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Kalıcı veri için `/data` volume'ü bağla ve `DB_PATH=/data/bot.db` ver.

---

## Çalıştırırken dikkat

- **Replica sayısı 1 olmalı.** Aynı token ile iki örnek çalışırsa Telegram polling çakışır (`Conflict`).
- **SQLite kalıcı olmalı.** Volume bağlanmazsa her deploy'da kullanıcı/bakiye/sipariş verisi sıfırlanır.
- **Token'i koda yazma.** Sadece ortam değişkenine koy. Bu depoda token bir sohbette açığa çıkmıştı; BotFather'dan yeni token al ve eskisini iptal et.
- **Zorunlu katılım kontrolü** için bot, kanalda **yönetici** olmalı.
- **Promo/hazine duyurusu** için bot, `PROMO_CHANNEL_ID` kanalında yönetici olmalı.
- **Yıldız yükleme** için bot, BotFather'da ödeme sağlayıcısı olarak Telegram Stars'ı (XTR) kabul etmiş olmalı.
