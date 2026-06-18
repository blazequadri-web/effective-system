#!/usr/bin/env python3
"""
Best-effort: pull dish-matched real photos from GitHub image-classification
datasets (the ONLY image source reachable from this environment's egress
allowlist). Discovers repos via the GitHub search API, finds ones that COMMIT
images in dish-named folders, and downloads one representative photo per dish.

Waits for the unauthenticated API rate limit to reset if needed.
Skips slugs that already have a photo. Writes to ./images/.
"""
import json, os, re, sys, time, urllib.request, urllib.error

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
UA  = {"User-Agent": "WahTajPhotoFetch/1.0"}
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

def norm(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

# dish keyword(s) (matched against folder/file names)  ->  slugs to fill
TARGETS = [
    (["biryani"],                              ["chicken-biryani","mutton-biryani","goat-pulao","peas-pulao"]),
    (["chicken_65","chicken65"],               ["chicken-65","chicken-65-bowl","chicken-65-roll","chicken-65-curry","chicken-65-dry"]),
    (["chilli_chicken","chili_chicken","chicken_manchurian"], ["chili-chicken-bowl","chilli-chicken-curry","chili-chicken-roll"]),
    (["tandoori_chicken","tandoori"],          ["tandoori-chicken","8-pieces-tandoori-boti","2-pieces-chicken-tikka","tandoori-tikka-boti-roll"]),
    (["chicken_tikka_masala"],                 ["chicken-tikka-masala-bowl"]),
    (["seekh","kebab","kakori","shami_kebab","reshmi"], ["seekh-kabab","seekh-kabab-roll","4-pieces-beef-seekh-kabab","4-pieces-chicken-seekh-kabab","seekh-fry-curry","shami-roll","2-pieces-chapli-kabab","mixed-grill-platter","wah-taj-platter","junior-platter","8-pieces-chicken-malai-boti","chicken-malai-boti-roll","beef-bihari-roll"]),
    (["samosa"],                               ["vegetable-samosa"]),
    (["pakora","pakode","pakoda"],             ["chicken-pakora","mirchi-pakoda"]),
    (["spring_roll"],                          ["spring-roll"]),
    (["gulab_jamun","gulab"],                  ["gulab-jamun"]),
    (["rasmalai","ras_malai"],                 ["ras-malai"]),
    (["gajar","halwa"],                        ["gajar-halwa","moong-daal-halwa"]),
    (["kulfi","custard","falooda"],            ["fruit-custard"]),
    (["lassi"],                                ["mango-lassi","butter-milk-salted"]),
    (["palak_paneer","palak","saag"],          ["palak-paneer"]),
    (["kadai_paneer","shahi_paneer","paneer_butter","paneer"], ["navratan-korma"]),
    (["chapati","paratha","roti"],             ["plain-paratha","lacha-paratha"]),
    (["fried_rice"],                           ["chicken-fried-rice","veg-fried-rice"]),
    (["jeera_rice","plain_rice","steamed_rice","white_rice"], ["plain-rice","zeera-rice","veg-bowl","chicken-and-vegetable-bowl"]),
    (["kadai_chicken","chicken_curry","murgh","chicken_masala","chicken_korma"], ["karahi-chicken-curry","chicken-afghani-curry","nawabi-chicken-curry","chicken-achaari-curry","chicken-vindaloo-curry"]),
    (["nihari"],                               ["beef-nihari-curry"]),
    (["rogan_josh","mutton_curry","mutton_masala","gosht","mutton_rogan"], ["karahi-gosht-curry","mutton-masala-curry","mutton-masala-bowl","talawa-gosht-curry"]),
    (["fish_fry","fish_curry","fish"],         ["4-pieces-fish-fry"]),
    (["lamb_chops","mutton_chops","chops"],    ["6-pieces-goat-chops"]),
    (["bhindi","okra"],                        ["bhindi-masala"]),
    (["dal_makhani","daal","dal","tadka"],     ["khatti-daal"]),
    (["kathi_roll","frankie","roll"],          ["frankie-roll","bun-kabab"]),
    (["chicken_nuggets","fried_chicken","chicken_wings"], ["kids-chicken-nuggets"]),
    (["french_fries","fries"],                 ["kids-fries"]),
    (["avocado","milkshake","smoothie","shake"], ["avocado-shake"]),
]

SEARCH_QUERIES = [
    "indian food image classification dataset",
    "indian food images dataset cnn",
    "food classification indian dishes dataset",
    "pakistani food image dataset",
]

def api(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                reset = e.headers.get("X-RateLimit-Reset")
                wait = max(5, int(reset) - int(time.time()) + 3) if reset else 60
                if wait > 1800:  # don't wait absurdly long
                    raise
                print("  rate limited; waiting %ds for reset..." % wait, flush=True)
                time.sleep(wait); continue
            raise
    raise RuntimeError("API kept failing: " + url)

def search_repos():
    seen, repos = set(), []
    for q in SEARCH_QUERIES:
        url = "https://api.github.com/search/repositories?q=" + urllib.request.quote(q) + "&sort=stars&per_page=12"
        try:
            for item in api(url).get("items", []):
                fn = item["full_name"]
                if fn not in seen:
                    seen.add(fn); repos.append((fn, item.get("default_branch", "main")))
        except Exception as e:
            print("  search failed (%s): %s" % (q, e), flush=True)
        time.sleep(1)
    return repos

def get_image_tree(full_name, branch):
    url = "https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (full_name, branch)
    try:
        data = api(url)
    except Exception:
        return None
    if data.get("truncated"):
        pass  # still usable, just partial
    folders = {}  # norm(folder) -> [paths]
    for n in data.get("tree", []):
        if n.get("type") != "blob": continue
        p = n["path"]
        if not p.lower().endswith(IMG_EXT): continue
        parts = p.split("/")
        folder = norm(parts[-2]) if len(parts) > 1 else ""
        fname  = norm(parts[-1])
        folders.setdefault(folder, []).append(p)
        folders.setdefault("file::"+fname, []).append(p)  # filename-based fallback
    return folders

def raw_url(full_name, branch, path):
    return "https://raw.githubusercontent.com/%s/%s/%s" % (full_name, branch, urllib.request.quote(path))

def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
    if len(b) < 4000: raise IOError("too small")
    if b[:2] != b"\xff\xd8" and b[:8] != b"\x89PNG\r\n\x1a\n" and b[:4] != b"RIFF":
        raise IOError("not an image (%r)" % b[:6])
    with open(dest, "wb") as f: f.write(b)
    return len(b)

def find_in_folders(folders, keywords):
    """Return a list of candidate image paths from folders matching a keyword."""
    for kw in keywords:
        kw = norm(kw)
        # exact-ish folder name match first
        for fname, paths in folders.items():
            if fname.startswith("file::"): continue
            if fname == kw or kw in fname.split("_") or fname in kw.split("_"):
                if paths: return sorted(paths)
        # looser substring folder match
        for fname, paths in folders.items():
            if fname.startswith("file::"): continue
            if kw in fname and paths: return sorted(paths)
    # filename-based fallback
    for kw in keywords:
        kw = norm(kw)
        hits = []
        for fname, paths in folders.items():
            if fname.startswith("file::") and kw in fname[6:]:
                hits += paths
        if hits: return sorted(hits)
    return []

def main():
    os.makedirs(OUT, exist_ok=True)
    print("Searching GitHub for committed Indian/Pakistani food image datasets...", flush=True)
    repos = search_repos()
    print("  candidate repos: %d" % len(repos), flush=True)

    # score repos by how many target keywords they can satisfy
    trees = []
    for fn, br in repos:
        folders = get_image_tree(fn, br)
        if not folders: continue
        score = sum(1 for kws, _ in TARGETS if find_in_folders(folders, kws))
        if score:
            trees.append((score, fn, br, folders))
            print("  %-55s images-folders match=%d" % (fn, score), flush=True)
        time.sleep(0.6)
    trees.sort(reverse=True, key=lambda t: t[0])
    if not trees:
        print("\nNo repo with committed dish-labeled images was found.", flush=True)
        return

    got = 0
    for kws, slugs in TARGETS:
        # all slugs already present?
        if all(os.path.exists(os.path.join(OUT, s + ".jpg")) for s in slugs):
            continue
        blob = None; src = None
        for score, fn, br, folders in trees:
            cands = find_in_folders(folders, kws)
            if not cands: continue
            pick = cands[len(cands)//2]
            try:
                tmp = os.path.join(OUT, "_tmp_dl")
                download(raw_url(fn, br, pick), tmp)
                blob = open(tmp, "rb").read(); os.remove(tmp); src = fn
                break
            except Exception:
                continue
        if not blob:
            print("  miss : %s" % kws[0], flush=True); continue
        for s in slugs:
            dest = os.path.join(OUT, s + ".jpg")
            if os.path.exists(dest): continue
            with open(dest, "wb") as f: f.write(blob)
            got += 1
        print("  ok   : %-22s -> %d slug(s)  [%s]" % (kws[0], len(slugs), src), flush=True)

    print("\nDone. Wrote %d new photo file(s) to %s" % (got, OUT), flush=True)

if __name__ == "__main__":
    main()
