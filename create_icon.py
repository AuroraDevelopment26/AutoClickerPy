import os
from PIL import Image, ImageDraw

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# circle
draw.ellipse([2, 2, 62, 62], fill="#e53935")

# mouse cursor
draw.polygon([(20, 18), (44, 18), (32, 44)], fill="white")
draw.ellipse([28, 12, 36, 20], fill="white")

path = os.path.join(os.path.dirname(__file__), "icon.png")
img.save(path)
print(f"icon.png erstellt: {path}")
