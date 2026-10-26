import json
import os
import pandas as pd

# -------------------------------------------------------------
# 1. SETUP PROJECT DIRECTORIES
# -------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------
# 2. LOCATE EXPORT.JSON
# -------------------------------------------------------------
candidates = [
    os.path.join(PROJECT_ROOT, "export.json"),
    os.path.join(PROJECT_ROOT, "datasets", "export.json"),
    os.path.join(PROJECT_ROOT, "data", "export.json"),
    "export.json",
    "datasets/export.json"
]

json_path = next((p for p in candidates if os.path.exists(p)), None)
if not json_path:
    raise FileNotFoundError("Could not find export.json. Please ensure it is in your project root or datasets/ folder.")

print(f"Reading campsite data from: {json_path}")
with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
    geojson_data = json.load(f)

# -------------------------------------------------------------
# 3. DEFINE THE 6 KEY AMENITIES & ORDER
# -------------------------------------------------------------
# Ordered from most basic (Tent Pitching) to highest utility (Drinking Water)
AMENITY_ORDER = [
    "Tent Pitching",
    "Caravan Access",
    "Flush Toilets",
    "Hot Showers",
    "Power Supply",
    "Drinking Water"
]

# -------------------------------------------------------------
# 4. PARSE FEATURES AND EXTRACT COMBINATIONS
# -------------------------------------------------------------
records = []
seen_ids = set()

for feat in geojson_data.get("features", []):
    props = feat.get("properties", {})
    geom = feat.get("geometry", {})
    coords = geom.get("coordinates", [None, None])

    # De-duplicate features
    feat_id = feat.get("id") or props.get("@id")
    if feat_id:
        if feat_id in seen_ids:
            continue
        seen_ids.add(feat_id)

    # Validate coordinate bounds for Australia
    if not (isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float))):
        continue
    lon, lat = float(coords[0]), float(coords[1])
    if not (110.0 <= lon <= 156.0 and -45.0 <= lat <= -9.0):
        continue

    tourism = props.get("tourism", "")
    if tourism not in ["camp_site", "caravan_site"]:
        continue

    # Extract binary presence (1 or 0) for each amenity
    tents = 1 if props.get("tents") == "yes" or tourism == "camp_site" else 0
    caravans = 1 if props.get("caravan") == "yes" or props.get("caravans") == "yes" or tourism == "caravan_site" else 0
    toilets = 1 if props.get("toilets") == "yes" or props.get("toilet") == "yes" else 0
    showers = 1 if props.get("shower") in ["yes", "hot"] else 0
    power = 1 if props.get("power_supply") in ["yes", "15"] else 0
    water = 1 if props.get("drinking_water") == "yes" or props.get("water_point") == "yes" else 0

    # Only include records where at least one amenity is documented
    if (tents + caravans + toilets + showers + power + water) == 0:
        continue

    records.append({
        "Tent Pitching": tents,
        "Caravan Access": caravans,
        "Flush Toilets": toilets,
        "Hot Showers": showers,
        "Power Supply": power,
        "Drinking Water": water
    })

df_raw = pd.DataFrame(records)
print(f"Processed {len(df_raw):,} campsites with documented amenities.")

# -------------------------------------------------------------
# 5. AGGREGATE COMBINATIONS & SELECT TOP 10 BUNDLES
# -------------------------------------------------------------
bundle_counts = df_raw.groupby(AMENITY_ORDER).size().reset_index(name="count")
bundle_counts = bundle_counts.sort_values(by="count", ascending=False).reset_index(drop=True)

# Select top 10 most frequent bundles
top_bundles = bundle_counts.head(10).copy()

# Name each bundle based on what it contains
def generate_bundle_name(row):
    active = [amenity for amenity in AMENITY_ORDER if row[amenity] == 1]
    if len(active) == 6:
        return "Full-Service Park"
    if active == ["Tent Pitching"]:
        return "Tents Only"
    if active == ["Tent Pitching", "Flush Toilets"]:
        return "Tents + Toilets"
    if active == ["Tent Pitching", "Caravan Access"]:
        return "Caravans + Tents"
    if active == ["Tent Pitching", "Caravan Access", "Flush Toilets"]:
        return "Caravans + Tents + Toilets"
    if active == ["Flush Toilets"]:
        return "Toilets Only (Rest Stop)"
    if set(active) == {"Tent Pitching", "Caravan Access", "Flush Toilets", "Hot Showers"}:
        return "Basic Holiday Park"
    if set(active) == {"Tent Pitching", "Caravan Access", "Flush Toilets", "Hot Showers", "Power Supply"}:
        return "Powered Holiday Park"
    if set(active) == {"Tent Pitching", "Flush Toilets", "Drinking Water"}:
        return "Tents + Water + Toilets"
    if set(active) == {"Caravan Access", "Flush Toilets"}:
        return "Caravans + Toilets"
    return " + ".join(active)

top_bundles["bundle_name"] = top_bundles.apply(generate_bundle_name, axis=1)
top_bundles["bundle_id"] = range(1, len(top_bundles) + 1)

# -------------------------------------------------------------
# 6. RESHAPE TO LONG FORMAT FOR UPSET PLOT
# -------------------------------------------------------------
upset_rows = []

for _, b_row in top_bundles.iterrows():
    b_id = b_row["bundle_id"]
    b_name = b_row["bundle_name"]
    b_count = int(b_row["count"])

    # Find the lowest and highest active amenity in the order (for the vertical connecting line)
    active_amenities = [a for a in AMENITY_ORDER if b_row[a] == 1]
    min_amenity = active_amenities[0] if active_amenities else AMENITY_ORDER[0]
    max_amenity = active_amenities[-1] if active_amenities else AMENITY_ORDER[0]

    for amenity in AMENITY_ORDER:
        present = int(b_row[amenity])
        upset_rows.append({
            "bundle_id": b_id,
            "bundle_name": b_name,
            "count": b_count,
            "amenity": amenity,
            "present": present,
            "min_amenity": min_amenity,
            "max_amenity": max_amenity
        })

df_upset = pd.DataFrame(upset_rows)

# -------------------------------------------------------------
# 7. EXPORT CSV
# -------------------------------------------------------------
output_path = os.path.join(DATA_DIR, "campsite_amenities_upset.csv")
df_upset.to_csv(output_path, index=False)

print(f"\nSuccessfully generated and exported '{output_path}'!")
print(f"Total rows in exported CSV: {len(df_upset)}")
print("\nTop 5 Bundles preview:")
print(top_bundles[["bundle_id", "bundle_name", "count"]].head(5))