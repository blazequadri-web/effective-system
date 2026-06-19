#!/usr/bin/env python3
"""
Fetch real, dish-matched photos for Wah! Taj Grill & Bowls into ./images/.

Source: Wikimedia Commons (freely licensed photos), resolved by SEARCH via the
official API so we never guess filenames. For each dish we pull several search
candidates and SCORE them by how well the file title matches the dish — the
distinctive word (e.g. "biryani", "jamun", "tandoori") must appear, landscape
food shots are preferred — so we stop grabbing the first, often-wrong hit.
One photo is downloaded per dish "query" and saved under every matching menu
slug, so menu thumbnails, the signature cards, and the gallery all light up.

REQUIRES these hosts in the environment's network egress allowlist:
    commons.wikimedia.org      (search + image-info API)
    upload.wikimedia.org       (the actual image files)

Run:  python3 fetch-photos.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

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

# words too common to identify a dish on their own
GENERIC = {"chicken","mutton","beef","goat","lamb","fish","rice","curry","bowl",
           "roll","dry","pieces","piece","plain","mixed","grill","platter",
           "bread","drink","kebab","masala","ka"}
STOP = {"the","a","an","of","and","with","in","on","dish","food","cuisine",
        "style","homemade","recipe","indian","pakistani","desi","restaurant"}
# tokens in a file title that mean it's almost certainly NOT an appetizing plate
BAD = {"logo","map","sign","poster","menu","label","packet","packaging","box",
       "raw","uncooked","powder","spice","spices","plant","tree","leaf","leaves",
       "diagram","chart","portrait","statue","temple","building","street","market",
       "person","woman","man","chef","stamp","coin","painting","drawing"}

def words(s):
    return re.findall(r"[a-z0-9]+", s.lower())

def title_score(query, title):
    """Higher is better; -1 means reject. Requires the dish's distinctive word."""
    q = [w for w in words(query) if w not in STOP]
    t = set(words(title))
    if not q:
        return -1
    if t & BAD:
        return -1
    matched   = [w for w in q if w in t]
    distinct  = [w for w in q if w not in GENERIC]
    if distinct:
        hit_d = [w for w in distinct if w in t]
        if not hit_d:                 # must share a distinctive word
            return -1
        return len(hit_d) * 3 + len(matched)
    # query is all-generic (e.g. "Fried rice", "Naan bread") -> need every word
    if len(matched) < len(q):
        return -1
    return len(matched)

def api_get(params, tries=6):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < tries - 1:
                wait = 15 * (i + 1)
                print("    rate limited; waiting %ds…" % wait); time.sleep(wait); continue
            raise
    raise RuntimeError("API kept failing")

def find_thumb(query, width=1000):
    """Return the best-matching food photo thumbnail URL, or None."""
    data = api_get({
        "action": "query", "format": "json",
        "generator": "search",
        "gsrsearch": "filetype:bitmap " + query,
        "gsrnamespace": "6", "gsrlimit": "20",
        "prop": "imageinfo", "iiprop": "url|mime|size", "iiurlwidth": str(width),
    })
    pages = (data.get("query") or {}).get("pages") or {}
    best, best_score = None, 0
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("mime", "").startswith("image/"): continue
        thumb = ii.get("thumburl")
        if not thumb: continue
        title = re.sub(r"\.[a-z0-9]+$", "", p.get("title", "")).replace("File:", "")
        sc = title_score(query, title)
        if sc < 0: continue
        # prefer landscape-ish plates; penalize tall/portrait crops
        tw, th = ii.get("thumbwidth") or 1, ii.get("thumbheight") or 1
        ratio = th / tw
        bonus = 1.0 if ratio <= 1.05 else (0.6 if ratio <= 1.4 else 0.2)
        rank = sc + bonus
        if rank > best_score:
            best_score, best = rank, thumb
    return best

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < 4:
                wait = 15 * (i + 1)
                print("    rate limited (dl); waiting %ds…" % wait); time.sleep(wait); continue
            raise
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
                print("  no match  : %s" % query); miss += 1; time.sleep(1.0); continue
            first = os.path.join(OUT, slugify(names[0]) + ".jpg")
            kb = download(thumb, first)
            blob = open(first, "rb").read()
            for n in names[1:]:
                with open(os.path.join(OUT, slugify(n) + ".jpg"), "wb") as f:
                    f.write(blob)
            print("  ok        : %-26s -> %d slug(s), %d KB" % (query, len(names), kb // 1024))
            ok += len(names)
        except Exception as e:
            print("  FAILED    : %-26s (%s)" % (query, e)); miss += 1
        time.sleep(1.2)
    print("\nDone. %d image file(s) written to %s  (%d queries missed)" % (ok, OUT, miss))
    if miss and ok == 0:
        print("\nAll fetches failed — confirm commons.wikimedia.org and upload.wikimedia.org\n"
              "are in your network egress allowlist, then re-run.")
        sys.exit(1)

if __name__ == "__main__":
    main()
