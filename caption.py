import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os
import json

IMAGE_DIR = "images_hq"

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()

with open("image_metadata_hq.json", "r") as f:
    metadata = json.load(f)

results = []

for i, item in enumerate(metadata):
    path = os.path.join(IMAGE_DIR, item["filename"])

    if not os.path.exists(path):
        continue

    img = Image.open(path).convert("RGB")

    inputs = processor(img, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**inputs, max_length=50, num_beams=5)
    caption = processor.decode(out[0], skip_special_tokens=True)

    inputs2 = processor(img, text="a detailed description of", return_tensors="pt").to(device)
    with torch.no_grad():
        out2 = model.generate(**inputs2, max_length=75, num_beams=5)
    caption_detailed = processor.decode(out2[0], skip_special_tokens=True)

    results.append({
        "image_id": item["image_id"],
        "filename": item["filename"],
        "category": item.get("category", "unknown"),
        "caption": caption,
        "caption_detailed": caption_detailed
    })

    if (i + 1) % 500 == 0:
        print(f"{i+1}/{len(metadata)} done")

with open("dataset_with_captions.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Done. {len(results)} images captioned")