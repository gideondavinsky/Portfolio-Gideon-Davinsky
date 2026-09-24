"""
Builds branded Open Graph share-card images (1200x630 PNG) for every page,
so links pasted into LinkedIn/Slack render as a card instead of a bare URL.

Uses the site's actual brand colors (css/main.css --bg / --accent) and system
fonts (Segoe UI / Calibri) as a stand-in for the site's web fonts (Inter /
Space Grotesk), since no web-font files are bundled in the repo.

Requires: Pillow (`pip install pillow`)
"""
import os

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "og")
W, H = 1200, 630

BG = (15, 20, 18)          # --bg dark
ACCENT = (15, 118, 110)    # --accent light-theme teal (#0f766e)
ACCENT_LIGHT = (45, 212, 191)  # --accent dark-theme teal (#2dd4bf)
WHITE = (255, 255, 255)
MUTED = (170, 182, 178)

FONTS_DIR = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)


F_BOLD = "segoeuib.ttf" if os.path.exists(os.path.join(FONTS_DIR, "segoeuib.ttf")) else "arialbd.ttf"
F_REG = "segoeui.ttf" if os.path.exists(os.path.join(FONTS_DIR, "segoeui.ttf")) else "arial.ttf"


def draw_mark(draw, cx, cy, scale):
    # Simplified version of the site's pin/leaf brand mark.
    r = 16 * scale
    draw.ellipse([cx - r, cy - r * 1.6, cx + r, cy + r * 0.6], fill=ACCENT_LIGHT)
    draw.ellipse([cx - r * 0.45, cy - r * 0.85, cx + r * 0.45, cy - r * 0.05], fill=BG)


def wrap(text, f, max_width, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build(filename, eyebrow, title, subtitle):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Subtle accent panel on the left edge
    d.rectangle([0, 0, 14, H], fill=ACCENT_LIGHT)

    margin = 80
    draw_mark(d, margin + 18, 118, 1.15)

    f_name = font(F_BOLD, 30)
    d.text((margin + 50, 96), "Gideon Davinsky", font=f_name, fill=WHITE)
    f_eyebrow = font(F_REG, 22)
    d.text((margin + 50, 136), eyebrow, font=f_eyebrow, fill=ACCENT_LIGHT)

    f_title = font(F_BOLD, 54)
    lines = wrap(title, f_title, W - margin * 2, d)[:3]
    y = 260
    for line in lines:
        d.text((margin, y), line, font=f_title, fill=WHITE)
        y += 64

    if subtitle:
        f_sub = font(F_REG, 26)
        sub_lines = wrap(subtitle, f_sub, W - margin * 2, d)[:2]
        y += 14
        for line in sub_lines:
            d.text((margin, y), line, font=f_sub, fill=MUTED)
            y += 36

    d.text((margin, H - 56), "GIS & Urban Data Analyst · Madrid", font=font(F_REG, 22), fill=ACCENT_LIGHT)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path, "PNG", optimize=True)
    print(f"wrote {out_path}  ({os.path.getsize(out_path)/1024:.0f} KB)")


PAGES = [
    ("home.png", "GIS Portfolio", "Mapping the questions that don't fit on a single layer.",
     "Urban mobility, accessibility, and environmental analysis for public administrations."),
    ("about.png", "About & CV", "About Gideon Davinsky",
     "Background, education, and experience — GIS and urban data analyst based in Madrid."),
    ("projects.png", "Projects", "Academic & professional GIS case studies",
     "Spatial analysis, remote sensing, and hand-built interactive web maps."),
    ("e2sfca.png", "Academic · Atlanta", "Multimodal Healthcare Accessibility",
     "An E2SFCA model scoring 600 census tracts by drive, transit, and walk access."),
    ("contact.png", "Get in touch", "Contact Gideon Davinsky",
     "GIS & urban data analyst based in Madrid — open to GIS, mobility, and smart-cities roles."),
    ("resilencia.png", "Academic · Logroño", "Fluvial Flood Risk & Resilience",
     "A T500 hazard-to-risk pipeline: severity, exposure, vulnerability, and a composite risk map."),
]


def main():
    for filename, eyebrow, title, subtitle in PAGES:
        build(filename, eyebrow, title, subtitle)


if __name__ == "__main__":
    main()
