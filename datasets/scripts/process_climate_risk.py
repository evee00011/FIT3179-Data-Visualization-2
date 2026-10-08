import json
import os
import pandas as pd

# -------------------------------------------------------------
# 1. SETUP PATHS
# -------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Locate export.json
candidates = [
    os.path.join(PROJECT_ROOT, 'datasets', 'export.json'),
    os.path.join(PROJECT_ROOT, 'export.json'),
    'datasets/export.json',
    'export.json'
]

json_path = None
for p in candidates:
    if os.path.exists(p):
        json_path = p
        break

if not json_path:
    raise FileNotFoundError("Could not find export.json. Please ensure it is in the project folder or datasets/.")

print(f"Reading campsite data from: {json_path}")
with open(json_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# -------------------------------------------------------------
# 2. STATE DETERMINATION FUNCTION
# -------------------------------------------------------------
def get_state(props, lon, lat):
    st = props.get('addr:state')
    if st:
        st_clean = st.strip().upper().replace('.', '')
        valid = {'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT'}
        if st_clean in valid:
            return st_clean
        name_map = {
            'NEW SOUTH WALES': 'NSW', 'VICTORIA': 'VIC', 'QUEENSLAND': 'QLD',
            'WESTERN AUSTRALIA': 'WA', 'SOUTH AUSTRALIA': 'SA', 'TASMANIA': 'TAS',
            'NORTHERN TERRITORY': 'NT', 'AUSTRALIAN CAPITAL TERRITORY': 'ACT'
        }
        if st_clean in name_map:
            return name_map[st_clean]

    # Postcode heuristic
    pc = props.get('addr:postcode')
    if pc and len(str(pc).strip()) == 4:
        p_str = str(pc).strip()
        if p_str.startswith('2'):
            return 'ACT' if p_str.startswith(('260', '261', '290', '291')) else 'NSW'
        if p_str.startswith('3'): return 'VIC'
        if p_str.startswith('4'): return 'QLD'
        if p_str.startswith('5'): return 'SA'
        if p_str.startswith('6'): return 'WA'
        if p_str.startswith('7'): return 'TAS'
        if p_str.startswith('0'): return 'NT'

    # Coordinate boundary fallback
    if lon is not None and lat is not None:
        if lat < -39.2: return 'TAS'
        if lon < 129.0: return 'WA'
        if 129.0 <= lon < 138.0:
            return 'NT' if lat >= -26.0 else 'SA'
        if 138.0 <= lon < 141.0:
            return 'SA' if lat < -26.0 else ('NT' if lon < 138.0 else 'QLD')
        if lon >= 141.0:
            if lat > -28.1: return 'QLD'
            if -35.95 <= lat <= -35.1 and 148.75 <= lon <= 149.4: return 'ACT'
            if lat <= -37.5: return 'VIC'
            if lat < -34.0 and lon < 148.0:
                return 'VIC' if lat < -35.8 else 'NSW'
            return 'NSW'

    return 'NSW'

# -------------------------------------------------------------
# 3. CAMPSITE CLASSIFICATION FUNCTION
# -------------------------------------------------------------
def classify_style(props):
    tourism = props.get('tourism', '')
    power = props.get('power_supply') == 'yes'
    cabins = props.get('cabins') == 'yes'
    brand = bool(props.get('brand'))
    if tourism == 'caravan_site' or power or cabins or brand:
        return 'Fancy / Resort Parks'
    return 'Hardcore Bushcamps'

# -------------------------------------------------------------
# 4. CLIMATE HAZARD & DISPLACEMENT LOGIC (BOM / AFAC Baselines)
# -------------------------------------------------------------
def assign_climate_profile(state, lon, lat):
    """
    Evaluates seasonal climate risks:
      - Top End / Tropical Monsoons (Lat > -20.0 or NT/Far North QLD/Kimberley)
      - Southern Temperate Bushfire Belt (VIC, NSW, TAS, ACT, Southern SA/WA)
      - Arid Outback Interior
    """
    # 1. Tropical Top End (Monsoonal Wet Season vs. Winter Dry Season)
    if lat > -19.5 or (state == 'NT' and lat > -22.0) or (state == 'QLD' and lat > -20.0):
        summer_hazard = "Monsoon Flooding & River Swells"
        summer_status = "Inaccessible / Flooded Closures"
        winter_hazard = "Optimal Dry Season"
        winter_status = "Open / Prime Season"
        climate_zone = "Tropical Monsoonal"

    # 2. Central Arid Interior (Extreme Heatwave Zone)
    elif (lon < 140.0 and lon > 120.0 and -31.0 < lat <= -19.5):
        summer_hazard = "Extreme Heat (>42°C) & Flash Aridity"
        summer_status = "Severe Heat Warning / Self-Reliance Advised"
        winter_hazard = "Optimal Touring"
        winter_status = "Open / Clear Days"
        climate_zone = "Arid Interior"

    # 3. Southern Temperate Bushfire Frontline (VIC, NSW, ACT, SA South, WA South-West)
    elif state in ['VIC', 'ACT', 'NSW', 'TAS'] or (state == 'WA' and lat <= -28.0) or (state == 'SA' and lat <= -30.0):
        # Coastal & Dense Eucalyptus Biomes in Summer
        summer_hazard = "Total Fire Ban & Wildfire Risk"
        summer_status = "Peak Demand / Fire Ban Enforced"
        
        # Winter Conditions
        if state == 'TAS' or lat < -36.5:
            winter_hazard = "Cold & Rainy / Frost Risk"
            winter_status = "Open / Low Demand"
        else:
            winter_hazard = "Mild & Sunny"
            winter_status = "Open"
        climate_zone = "Southern Temperate"

    # 4. Subtropical East Coast (Southern & Central QLD)
    else:
        summer_hazard = "Severe Summer Storms & Humid Swells"
        summer_status = "Open / Monitor Weather Alerts"
        winter_hazard = "Mild & Sunny"
        winter_status = "Open / High Demand"
        climate_zone = "Subtropical"

    return summer_hazard, winter_hazard, summer_status, winter_status, climate_zone

# -------------------------------------------------------------
# 5. PARSE ALL FEATURES
# -------------------------------------------------------------
print("Processing features...")
records = []

for feat in raw_data.get('features', []):
    geom = feat.get('geometry', {})
    coords = geom.get('coordinates', [None, None])
    lon, lat = coords[0], coords[1]

    # Validate coordinate bounds for Australia
    if lon is None or lat is None or not (110 <= lon <= 155 and -45 <= lat <= -9):
        continue

    props = feat.get('properties', {})
    campsite_name = props.get('name') or props.get('brand') or 'Unnamed Campsite'
    state = get_state(props, lon, lat)
    campsite_type = classify_style(props)
    
    s_haz, w_haz, s_stat, w_stat, czone = assign_climate_profile(state, lon, lat)

    records.append({
        'name': campsite_name,
        'state': state,
        'lon': round(lon, 4),
        'lat': round(lat, 4),
        'campsite_type': campsite_type,
        'climate_zone': czone,
        'summer_hazard': s_haz,
        'winter_hazard': w_haz,
        'summer_status': s_stat,
        'winter_status': w_stat
    })

df = pd.DataFrame(records)

# -------------------------------------------------------------
# 6. EXPORT TO CSV
# -------------------------------------------------------------
output_file = os.path.join(DATA_DIR, 'campsites_climate_risk.csv')
df.to_csv(output_file, index=False)

print(f"\nSuccessfully processed {len(df):,} Australian campsites!")
print(f"Saved to: {output_file}")
print("\nSample records:")
print(df[['name', 'state', 'climate_zone', 'summer_hazard', 'summer_status']].head(6))