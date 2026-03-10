import os
import pandas as pd
import folium
from dotenv import load_dotenv

# Load your API keys from the .env file
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

# Initialize the map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# 1. Process local CSV files from your /data folder
data_dir = 'data'
if os.path.exists(data_dir):
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            try:
                path = os.path.join(data_dir, filename)
                df = pd.read_csv(path)
                for index, row in df.iterrows():
                    # Standardizing coordinate lookup
                    lat = row.get('latitude') or row.get('lat') or row.get('LAT')
                    lon = row.get('longitude') or row.get('lon') or row.get('long') or row.get('LON')

                    if pd.notnull(lat) and pd.notnull(lon):
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"Source: {filename}",
                            icon=folium.Icon(color='blue')
                        ).add_to(m)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# 2. Process a remote CSV from GitHub (Uncomment and replace URL when ready)
# remote_url = "https://raw.githubusercontent.com/User/Repo/main/data.csv"
# try:
#     remote_df = pd.read_csv(remote_url)
#     for index, row in remote_df.iterrows():
#         folium.Marker(
#             location=[row['latitude'], row['longitude']],
#             popup="Remote Data",
#             icon=folium.Icon(color='red')
#         ).add_to(m)
# except Exception as e:
#     print(f"Note: Remote data not loaded. (Check the URL in map.py)")

# Save the final map
m.save('index.html')
print("Success! Map has been generated as index.html")
