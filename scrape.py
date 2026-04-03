import requests
import os
import time
import json

API_KEY = "2o01TwDUMOlKQFA5sP2cH5j2WloD98PiiuC6BF393PBGSiBcOSho9xCF"
IMAGE_DIR = "images_hq"
os.makedirs(IMAGE_DIR, exist_ok=True)

CATEGORIES = {
    "people_walking": ["people walking street", "pedestrians sidewalk city", "person walking urban road", "people crossing road", "man walking alone street", "woman walking city"],
    "street_scene": ["street scene urban", "city street daytime", "urban road buildings", "downtown street view", "residential street neighborhood", "busy city road"],
    "parking_lot": ["parking lot cars", "car park outdoor", "parking garage vehicles", "parking area shopping mall", "underground parking", "parking space"],
    "vehicles": ["vehicles cars road", "cars driving highway", "automobile traffic city", "car on street parked", "bus on road city", "motorcycle road urban"],
    "office_building": ["office building exterior", "commercial building", "corporate building entrance", "modern office architecture", "skyscraper building city", "glass building facade"],
    "indoor_spaces": ["indoor hallway corridor", "building interior hallway", "office corridor inside", "hotel lobby interior", "shopping mall interior", "warehouse interior"],
    "crowd": ["crowd of people gathering", "group of people outdoor", "busy public place people", "people gathering event", "train station crowd", "market crowd people"],
    "entrance_security": ["entrance door building", "building doorway entry", "security gate entrance", "glass door entrance office", "lobby entrance building", "turnstile entrance"],
    "night_surveillance": ["night street city lights", "city night urban", "dark street lamps", "nighttime road cars", "night parking lot", "street night security"],
    "traffic_vehicles": ["traffic intersection cars", "busy road traffic", "vehicles traffic light", "road junction cars", "highway traffic aerial", "traffic jam city"],
    "security_camera_view": ["surveillance camera view", "cctv security monitoring", "security guard building", "gated community entrance", "warehouse security", "retail store interior"],
    "outdoor_areas": ["campus outdoor walkway", "park pathway people", "sidewalk cafe outdoor", "public square city", "train platform station", "airport terminal people"]
}

headers = {"Authorization": API_KEY}
seen_ids = set()
all_metadata = []
img_count = 0

for cat_name, queries in CATEGORIES.items():
    print(f"\n--- {cat_name} ---")

    for query in queries:
        if img_count >= 10500:
            break

        page = 1
        while True:
            resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params={"query": query, "per_page": 80, "page": page}, timeout=30)

            if resp.status_code == 429:
                time.sleep(60)
                continue

            if resp.status_code != 200:
                break

            photos = resp.json().get("photos", [])
            if not photos:
                break

            for photo in photos:
                if photo["id"] in seen_ids or photo["width"] < 640:
                    continue

                fname = f"img_{img_count:05d}.jpg"
                fpath = os.path.join(IMAGE_DIR, fname)

                try:
                    img_resp = requests.get(photo["src"]["large"], timeout=30)
                    if img_resp.status_code == 200 and len(img_resp.content) > 50000:
                        with open(fpath, "wb") as f:
                            f.write(img_resp.content)

                        all_metadata.append({
                            "image_id": img_count,
                            "filename": fname,
                            "category": cat_name,
                            "pexels_id": photo["id"],
                            "width": photo["width"],
                            "height": photo["height"]
                        })
                        seen_ids.add(photo["id"])
                        img_count += 1
                except:
                    pass

            page += 1
            time.sleep(1)

        print(f"  '{query}' done | total so far: {img_count}")

    if img_count >= 10500:
        break

with open("image_metadata_hq.json", "w") as f:
    json.dump(all_metadata, f, indent=2)

print(f"\nDone. {img_count} images saved.")