import os
import re
import json
import pandas as pd

# 1. Locate export.json
candidates = [
    'export.json',
    'datasets/export.json',
    'FIT3179-Data-Visualization-2/datasets/export.json',
    'data/export.json'
]
file_path = next((p for p in candidates if os.path.exists(p)), None)

if not file_path:
    raise FileNotFoundError("Could not find export.json! Place it in the root or datasets/ folder.")

print(f"Loading {file_path}...")
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    raw_content = f.read().strip()

# Handle potential duplicate FeatureCollection headers
features = []
try:
    data = json.loads(raw_content)
    features = data.get('features', [])
except Exception:
    # Fallback regex if file was pasted with duplicate FeatureCollections
    print("Standard JSON load failed. Using regex feature extractor...")
    pattern = re.compile(r'\{\s*"type"\s*:\s*"Feature"\s*,.*?\}(?=\s*,\s*\{\s*"type"\s*:\s*"Feature"|\s*\])', re.DOTALL)
    for m in pattern.finditer(raw_content):
        try:
            features.append(json.loads(m.group(0)))
        except Exception:
            continue

print(f"Parsed {len(features)} campsite features.")

# 2. State bounding helper
def determine_state(props, lon, lat):
    st = str(props.get('addr:state', '')).strip().upper().replace('.', '')
    state_map = {
        'NEW SOUTH WALES': 'NSW', 'VICTORIA': 'VIC', 'QUEENSLAND': 'QLD',
        'WESTERN AUSTRALIA': 'WA', 'SOUTH AUSTRALIA': 'SA', 'TASMANIA': 'TAS',
        'NORTHERN TERRITORY': 'NT', 'AUSTRALIAN CAPITAL TERRITORY': 'ACT'
    }
    if st in ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']:
        return st
    if st in state_map:
        return state_map[st]

    # Coordinate boundaries
    if lat < -39.2:
        return 'TAS'
    if lon < 129.0:
        return 'WA'
    if 129.0 <= lon < 138.0:
        return 'NT' if lat >= -26.0 else 'SA'
    if 138.0 <= lon < 141.0:
        return 'SA' if lat < -26.0 else ('NT' if lon < 138.0 else 'QLD')
    if lon >= 141.0:
        if lat > -28.1:
            return 'QLD'
        if -35.95 <= lat <= -35.1 and 148.75 <= lon <= 149.4:
            return 'ACT'
        if lat <= -37.5:
            return 'VIC'
        if lat < -34.0 and lon < 148.0:
            return 'VIC' if lat < -35.8 else 'NSW'
        return 'NSW'
    return 'NSW'

# 3. Process every record
records = []
seen_ids = set()

for feat in features:
    props = feat.get('properties', {})
    geom = feat.get('geometry', {})
    coords = geom.get('coordinates', [None, None])

    # De-duplicate by OSM ID if present
    feat_id = feat.get('id') or props.get('@id')
    if feat_id:
        if feat_id in seen_ids:
            continue
        seen_ids.add(feat_id)

    if not isinstance(coords[0], (int, float)) or not isinstance(coords[1], (int, float)):
        continue

    lon, lat = float(coords[0]), float(coords[1])
    if not (110.0 <= lon <= 156.0 and -45.0 <= lat <= -9.0):
        continue

    name = props.get('name') or props.get('alt_name') or 'Unnamed Campsite'
    tourism = props.get('tourism', 'camp_site')
    brand = str(props.get('brand', ''))

    # Calculate individual facilities (0 or 1)
    has_power = 1 if props.get('power_supply') in ['yes', '15'] else 0
    has_water = 1 if props.get('drinking_water') == 'yes' or props.get('water_point') == 'yes' else 0
    has_toilet = 1 if props.get('toilets') == 'yes' or props.get('toilet') == 'yes' else 0
    has_shower = 1 if props.get('shower') in ['yes', 'hot'] else 0
    has_dump = 1 if props.get('sanitary_dump_station') in ['yes', 'customers'] else 0

    facility_score = has_power + has_water + has_toilet + has_shower + has_dump

    # Determine Fee / Price Tier
    fee_raw = str(props.get('fee', '')).lower()
    name_lower = name.lower()
    brand_lower = brand.lower()
    is_commercial = any(k in name_lower or k in brand_lower for k in [
        'big4', 'big 4', 'discovery', 'holiday park', 'tourist park', 'resort', 'caravan park'
    ])

    if fee_raw == 'no' or 'free' in name_lower or props.get('charge') in ['Free', 'free', 'Donation']:
        fee_tier = 'Free Bushcamp ($0)'
    elif is_commercial or fee_raw == 'yes' or tourism == 'caravan_site':
        fee_tier = 'Commercial Park ($25–$50+)'
    else:
        fee_tier = 'Free Bushcamp ($0)' if facility_score <= 1 else 'Commercial Park ($25–$50+)'

    state = determine_state(props, lon, lat)

    # Tooltip summary
    amenities = []
    if has_power: amenities.append('Power')
    if has_water: amenities.append('Drinking Water')
    if has_toilet: amenities.append('Toilets')
    if has_shower: amenities.append('Showers')
    if has_dump: amenities.append('Dump Station')
    amenities_str = ', '.join(amenities) if amenities else 'Self-Sufficient (None)'

    records.append({
        'name': name,
        'lon': round(lon, 4),
        'lat': round(lat, 4),
        'state': state,
        'site_type': 'Caravan Park' if tourism == 'caravan_site' else 'Campground / Bush Camp',
        'fee_tier': fee_tier,
        'facility_score': facility_score,
        'amenities': amenities_str
    })

# 4. Save to CSV
os.makedirs('data', exist_ok=True)
output_file = 'data/campsites_price_facilities.csv'
df = pd.DataFrame(records)
df.to_csv(output_file, index=False)
print(f"Done! Cleaned {len(df)} campsites into '{output_file}'.")