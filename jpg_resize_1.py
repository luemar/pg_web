from PIL import Image, ImageOps
import os

print("===RESIZE SCRIPT RUNNING===")

SRC = "/mnt/pg_web_data/slide_show_original"
DST = "/mnt/pg_web_data/slide_show"

os.makedirs(DST, exist_ok=True)

for f in os.listdir(SRC):
    if f.lower().endswith(".jpg"):
        src = os.path.join(SRC, f)
        dst = os.path.join(DST, f)

        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            img.thumbnail((1600, 1600))
            img.save(
                dst,
                "JPEG",
                quality=85,
                optimize=True,
                progressive=False
            )

        print("Resized:", f)
