"""gunler.json + notlar/ klasöründen ozel-gunler.ics üretir.

Bugünden 60 gün öncesi ile 400 gün sonrası arasındaki her özel gün tek tek
etkinlik olarak yazılır; notlar/YYYY-MM-DD.md varsa o günün etkinliklerinin
açıklamasına eklenir. Her etkinlikte bir gün önce 09:00 hatırlatması vardır.

Kullanım:
  python3 uret.py                    ozel-gunler.ics dosyasını üretir
  python3 uret.py --gun 2026-10-29   o gün başlayan özel günleri listeler
"""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

KOK = Path(__file__).resolve().parent
DEPO_URL = "https://github.com/caciki123-dev/ozel-gunler-takvimi/blob/main/notlar/"
HAFTAGUNU = {"pazartesi": 0, "salı": 1, "çarşamba": 2, "perşembe": 3,
             "cuma": 4, "cumartesi": 5, "pazar": 6}
NOT_YOK = ("Gündem ve içerik planı, bir gün önce sabah "
           "bu notlara eklenecek.")


def kacinci_haftagunu(yil, ay, kacinci, haftagunu):
    ilk = dt.date(yil, ay, 1)
    fark = (HAFTAGUNU[haftagunu] - ilk.weekday()) % 7
    return ilk + dt.timedelta(days=fark + 7 * (kacinci - 1))


def gunleri_topla(veri, bas, son):
    """(başlangıç, bitiş_dahil, ad, etiket, kaynak) listesi döner."""
    out = []
    for yil in range(bas.year, son.year + 1):
        for g in veri["sabit"]:
            ay, gun = map(int, g["tarih"].split("-"))
            d = dt.date(yil, ay, gun)
            b = d
            if "bitis" in g:
                b = dt.date(yil, *map(int, g["bitis"].split("-")))
            out.append((d, b, g["ad"], g.get("etiket", ""), ""))
        for g in veri["kural"]:
            d = kacinci_haftagunu(yil, g["ay"], g["kacinci"], g["haftagunu"])
            out.append((d, d, g["ad"], g.get("etiket", ""), ""))
    for g in veri["tek_seferlik"]:
        d = dt.date.fromisoformat(g["tarih"])
        b = dt.date.fromisoformat(g["bitis"]) if "bitis" in g else d
        out.append((d, b, g["ad"], g.get("etiket", ""), g.get("kaynak", "")))
    return sorted((e for e in out if bas <= e[0] <= son),
                  key=lambda e: (e[0], e[2]))


def kacis(metin):
    return (metin.replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\r\n", "\n").replace("\n", "\\n"))


def katla(satir):
    """RFC 5545: satırları 75 oktette katla, UTF-8 karakterini bölmeden."""
    parcalar, cur = [], b""
    for ch in satir:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > 75:
            parcalar.append(cur)
            cur = b" "
        cur += b
    parcalar.append(cur)
    return b"\r\n".join(parcalar)


def etkinlik(bas, bitis, ad, etiket, kaynak, not_metni, damga):
    baslik = f"{ad} [{etiket}]" if etiket else ad
    aciklama = not_metni or NOT_YOK
    if kaynak:
        aciklama += f"\n\nTarih kaynağı: {kaynak}"
    uid = hashlib.sha1(f"{ad}|{bas}".encode()).hexdigest()[:16]
    satirlar = [
        "BEGIN:VEVENT",
        f"UID:{uid}@ozel-gunler-takvimi",
        f"DTSTAMP:{damga}",
        f"DTSTART;VALUE=DATE:{bas:%Y%m%d}",
        f"DTEND;VALUE=DATE:{bitis + dt.timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{kacis(baslik)}",
        f"DESCRIPTION:{kacis(aciklama)}",
        "TRANSP:TRANSPARENT",
    ]
    if not_metni:
        satirlar.append(f"URL:{DEPO_URL}{bas:%Y-%m-%d}.md")
    satirlar += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        # Tüm gün etkinliği 00:00'da başlar; -15 saat = önceki gün 09:00
        "TRIGGER:-PT15H",
        "DESCRIPTION:" + kacis(f"Yarın: {baslik} — gündem ve içerik "
                               "planı etkinlik notlarında"),
        "END:VALARM",
        "END:VEVENT",
    ]
    return satirlar


def gunu_listele(veri, tarih):
    for _, bitis, ad, etiket, _ in gunleri_topla(veri, tarih, tarih):
        sure = f" (→ {bitis:%d.%m})" if bitis != tarih else ""
        print(f"{ad}{f' [{etiket}]' if etiket else ''}{sure}")


def main():
    veri = json.loads((KOK / "gunler.json").read_text(encoding="utf-8"))
    if sys.argv[1:2] == ["--gun"]:
        gunu_listele(veri, dt.date.fromisoformat(sys.argv[2]))
        return
    bugun = dt.datetime.now(ZoneInfo("Europe/Istanbul")).date()
    bas, son = bugun - dt.timedelta(days=60), bugun + dt.timedelta(days=400)
    damga = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    satirlar = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ozel-gunler-takvimi//TR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Özel Günler",
        "X-WR-CALDESC:Türkiye ve dünyadan özel günler; bir gün önce "
        "gündem ve içerik planı",
        "X-WR-TIMEZONE:Europe/Istanbul",
        "X-APPLE-CALENDAR-COLOR:#E4572E",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]
    gunler = gunleri_topla(veri, bas, son)
    for bas_t, bitis, ad, etiket, kaynak in gunler:
        dosya = KOK / "notlar" / f"{bas_t:%Y-%m-%d}.md"
        not_metni = dosya.read_text(encoding="utf-8").strip() if dosya.exists() else ""
        satirlar += etkinlik(bas_t, bitis, ad, etiket, kaynak, not_metni, damga)
    satirlar.append("END:VCALENDAR")
    (KOK / "ozel-gunler.ics").write_bytes(
        b"\r\n".join(katla(s) for s in satirlar) + b"\r\n")
    print(f"{len(gunler)} etkinlik yazıldı ({bas} – {son})")


if __name__ == "__main__":
    main()
