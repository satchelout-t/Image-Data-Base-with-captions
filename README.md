# Image Captioning Dataset

Harpreet Singh | IIT Bombay

## What I did

Built a dataset of 10,617 images with captions. Scraped images from Pexels API and used BLIP model to generate captions for each image.

## How it works

1. Picked 12 categories relevant to surveillance (people walking, vehicles, parking lots, night streets, entrances etc)
2. Used Pexels API to download ~1000 images per category
3. Ran BLIP (Salesforce/blip-image-captioning-base) on each image to generate captions
4. Generated 2 captions per image - one basic and one detailed

## Files

- `eagle_eye_assignment.ipynb` - main notebook with all the code and analysis
- `images_hq/` - folder with all 10,617 images
- `dataset_with_captions.json` - images mapped to their captions
- `dataset_with_captions.csv` - same thing in csv format
- `image_metadata_hq.json` - metadata for each image (source, category, size etc)

## Tools used

- Python 3.11
- PyTorch with CUDA (RTX 3050)
- HuggingFace transformers (BLIP model)
- Pexels API for images
- matplotlib for visualizations

## Some notes

- Initially tried medium size images from pexels but they were too small (20-30kb). Switched to large size which gave much better quality
- Some captions are similar because similar looking images get similar descriptions. Could improve this with more diverse queries or using conditional prompting
- The whole pipeline took about 4-5 hours total (2-3 hours scraping + 2 hours captioning)
