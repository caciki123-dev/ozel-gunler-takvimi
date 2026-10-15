# Özel Günler Takvimi

Türkiye'den ve dünyadan özel günleri içeren, abone olunabilir bir takvim.
Her özel günden bir gün önce saat 09:00'da hatırlatma verir. O sabah,
haftanın gündemine göre hazırlanan içerik planı (post, reels, hikâye)
etkinliğin notlarına eklenir.

## Abone olma (iPhone)

Takvim adresi:

```
https://raw.githubusercontent.com/caciki123-dev/ozel-gunler-takvimi/main/ozel-gunler.ics
```

1. **Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer → Abone Olunan Takvim Ekle** yolunu izle.
2. Yukarıdaki adresi yapıştır, **İleri**'ye dokun.
3. **Uyarıları Kaldır** seçeneğini **kapat**, sonra **Kaydet**'e dokun.
4. **Ayarlar → Takvim → Hesaplar → Yeni Verileri Al** bölümünde sıklığı
   **Her 15 dakikada bir** ya da **Saatte bir** yap.

## Yapı

| Dosya | Ne işe yarar |
|---|---|
| `gunler.json` | Özel günler: `sabit` (her yıl aynı gün), `kural` (ör. Mayıs'ın 2. pazarı), `tek_seferlik` (dini günler, MEB takvimi gibi yıla göre değişen tarihler) |
| `notlar/YYYY-MM-DD.md` | O günün gündem ve içerik planı |
| `uret.py` | `gunler.json` ve `notlar/` klasöründen `ozel-gunler.ics` dosyasını üretir (`python3 uret.py`) |
| `ozel-gunler.ics` | Abone olunan takvim dosyası (otomatik üretilir) |
