# Dish photos

Real, dish-matched photos live here as `images/<slug>.jpg`, where `<slug>` is the
lowercased, hyphenated dish name (e.g. `chicken-biryani.jpg`, `butter-chicken-bowl.jpg`).

Until a photo exists for a dish, the site shows an elegant gold fallback tile with
the dish name — so the layout always looks intentional.

## Populating photos automatically

Run the fetch script from the `wah-taj/` folder:

```bash
python3 fetch-photos.py
```

It pulls freely-licensed, dish-matched photos from Wikimedia Commons (resolved by
search, so no guessed filenames) and writes them here.

**Requires these hosts in the environment's network egress allowlist:**

- `commons.wikimedia.org` (search + image-info API)
- `upload.wikimedia.org` (the image files)

## Using your own photos

Drop a JPG named after the dish slug (e.g. `chicken-65.jpg`) into this folder and
it will be used automatically — best for your real restaurant photography.
