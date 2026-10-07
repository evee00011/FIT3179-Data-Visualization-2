import json
import pandas as pd  

# 1. Load GeoJSON
with open('export.json', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

features = geojson_data['features']
total_sites = len(features)

# 2. Extract properties
props = [feat['properties'] for feat in features]
df = pd.DataFrame(props)

# 3. Compute counts for site types and key amenities
summary = [
    {
        "category": "Caravan Sites",
        "count": int((df.get("tourism") == "caravan_site").sum()),
    },
    {
        "category": "Campgrounds / Bush Camps",
        "count": int((df.get("tourism") == "camp_site").sum()),
    },
    {
        "category": "Tent Camping Allowed",
        "count": int((df.get("tents") == "yes").sum()),
    },
    {
        "category": "Caravan Accessible",
        "count": int(
            (
                (df.get("caravans") == "yes") | (df.get("caravan") == "yes")
            ).sum()
        ),
    },
    {
        "category": "Power Supply Available",
        "count": int((df.get("power_supply") == "yes").sum()),
    },
    {
        "category": "Toilets Available",
        "count": int(
            ((df.get("toilets") == "yes") | (df.get("toilet") == "yes")).sum()
        ),
    },
    {
        "category": "Showers Available",
        "count": int((df.get("shower") == "yes").sum()),
    },
    {
        "category": "Drinking Water",
        "count": int((df.get("drinking_water") == "yes").sum()),
    },
    {
        "category": "Sanitary Dump Station",
        "count": int((df.get("sanitary_dump_station") == "yes").sum()),
    },
]

summary_df = pd.DataFrame(summary)
summary_df["percentage"] = (summary_df["count"] / total_sites * 100).round(1)

# Save to CSV for Vega-Lite
summary_df.to_csv("campsite_facilities_summary.csv", index=False)
print(summary_df)