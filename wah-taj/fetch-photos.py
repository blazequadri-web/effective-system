#!/usr/bin/env python3
"""
Fetch real, dish-matched photos for Wah! Taj Grill & Bowls into ./images/.

Source: Wikimedia Commons (freely licensed photos), resolved by SEARCH via the
official API so we never guess filenames. One photo is downloaded per dish
"query" and saved under every matching menu slug, so menu thumbnails, the
signature cards, and the gallery all light up.

REQUIRES these hosts in the environment's network egress allowlist:
    commons.wikimedia.org      (search + image-info API)
    upload.wikimedia.org       (the actual image files)

Run:  python3 fetch-photos.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
UA  = "WahTajSite/1.0 (menu photo fetch; contact: wahtajindopak.com)"
API = "https://commons.wikimedia.org/w/api.php"

def slugify(s):
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

# query (what to search on Commons)  ->  list of menu/feature names that share that photo
DISHES = {
    "Chicken biryani":      ["Chicken Biryani"],
    "Mutton biryani":       ["Mutton Biryani"],
    "Chicken 65":           ["Chicken 65", "Chicken 65 Bowl", "Chicken 65 Roll", "Chicken 65 Curry", "Chicken 65 Dry"],
    "Butter chicken":       ["Butter Chicken", "Butter Chicken Bowl", "Butter Chicken Curry"],
    "Chicken tikka masala": ["Chicken Tikka Masala Bowl"],
    "Palak paneer":         ["Palak Paneer"],
    "Paneer tikka":         ["Paneer Tikka Masala", "Navratan Korma"],
    "Mango lassi":          ["Mango Lassi"],
    "Samosa":               ["Vegetable Samosa"],
    "Pakora":               ["Chicken Pakora", "Mirchi Pakoda"],
    "Spring roll":          ["Spring Roll"],
    "Gulab jamun":          ["Gulab Jamun"],
    "Rasmalai":             ["Ras Malai"],
    "Gajar ka halwa":       ["Gajar Halwa", "Moong Daal Halwa", "Fruit Custard"],
    "Seekh kebab":          ["Seekh Kabab", "Seekh Kabab Roll", "4 Pieces Beef Seekh Kabab", "4 Pieces Chicken Seekh Kabab", "Seekh Fry Curry", "Shami Roll", "Bun Kabab"],
    "Tandoori chicken":     ["Tandoori Chicken", "8 Pieces Tandoori Boti", "2 Pieces Chicken Tikka", "Tandoori Tikka Boti Roll"],
    "Chicken malai tikka":  ["8 Pieces Chicken Malai Boti", "Chicken Malai Boti Roll", "Junior Platter"],
    "Chapli kabab":         ["2 Pieces Chapli Kabab"],
    "Mixed grill kebab platter": ["Mixed Grill Platter", "Wah! Taj Platter"],
    "Naan bread":           ["Plain Naan"],
    "Paratha":              ["Plain Paratha", "Lacha Paratha"],
    "Chicken karahi":       ["Karahi Chicken Curry", "Chicken Afghani Curry", "Nawabi Chicken Curry", "Chicken Achaari Curry"],
    "Chicken vindaloo":     ["Chicken Vindaloo Curry"],
    "Chilli chicken":       ["Chili Chicken Bowl", "Chilli Chicken Curry", "Chili Chicken Roll", "Chicken and Vegetable Bowl"],
    "Karahi gosht":         ["Karahi Gosht Curry", "Mutton Masala Curry", "Mutton Masala Bowl", "Talawa Gosht Curry"],
    "Nihari":               ["Beef Nihari Curry"],
    "Lamb chops":           ["6 Pieces Goat Chops"],
    "Fried fish":           ["4 Pieces Fish Fry"],
    "Dal tadka":            ["Daal Tarka", "Khatti Daal"],
    "Bhindi masala":        ["Bhindi Masala"],
    "Beef kati roll":       ["Beef Bihari Roll", "Frankie Roll"],
    "Fried rice":           ["Chicken Fried Rice", "Veg Fried Rice"],
    "Pulao rice":           ["Goat Pulao", "Peas Pulao"],
    "Cumin rice":           ["Zeera Rice", "Plain Rice", "Veg Bowl"],
    "Avocado milkshake":    ["Avocado Shake"],
    "Buttermilk drink":     ["Butter Milk Salted"],
    "Chicken nuggets":      ["Kids Chicken Nuggets"],
    "French fries":         ["Kids Fries"],
}

def api_get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)

def find_thumb(query, width=900):
    """Return a thumbnail URL for the best photo match, or None."""
    data = api_get({
        "action": "query", "format": "json",
        "generator": "search",
        "gsrsearch": "filetype:bitmap " + query,
        "gsrnamespace": "6", "gsrlimit": "6",
        "prop": "imageinfo", "iiprop": "url|mime", "iiurlwidth": str(width),
    })
    pages = (data.get("query") or {}).get("pages") or {}
    best = sorted(pages.values(), key=lambda p: p.get("index", 99))
    for p in best:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime", "").startswith("image/") and ii.get("thumburl"):
            return ii["thumburl"]
    return None

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if len(data) < 1500:
        raise IOError("suspiciously small (%d bytes) — likely blocked" % len(data))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def main():
    os.makedirs(OUT, exist_ok=True)
    ok = miss = 0
    for query, names in DISHES.items():
        try:
            thumb = find_thumb(query)
            if not thumb:
                print("  no match  : %s" % query); miss += 1; continue
            tmp = download(thumb, os.path.join(OUT, slugify(names[0]) + ".jpg"))
            # copy the same bytes to every other slug that uses this dish
            src = os.path.join(OUT, slugify(names[0]) + ".jpg")
            with open(src, "rb") as f:
                blob = f.read()
            for n in names[1:]:
                with open(os.path.join(OUT, slugify(n) + ".jpg"), "wb") as f:
                    f.write(blob)
            print("  ok        : %-26s -> %d slug(s), %d KB" % (query, len(names), tmp // 1024))
            ok += len(names)
        except Exception as e:
            print("  FAILED    : %-26s (%s)" % (query, e)); miss += 1
        time.sleep(0.3)
    print("\nDone. %d image file(s) written to %s  (%d queries missed)" % (ok, OUT, miss))
    if miss and ok == 0:
        print("\nAll fetches failed — confirm commons.wikimedia.org and upload.wikimedia.org\n"
              "are in your network egress allowlist, then re-run.")
        sys.exit(1)

if __name__ == "__main__":
    main()
