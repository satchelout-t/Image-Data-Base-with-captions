import requests
import os
import time
import json

API_KEY = "YOUR_PEXELS_API_KEY_HERE"

IMAGE_DIR = "images_hq"
os.makedirs(IMAGE_DIR, exist_ok=True)

CATEGORIES = {
    "people_walking": [
        "people walking street",
        "pedestrians sidewalk city",
        "person walking urban road",
        "people crossing road",
        "man walking alone street",
        "woman walking city"
    ],
    "street_scene": [
        "street scene urban",
        "city street daytime",
        "urban road buildings",
        "downtown street view",
        "residential street neighborhood",
        "busy city road"
    ],
    "parking_lot": [
        "parking lot cars",
        "car park outdoor",
        "parking garage vehicles",
        "parking area shopping mall",
        "underground parking",
        "parking space"
    ],
    "vehicles": [
        "vehicles cars road",
        "cars driving highway",
        "automobile traffic city",
        "car on street parked",
        "bus on road city",
        "motorcycle road urban"
    ],
    "office_building": [
        "office building exterior",
        "commercial building",
        "corporate building entrance",
        "modern office architecture",
        "skyscraper building city",
        "glass building facade"
    ],
    "indoor_spaces": [
        "indoor hallway corridor",
        "building interior hallway",
        "office corridor inside",
        "hotel lobby interior",
        "shopping mall interior",
        "warehouse interior"
    ],
    "crowd": [
        "crowd of people gathering",
        "group of people outdoor",
        "busy public place people",
        "people gathering event",
        "train station crowd",
        "market crowd people"
    ],
    "entrance_security": [
        "entrance door building",
        "building doorway entry",
        "security gate entrance",
        "glass door entrance office",
        "lobby entrance building",
        "turnstile entrance"
    ],
    "night_surveillance": [
        "night street city lights",
        "city night urban",
        "dark street lamps",
        "nighttime road cars",
        "night parking lot",
        "street night security"
    ],
    "traffic_vehicles": [
        "traffic intersection cars",
        "busy road traffic",
        "vehicles traffic light",
        "road junction cars",
        "highway traffic aerial",
        "traffic jam city"
    ],
    "security_camera_view": [
        "surveillance camera view",
        "cctv security monitoring",
        "security guard building",
        "gated community entrance",
        "warehouse security",
        "retail store interior"
    ],
    "outdoor_areas": [
        "campus outdoor walkway",
        "park pathway people",
        "sidewalk cafe outdoor",
        "public square city",
        "train platform station",
        "airport terminal people"
    ]
}

HEADERS = {"Authorization": API_KEY}
seen_ids = set()


def download_image(url, filepath):
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 50000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False


def scrape_query(query, category, start_id):
    count = 0
    page = 1
    metadata = []

    while True:
        params = {"query": query, "per_page": 80, "page": page}

        try:
            resp = requests.get("https://api.pexels.com/v1/search", headers=HEADERS, params=params, timeout=30)

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

                img_id = start_id + count
                fname = f"img_{img_id:05d}.jpg"
                fpath = os.path.join(IMAGE_DIR, fname)

                if download_image(photo["src"]["large"], fpath):
                    metadata.append({
                        "image_id": img_id,
                        "filename": fname,
                        "category": category,
                        "query": query,
                        "pexels_id": photo["id"],
                        "photographer": photo.get("photographer", "unknown"),
                        "width": photo["width"],
                        "height": photo["height"]
                    })
                    seen_ids.add(photo["id"])
                    count += 1

            page += 1
            time.sleep(1)

        except:
            time.sleep(5)
            continue

    return count, metadata


def main():
    all_metadata = []
    total = 0
    next_id = 0

    for cat_name, queries in CATEGORIES.items():
        print(f"\n--- {cat_name} ---")
        cat_count = 0

        for q in queries:
            if total >= 10500:
                break
            n, meta = scrape_query(q, cat_name, next_id)
            print(f"  '{q}' -> {n} images")
            all_metadata.extend(meta)
            cat_count += n
            total += n
            next_id += n

        print(f"  total for {cat_name}: {cat_count}")
        print(f"  overall: {total}")

        with open("image_metadata_hq.json", "w") as f:
            json.dump(all_metadata, f, indent=2)

        if total >= 10500:
            break

    print(f"\nDone. {len(all_metadata)} images saved.")


main()