r"""Find openly licensed artwork and photographs on Wikimedia Commons, download them and cut device-sized wallpapers.

    F:\Quantix_Master_Vault\simba_desktop_companion\.venv\Scripts\python.exe fetch_art.py search   list candidates + contact sheet
    F:\Quantix_Master_Vault\simba_desktop_companion\.venv\Scripts\python.exe fetch_art.py build    download picks, write wallpapers

Only public-domain, CC0, CC BY and CC BY-SA files are accepted; artist, licence and source page go to ART_MANIFEST.md.
"""
from __future__ import annotations

import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
ART = HERE / "wallpapers" / "art"
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "QuantixThemeSuite/1.0 (wallpaper set; https://github.com/000MAK/quantix-theme-suite)"}
OK = re.compile(r"^(public domain|pd|cc0|cc by(-sa)? [1-4]\.0|cc-by(-sa)?-[1-4]\.0)", re.I)
SIZES = {"pc": (1920, 1080), "tablet": (1920, 3000), "telefon": (720, 1560)}

QUERIES = {
    "great_wave": "Great Wave off Kanagawa Hokusai",
    "kuniyoshi_cats": "Kuniyoshi cats fifty-three stations",
    "chat_noir": "Tournée du Chat Noir Steinlen",
    "cosmic_cliffs": "Cosmic Cliffs Carina Nebula Webb NIRCam",
    "pillars": "Pillars of Creation Webb NIRCam",
    "mystic_mountain": "Mystic Mountain Hubble",
    "milky_way_paranal": "Milky Way over Paranal ESO",
    "mevlana_dome": "Mevlana Museum green dome Konya",
    "orange_tabby": "orange tabby cat portrait",
}
PICK = {"chat_noir": 1, "orange_tabby": 1}        # index of the chosen candidate when the first is not the best


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def strip(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def candidates(q: str, n: int = 8) -> list[dict]:
    d = api({"action": "query", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6,
             "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 400})
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = strip(m.get("LicenseShortName", {}).get("value", ""))
        if not OK.match(lic) or ii["width"] < 1800:
            continue
        out.append({"title": p["title"], "w": ii["width"], "h": ii["height"], "license": lic,
                    "artist": strip(m.get("Artist", {}).get("value", ""))[:80], "url": ii["url"],
                    "thumb": ii["thumburl"], "page": ii["descriptionurl"]})
    return out


def fetch(url: str) -> Image.Image:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return ImageOps.exif_transpose(Image.open(io.BytesIO(r.read()))).convert("RGB")   # honour camera rotation


def search() -> None:
    picks, thumbs = {}, []
    for key, q in QUERIES.items():
        c = candidates(q)
        print(f"\n## {key}")
        for i, x in enumerate(c[:3]):
            print(f"  [{i}] {x['title']}  {x['w']}x{x['h']}  {x['license']}  {x['artist']}")
        if c:
            picks[key] = c[min(PICK.get(key, 0), len(c) - 1)]
            t = fetch(picks[key]["thumb"])
            t.thumbnail((400, 300))
            thumbs.append(t)
    (HERE / "art_picks.json").write_text(json.dumps(picks, indent=1, ensure_ascii=False), encoding="utf-8")
    sheet = Image.new("RGB", (400 * 5, 300 * ((len(thumbs) + 4) // 5)), (20, 20, 28))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % 5) * 400, (i // 5) * 300))
    sheet.save(HERE / "art_candidates.jpg", quality=85)


def build() -> None:
    picks = json.loads((HERE / "art_picks.json").read_text(encoding="utf-8"))
    ART.mkdir(parents=True, exist_ok=True)
    rows = []
    for key, x in picks.items():
        src = x["url"]
        if max(x["w"], x["h"]) > 4000:                          # let the API hand out a valid 3840 px rendition
            d = api({"action": "query", "titles": x["title"], "prop": "imageinfo", "iiprop": "url",
                     "iiurlwidth": 3840 if x["w"] >= x["h"] else int(3840 * x["w"] / x["h"])})
            src = next(iter(d["query"]["pages"].values()))["imageinfo"][0]["thumburl"]
        img = fetch(src)
        for dev, (w, h) in SIZES.items():
            keep = min(img.width / img.height, w / h) / max(img.width / img.height, w / h)
            if keep < 0.35:                                     # the crop would keep too little of the work
                continue
            size = (w, h)
            ImageOps.fit(img, size, Image.LANCZOS, centering=(0.5, 0.45)).save(ART / f"{key}_{dev}.jpg", quality=92)
        rows.append(f"| `{key}_*.jpg` | {x['title'].removeprefix('File:')} | {x['artist'] or '—'} | {x['license']} | [kaynak]({x['page']}) |")
        print(key, "ok")
    (HERE / "ART_MANIFEST.md").write_text(
        "# Duvar kağıtları: gerçek sanatçı ve fotoğrafçı eserleri\n\nKaynak: Wikimedia Commons. Sadece kamu malı, CC0, CC BY ve CC BY-SA.\n"
        "CC BY / BY-SA eserleri paylaşırken sanatçı adı ve lisans belirtilmeli; kişisel duvar kağıdı kullanımı serbest.\n"
        "Her eser 3 boyutta: `_pc` 1920×1080, `_tablet` 1920×3000, `_telefon` 720×1560.\n\n"
        "| Dosya | Eser | Sanatçı | Lisans | Sayfa |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    {"search": search, "build": build}[sys.argv[1]]()
