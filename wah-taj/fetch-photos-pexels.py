#!/usr/bin/env python3
"""
Fetch clean, single-dish photos for Wah! Taj Grill & Bowls from Pexels.

Why Pexels: high-quality, properly-lit single-dish food photography, and every
image is served from one host (images.pexels.com) so it works behind a strict
egress allowlist. Pexels search is relevance-ranked, so we take the top
landscape result per dish — no empty pans, prep shots, or multi-dish plates.

REQUIRES:
  * env var PEXELS_API_KEY   (free key from https://www.pexels.com/api/)
  * these hosts in the environment's network egress allowlist:
        api.pexels.com         (search API)
        images.pexels.com      (the photo files)

Run:  PEXELS_API_KEY=xxxx python3 fetch-photos-pexels.py
One photo is downloaded per query and copied to every slug that shares it, so
the menu thumbnails, signature cards, and gallery all get matching imagery.
Per Pexels terms we keep attribution in images/CREDITS.txt.
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
KEY = os.environ.get("PEXELS_API_KEY", "").strip()
API = "https://api.pexels.com/v1/search"

def slugify(s):
    s = s.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

# Pexels search query  ->  menu / feature / gallery dish names that use that photo.
# Queries are picked so the top result is a clean, single plate of the right thing
# (a roll looks like a roll, a curry like a curry, a drink like a drink).
DISHES = [
    ("chicken biryani rice",        ["Chicken Biryani"]),
    ("mutton biryani",              ["Mutton Biryani"]),
    ("fried chicken 65 indian",     ["Chicken 65", "Chicken 65 Bowl", "Chicken 65 Curry", "Chicken 65 Dry"]),
    ("butter chicken curry",        ["Butter Chicken", "Butter Chicken Bowl", "Butter Chicken Curry"]),
    ("chicken tikka masala",        ["Chicken Tikka Masala Bowl"]),
    ("palak paneer spinach curry",  ["Palak Paneer"]),
    ("paneer tikka masala",         ["Paneer Tikka Masala"]),
    ("vegetable korma curry",       ["Navratan Korma"]),
    ("mango lassi drink",           ["Mango Lassi"]),
    ("samosa",                      ["Vegetable Samosa"]),
    ("chicken pakora fritters",     ["Chicken Pakora", "Mirchi Pakoda"]),
    ("spring rolls",                ["Spring Roll"]),
    ("gulab jamun dessert",         ["Gulab Jamun"]),
    ("rasmalai dessert",            ["Ras Malai"]),
    ("carrot halwa dessert",        ["Gajar Halwa"]),
    ("indian halwa sweet",          ["Moong Daal Halwa"]),
    ("fruit custard dessert",       ["Fruit Custard"]),
    ("seekh kebab grilled",         ["Seekh Kabab", "4 Pieces Beef Seekh Kabab", "4 Pieces Chicken Seekh Kabab", "Seekh Fry Curry"]),
    ("tandoori chicken",            ["Tandoori Chicken", "8 Pieces Tandoori Boti", "2 Pieces Chicken Tikka"]),
    ("chicken tikka skewers",       ["8 Pieces Chicken Malai Boti", "Junior Platter"]),
    ("chapli kebab patty",          ["2 Pieces Chapli Kabab"]),
    ("mixed grill kebab platter",   ["Mixed Grill Platter", "Wah! Taj Platter"]),
    ("naan bread",                  ["Plain Naan"]),
    ("paratha flatbread",           ["Plain Paratha", "Lacha Paratha"]),
    ("chicken karahi curry",        ["Karahi Chicken Curry", "Chicken Afghani Curry", "Nawabi Chicken Curry", "Chicken Achaari Curry"]),
    ("chicken vindaloo curry",      ["Chicken Vindaloo Curry"]),
    ("chilli chicken indo chinese", ["Chili Chicken Bowl", "Chilli Chicken Curry", "Chili Chicken Roll", "Chicken and Vegetable Bowl"]),
    ("mutton curry gosht",          ["Karahi Gosht Curry", "Mutton Masala Curry", "Mutton Masala Bowl", "Talawa Gosht Curry"]),
    ("beef nihari curry",           ["Beef Nihari Curry"]),
    ("grilled lamb chops",          ["6 Pieces Goat Chops"]),
    ("fried fish fillet",           ["4 Pieces Fish Fry"]),
    ("dal tadka lentil curry",      ["Daal Tarka", "Khatti Daal"]),
    ("bhindi okra curry",           ["Bhindi Masala"]),
    ("kathi roll wrap",             ["Beef Bihari Roll", "Shami Roll", "Tandoori Tikka Boti Roll", "Chicken Malai Boti Roll",
                                     "Seekh Kabab Roll", "Chicken 65 Roll", "Chili Chicken Roll", "Frankie Roll"]),
    ("bun kabab burger",            ["Bun Kabab"]),
    ("chicken fried rice",          ["Chicken Fried Rice"]),
    ("vegetable fried rice",        ["Veg Fried Rice"]),
    ("pulao rice",                  ["Goat Pulao", "Peas Pulao"]),
    ("basmati rice bowl",           ["Plain Rice", "Zeera Rice", "Veg Bowl"]),
    ("avocado milkshake",           ["Avocado Shake"]),
    ("buttermilk lassi glass",      ["Butter Milk Salted"]),
    ("chicken nuggets",             ["Kids Chicken Nuggets"]),
    ("french fries",                ["Kids Fries"]),
]

def api_search(query, per_page=8):
    url = API + "?" + urllib.parse.urlencode({
        "query": query, "per_page": per_page,
        "orientation": "landscape", "size": "medium",
    })
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "WahTaj/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < 4:
                print("    rate limited; waiting 20s…"); time.sleep(20); continue
            raise
    raise RuntimeError("search kept failing")

def pick(photos):
    """Top relevance-ranked landscape photo that's a reasonable size."""
    for p in photos:
        if (p.get("width") or 0) >= 700:
            return p
    return photos[0] if photos else None

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "WahTaj/1.0"})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < 4:
                print("    rate limited (dl); waiting 20s…"); time.sleep(20); continue
            raise
    if len(data) < 2000:
        raise IOError("image too small (%d bytes)" % len(data))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def main():
    if not KEY:
        sys.exit("PEXELS_API_KEY is not set. Get a free key at https://www.pexels.com/api/ "
                 "and run:  PEXELS_API_KEY=xxxx python3 fetch-photos-pexels.py")
    os.makedirs(OUT, exist_ok=True)
    credits, ok, miss = [], 0, 0
    for query, names in DISHES:
        try:
            data = api_search(query)
            photo = pick(data.get("photos", []))
            if not photo:
                print("  no result : %s" % query); miss += 1; time.sleep(0.4); continue
            src = photo["src"].get("large") or photo["src"].get("large2x") or photo["src"]["original"]
            first = os.path.join(OUT, slugify(names[0]) + ".jpg")
            kb = download(src, first)
            blob = open(first, "rb").read()
            for n in names[1:]:
                with open(os.path.join(OUT, slugify(n) + ".jpg"), "wb") as f:
                    f.write(blob)
            credits.append("%-26s  %s  by %s (%s)" % (query, photo.get("url",""),
                            photo.get("photographer",""), "Pexels"))
            print("  ok        : %-28s -> %d slug(s), %d KB" % (query, len(names), kb // 1024))
            ok += len(names)
        except Exception as e:
            print("  FAILED    : %-28s (%s)" % (query, e)); miss += 1
        time.sleep(0.5)
    if credits:
        with open(os.path.join(OUT, "CREDITS.txt"), "w") as f:
            f.write("Dish photos via Pexels (https://www.pexels.com) — free to use.\n\n" + "\n".join(credits) + "\n")
    print("\nDone. %d image file(s) written to %s  (%d queries missed)" % (ok, OUT, miss))
    if ok == 0:
        print("\nAll fetches failed — confirm api.pexels.com and images.pexels.com are in the\n"
              "network egress allowlist and PEXELS_API_KEY is valid, then re-run.")
        sys.exit(1)

if __name__ == "__main__":
    main()
