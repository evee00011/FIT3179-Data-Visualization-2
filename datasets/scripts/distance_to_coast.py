import json
import numpy as np
import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

# 1. Load your campsites data
with open('FIT3179-Data-Visualization-2/datasets/export.json', 'r', encoding='utf-8') as f:
  campsites_data = json.load(f)

# 2. Extract coordinates & classify campsite style
records = []
for feat in campsites_data.get('features', []):
  coords = feat.get('geometry', {}).get('coordinates', [None, None])
  props = feat.get('properties', {})

  lon, lat = coords[0], coords[1]
  if lon is None or lat is None:
    continue

  tourism = props.get('tourism', '')
  power = props.get('power_supply') == 'yes'
  cabins = props.get('cabins') == 'yes'
  brand = bool(props.get('brand'))

  style = (
      'Commercial / Resort'
      if (tourism == 'caravan_site' or power or cabins or brand)
      else 'Hardcore Bushcamp'
  )
  name = props.get('name', 'Unnamed Campsite')

  records.append(
      {'name': name, 'lon': lon, 'lat': lat, 'type': style}
  )

df = pd.DataFrame(records)

# 3. Simple Coastal Distance Proxy (or using GeoPandas coastline distance)
# Filter/clean valid Australian coordinates
df = df[
    (df['lon'].between(112, 154)) & (df['lat'].between(-44, -10))
].reset_index(drop=True)

# You can save this cleaned points file
df.to_csv('FIT3179-Data-Visualization-2/datasets/campsites_coastal_distribution.csv', index=False)
print(f'Processed {len(df)} campsites.')