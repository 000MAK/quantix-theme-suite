r"""Magisk module that replaces Android 11's Roboto (sans-serif) with Exo 2 (OFL, github.com/google/fonts ofl/exo2).

Android 11 maps each weight to a static Roboto-<Weight>.ttf in /system/fonts, so the Exo 2 variable font is cut
into static instances under those exact file names.

    set UV_CACHE_DIR=F:\MAK_System_Cache\uv
    uv run --with fonttools python make_font_module.py

Output: Quantix_Font_Exo2_Magisk.zip. Undo: Magisk -> Modules -> remove; if the phone ever shows broken text at
boot, hold Volume Down while it starts (Magisk safe mode disables all modules).
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
WEIGHTS = {"Thin": 100, "Light": 300, "Regular": 400, "Medium": 500, "Bold": 700, "Black": 900}
TURKISH = "ÇçĞğİıÖöŞşÜü"


def instance(src: Path, wght: int) -> bytes:
    font = instantiateVariableFont(TTFont(src), {"wght": wght}, updateFontNames=False)
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def main() -> None:
    upright, italic = HERE / "src" / "Exo2-VF.ttf", HERE / "src" / "Exo2-Italic-VF.ttf"
    cmap = TTFont(upright).getBestCmap()
    missing = [c for c in TURKISH if ord(c) not in cmap]
    assert not missing, f"Exo 2 lacks {missing}"
    files: dict[str, bytes] = {}
    for name, w in WEIGHTS.items():
        files[f"Roboto-{name}.ttf"] = instance(upright, w)
        files[f"Roboto-{'Italic' if name == 'Regular' else name + 'Italic'}.ttf"] = instance(italic, w)
    with zipfile.ZipFile(HERE / "Quantix_Font_Exo2_Magisk.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("module.prop", "id=quantix_font_exo2\nname=Quantix Font: Exo 2\nversion=v1\nversionCode=1\n"
                   "author=Quantix\ndescription=System sans-serif (Roboto) replaced with Exo 2 (SIL OFL 1.1, Natanael Gama).\n")
        z.writestr("META-INF/com/google/android/update-binary",
                   "#!/sbin/sh\numask 022\nOUTFD=$2\nZIPFILE=$3\n. /data/adb/magisk/util_functions.sh\ninstall_module\nexit 0\n")
        z.writestr("META-INF/com/google/android/updater-script", "#MAGISK\n")
        z.writestr("OFL.txt", (HERE / "src" / "OFL.txt").read_bytes())
        for name, data in files.items():
            z.writestr(f"system/fonts/{name}", data)
    print("turkish ok,", len(files), "fonts:", ", ".join(sorted(files)))


if __name__ == "__main__":
    main()
