"""生成 PC exe 图标 (ico) 和 APK 启动图标 (mipmap PNG)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")

BLUE = (37, 99, 235, 255)


def draw_shield(size: int) -> Image.Image:
    S = 4
    w = size * S
    img = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, w - 1], radius=int(w * 0.22), fill=BLUE)
    cx = w / 2
    top, bottom, half = w * 0.16, w * 0.85, w * 0.26
    pts = [(cx - half, top), (cx + half, top), (cx + half, w * 0.45), (cx, bottom), (cx - half, w * 0.45)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    lw = max(int(w * 0.055), S)
    d.line(
        [(cx - half * 0.45, w * 0.50), (cx - half * 0.08, w * 0.63), (cx + half * 0.55, w * 0.36)],
        fill=BLUE,
        width=lw,
        joint="curve",
    )
    return img.resize((size, size), Image.LANCZOS)


def main():
    root = Path(__file__).resolve().parents[1]

    # ico（PC exe）
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    icons_dir = root / "desktop"
    icons_dir.mkdir(exist_ok=True)
    draw_shield(256).save(
        icons_dir / "icon.ico", format="ICO", sizes=[(s, s) for s in ico_sizes]
    )
    print(f"OK {icons_dir / 'icon.ico'}")

    # mipmap PNG（APK）
    apk_res = root / "apk" / "res"
    mipmap = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    for folder, size in mipmap.items():
        p = apk_res / folder
        p.mkdir(parents=True, exist_ok=True)
        draw_shield(size).save(p / "ic_launcher.png")
        print(f"OK {p / 'ic_launcher.png'}")


if __name__ == "__main__":
    main()
