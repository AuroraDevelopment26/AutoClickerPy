import os
import struct
from PIL import Image

img = Image.open(os.path.join(os.path.dirname(__file__), "icon.png"))
img = img.resize((32, 32))

# pillow can save ICO, just need the right format
img.save(os.path.join(os.path.dirname(__file__), "icon.ico"), format="ICO", sizes=[(32, 32)])
print("icon.ico erstellt")
