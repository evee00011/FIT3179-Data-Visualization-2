import json
import os
import pandas as pd

# 1. Locate directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Find export.json
campsites_path = os.path.join(PROJECT_ROOT, 'datasets', 'export.json')
if not os.path.exists(campsites_path):
  campsites_path = os.path.join(PROJECT_ROOT, 'export.json')

print(f'Reading {campsites_path}...')
with open(campsites_path, 'r', encoding='utf-8') as f:
  geojson_data = json.load(f)


# 2. Robust State Determination
def determine_state(props, lon, lat):
  # Check explicit state tag first
  st = props.get('addr:state')
  if st:
    st_clean = st.strip().upper().replace('.', '')
    state_map = {
        'NEW SOUTH WALES': 'NSW',
        'VICTORIA': 'VIC',
        'QUEENSLAND': 'QLD',
        'WESTERN AUSTRALIA': 'WA',
        'SOUTH AUSTRALIA': 'SA',
        'TASMANIA': 'TAS',
        'NORTHERN TERRITORY': 'NT',
        'AUSTRALIAN CAPITAL TERRITORY': 'ACT',
    }
    if st_clean in [
        'NSW',
        'VIC',
        'QLD',
        'WA',
        'SA',
        'TAS',
        'NT',
        'ACT',
    ]:
      return st_clean
    if st_clean in state_map:
      return state_map[st_clean]

  # Check postcode prefix
  pc = props.get('addr:postcode')
  if pc:
    p_str = str(pc).strip()
    if len(p_str) == 4:
      if p_str.startswith('2'):
        return 'ACT' if p_str.startswith(('260', '261', '290', '291')) else 'NSW'
      if p_str.startswith('3'):
        return 'VIC'
      if p_str.startswith('4'):
        return 'QLD'
      if p_str.startswith('5'):
        return 'SA'
      if p_str.startswith('6'):
        return 'WA'
      if p_str.startswith('7'):
        return 'TAS'
      if p_str.startswith('0'):
        return 'NT'

  # Fallback to Geographic Coordinates
  if lon is not None and lat is not None:
    # Tasmania and Bass Strait islands
    if lat < -39.2:
      return 'TAS'
    # Western Australia (west of 129°E)
    if lon < 129.0:
      return 'WA'
    # Northern Territory vs South Australia (between 129°E and 138°E)
    if 129.0 <= lon < 138.0:
      return 'NT' if lat >= -26.0 else 'SA'
    # South Australia eastern border
    if 138.0 <= lon < 141.0:
      if lat < -26.0:
        return 'SA'
      return 'NT' if lon < 138.0 else 'QLD'
    # Eastern States (East of 141°E)
    if lon >= 141.0:
      if lat > -28.1:
        return 'QLD'
      # ACT bounding box
      if -35.95 <= lat <= -35.1 and 148.75 <= lon <= 149.4:
        return 'ACT'
      # Victoria vs NSW
      if lat <= -37.5:
        return 'VIC'
      if lat < -34.0 and lon < 148.0:
        return 'VIC' if lat < -35.8 else 'NSW'
      return 'NSW'

  return 'NSW'


# 3. Classify Campsite Type
def classify_type(props):
  tourism = props.get('tourism', '')
  power = props.get('power_supply') == 'yes'
  cabins = props.get('cabins') == 'yes'
  brand = bool(props.get('brand'))

  # Commercial/serviced holiday parks vs bush/basic campsites
  if tourism == 'caravan_site' or power or cabins or brand:
    return 'Fancy / Resort Parks'
  return 'Hardcore Bushcamps'


# 4. Process all features
records = []
for feat in geojson_data.get('features', []):
  props = feat.get('properties', {})
  geom = feat.get('geometry', {})
  coords = geom.get('coordinates', [None, None])
  lon, lat = coords[0], coords[1]

  state = determine_state(props, lon, lat)
  camp_type = classify_type(props)
  records.append({'state': state, 'type': camp_type})

df = pd.DataFrame(records)

# 5. Aggregate counts
summary = df.groupby(['state', 'type']).size().reset_index(name='count')

# Ensure full matrix of 8 states x 2 types
valid_states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']
valid_types = ['Hardcore Bushcamps', 'Fancy / Resort Parks']

grid = (
    pd.MultiIndex.from_product(
        [valid_states, valid_types], names=['state', 'type']
    )
    .to_frame()
    .reset_index(drop=True)
)
final_df = pd.merge(grid, summary, on=['state', 'type'], how='left').fillna(0)
final_df['count'] = final_df['count'].astype(int)

# 6. Save to CSV
output_csv = os.path.join(DATA_DIR, 'campsites_by_state_type.csv')
final_df.to_csv(output_csv, index=False)

print(f"Success! Generated '{output_csv}' with non-zero counts:")
print(final_df)