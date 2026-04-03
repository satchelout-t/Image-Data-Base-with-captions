import json
import random
import os
from PIL import Image
import matplotlib.pyplot as plt

IMAGE_DIR = "images_hq"

with open("dataset_with_captions.json", "r") as f:
    data = json.load(f)

samples = random.sample(data, 9)

fig, axes = plt.subplots(3, 3, figsize=(12, 10))

for idx, ax in enumerate(axes.flat):
    item = samples[idx]
    path = os.path.join(IMAGE_DIR, item["filename"])

    if os.path.exists(path):
        img = Image.open(path).convert("RGB")
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((300, 300))
        ax.imshow(img)

    caption = item["caption"] if item["caption"] else "no caption"
    category = item.get("category", "unknown")
    ax.set_title(f"[{category}]\n{caption}", fontsize=8)
    ax.axis("off")

plt.subplots_adjust(hspace=0.4, wspace=0.1)
plt.savefig("samples.png", dpi=150, bbox_inches="tight")
plt.show()