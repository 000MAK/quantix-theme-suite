# Quantix Theme Suite

A cyberpunk / martial-arts / orange-cat look for an Android phone, a tablet and a Windows PC.

| Folder | What |
|---|---|
| `wallpapers/art/` | Openly licensed artworks and photos (Hokusai, Kuniyoshi, Steinlen, NASA/ESA/JWST, ESO, neon city photos) cut to phone 720×1560, tablet 1920×3000 and PC 1920×1080. Every source, author and licence is in `ART_MANIFEST.md`; CC BY / CC BY-SA files keep those terms. |
| `fetch_art.py` | Re-downloads and re-crops the art from Wikimedia Commons (`art_picks.json`). |
| `fonts/` | Magisk module that swaps Android 11's Roboto for **Exo 2** (SIL OFL 1.1, `fonts/src/OFL.txt`), built by `make_font_module.py`. |
| `audio_branding/` | Ringtone, notification and alarm sounds synthesised from scratch. |
| `AI_PROMPTS.md` | Image-generator prompts for matching wallpapers. |

Code is MIT (`LICENSE`). Art, fonts and their licences are listed above and are **not** covered by MIT.
