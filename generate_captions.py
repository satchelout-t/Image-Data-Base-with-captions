import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os
import json
import csv
import time

IMAGE_DIR = "images_hq"
METADATA_FILE = "image_metadata_hq.json"

print("Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()
print(f"Running on: {device}")


def get_caption(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        inputs = processor(img, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_length=50, num_beams=5, early_stopping=True)
        return processor.decode(out[0], skip_special_tokens=True)
    except:
        return None


def get_detailed_caption(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        inputs = processor(img, text="a detailed description of", return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_length=75, num_beams=5, early_stopping=True)
        return processor.decode(out[0], skip_special_tokens=True)
    except:
        return None


if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)
    print(f"Found {len(metadata)} images in metadata")
else:
    files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith((".jpg", ".jpeg", ".png"))])
    metadata = [{"image_id": i, "filename": f, "category": "unknown"} for i, f in enumerate(files)]
    print(f"Found {len(metadata)} images in folder")

results = []
total = len(metadata)
start = time.time()

print(f"Generating captions for {total} images...\n")

for i, item in enumerate(metadata):
    path = os.path.join(IMAGE_DIR, item["filename"])

    if not os.path.exists(path):
        continue

    cap = get_caption(path)
    cap_detail = get_detailed_caption(path)

    results.append({
        "image_id": item["image_id"],
        "filename": item["filename"],
        "category": item.get("category", "unknown"),
        "caption": cap,
        "caption_detailed": cap_detail
    })

    if (i + 1) % 100 == 0:
        elapsed = time.time() - start
        speed = (i + 1) / elapsed
        remaining = (total - i - 1) / speed / 60
        print(f"  {i+1}/{total} done | {speed:.1f} img/s | ~{remaining:.0f} min left")

    if (i + 1) % 500 == 0:
        torch.cuda.empty_cache()

with open("dataset_with_captions.json", "w") as f:
    json.dump(results, f, indent=2)

with open("dataset_with_captions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["image_id", "filename", "category", "caption", "caption_detailed"])
    writer.writeheader()
    writer.writerows(results)

elapsed = time.time() - start
print(f"\nDone. {len(results)} images captioned in {elapsed/60:.1f} minutes")
print(f"Saved: dataset_with_captions.json, dataset_with_captions.csv")

print("\nSample captions:")
for r in results[:5]:
    print(f"  {r['filename']}: {r['caption']}")