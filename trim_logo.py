from PIL import Image, ImageChops
import os

base = "/Users/3947/Documents/dog/System/Proposal materials/mochizuki-rc/mochizuki-rc/picture"
img = Image.open(os.path.join(base, "望月リソルロゴ.jpg"))
print(f"Original size: {img.size}")

img_rgba = img.convert("RGBA")
bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
diff = ImageChops.difference(img_rgba, bg)
gray = diff.convert("L")
bbox = gray.point(lambda x: 255 if x > 20 else 0).getbbox()
print(f"Bounding box: {bbox}")

if bbox:
    padding = 20
    x1 = max(0, bbox[0] - padding)
    y1 = max(0, bbox[1] - padding)
    x2 = min(img.size[0], bbox[2] + padding)
    y2 = min(img.size[1], bbox[3] + padding)
    cropped = img_rgba.crop((x1, y1, x2, y2))
    print(f"Cropped size: {cropped.size}")

    data = cropped.getdata()
    new_data = []
    for item in data:
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    cropped.putdata(new_data)

    out = os.path.join(base, "logo.png")
    cropped.save(out, "PNG", optimize=True)
    print(f"Saved: {out}")
    final = Image.open(out)
    print(f"Final size: {final.size}")
