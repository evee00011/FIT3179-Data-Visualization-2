import json
import math
import os
import pandas as pd

# Coordinates of the major capital cities
CITIES = {
    'Sydney': (151.2093, -33.8688),
    'Melbourne': (144.9631, -37.8136),
    'Brisbane': (153.0251, -27.4698),
    'Perth': (115.8605, -31.9505),
    'Adelaide': (138.6007, -34.9285),
    'Darwin': (130.8456, -12.4634),
    'Hobart': (147.3272, -42.8821),
    'Canberra': (149.1300, -35.2809)
}

def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Load your export.json
file_path = 'FIT3179-Data-Visualization-2/datasets/export.json'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    geojson_data = json.load(f)

records = []
for feat in geojson_data.get('features', []):
    props = feat.get('properties', {})
    coords = feat.get('geometry', {}).get('coordinates', [None, None])
    
    if not isinstance(coords[0], (int, float)) or not isinstance(coords[1], (int, float)):
        continue
    lon, lat = float(coords[0]), float(coords[1])
    
    if not (110.0 <= lon <= 156.0 and -45.0 <= lat <= -9.0):
        continue

    # Calculate distance to closest capital city
    min_dist = float('inf')
    closest_city = 'None'
    for city_name, (c_lon, c_lat) in CITIES.items():
        d = haversine_km(lon, lat, c_lon, c_lat)
        if d < min_dist:
            min_dist = d
            closest_city = city_name

    # Distance classification (Escape vs Isolation)
    if min_dist <= 50:
        proximity_tier = 'Near City / Fringe (<50 km)'
    elif min_dist <= 150:
        proximity_tier = 'Weekend Getaway (50-150 km)'
    else:
        proximity_tier = 'Wilderness Isolation (>150 km)'

    # Facility score
    has_power = 1 if props.get('power_supply') in ['yes', '15'] else 0
    has_water = 1 if props.get('drinking_water') == 'yes' else 0
    has_toilet = 1 if props.get('toilets') == 'yes' or props.get('toilet') == 'yes' else 0
    has_shower = 1 if props.get('shower') in ['yes', 'hot'] else 0
    has_dump = 1 if props.get('sanitary_dump_station') in ['yes', 'customers'] else 0
    facility_score = has_power + has_water + has_toilet + has_shower + has_dump

    fee_raw = str(props.get('fee', '')).lower()
    name = props.get('name') or props.get('alt_name') or 'Unnamed Campsite'
    is_free = (fee_raw == 'no') or ('free' in name.lower()) or (props.get('charge') in ['Free', 'free', 'Donation'])
    fee_tier = 'Free Bushcamp ($0)' if is_free else 'Commercial Park ($25-$50+)'

    records.append({
        'name': name,
        'lon': round(lon, 4),
        'lat': round(lat, 4),
        'dist_to_city_km': round(min_dist, 1),
        'closest_city': closest_city,
        'proximity_tier': proximity_tier,
        'facility_score': facility_score,
        'fee_tier': fee_tier
    })

os.makedirs('data', exist_ok=True)
df = pd.DataFrame(records)
df.to_csv('data/campsites_distance.csv', index=False)
print(f"Generated data/campsites_distance.csv with {len(df)} records.")