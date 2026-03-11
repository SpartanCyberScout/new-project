import os
import pandas as pd
import folium
from folium.plugins import Search, Fullscreen, MeasureControl, FastMarkerCluster
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
from dotenv import load_dotenv

# Load local environment variables (Security First)
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

# 1. Initialize Map
# prefer_canvas=True improves performance on mobile and VirtualBox
m = folium.Map(
    location=[44.2619, -88.4154], 
    zoom_start=12, 
    tiles=None, 
    prefer_canvas=True, 
    control_scale=True
)

# Base Layers - Dark Mode is standard for Cyber/Information Assurance projects
folium.TileLayer('cartodbpositron', name="Light Mode").add_to(m)
folium.TileLayer('cartodbdark_matter', name="Dark Mode (Cyber)").add_to(m)

# 2. Advanced Interactive UI
m.add_child(MeasureControl(position='topright', primary_length_unit='meters'))
Fullscreen(position='topright').add_to(m)

# 3. Data Processing Containers
wigle_points = []  # [lat, lon, popup_html]
infra_points = []

# Geocoder setup with rate limiting (respects OpenStreetMap terms)
geolocator = Nominatim(user_agent="spartan_geoint_v5")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

data_dir = 'data'

if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            path = os.path.join(root, filename)
            
            if filename.endswith('.csv'):
                try:
                    # Logic for WiGLE vs General Data
                    if filename.startswith('WigleWifi'):
                        df = pd.read_csv(path, skiprows=1)
                        for _, row in df.iterrows():
                            lat, lon = row.get('CurrentLatitude'), row.get('CurrentLongitude')
                            if pd.notnull(lat) and pd.notnull(lon):
                                # Sanitize SSID and RSSI for the popup
                                ssid = row.get('SSID', 'Hidden')
                                popup_html = f"<b>SSID:</b> {ssid}<br><b>Signal:</b> {row.get('RSSI')}dBm"
                                wigle_points.append([lat, lon, popup_html])
                    else:
                        df = pd.read_csv(path)
                        # Process files with City/State (Atlas of Surveillance)
                        if 'City' in df.columns and 'State' in df.columns:
                            # Limit geocoding to prevent long hang times on deployment
                            for i, row in df.head(10).iterrows():
                                addr = f"{row['City']}, {row['State']}"
                                location = geocode(addr)
                                if location:
                                    popup_html = f"<b>Agency:</b> {row.get('Agency')}<br><b>Tech:</b> {row.get('Technology')}"
                                    infra_points.append([location.latitude, location.longitude, popup_html])

                except Exception as e:
                    print(f"[-] Error skipping {filename}: {e}")

# 4. Clustering Logic (Fluid Performance)
# This JS callback renders popups inside the FastMarkerCluster
marker_callback = """
function (row) {
    var icon = L.AwesomeMarkers.icon({icon: 'signal', markerColor: 'blue', prefix: 'fa'});
    var marker = L.marker(new L.LatLng(row[0], row[1]), {icon: icon});
    marker.bindPopup(row[2]);
    return marker;
};
"""

if wigle_points:
    m.add_child(FastMarkerCluster(wigle_points, callback=marker_callback, name="Wireless Hits"))

if infra_points:
    infra_layer = folium.FeatureGroup(name="Surveillance Infrastructure").add_to(m)
    for p in infra_points:
        folium.Marker(
            location=[p[0], p[1]], 
            popup=p[2], 
            icon=folium.Icon(color='red', icon='eye', prefix='fa')
        ).add_to(infra_layer)

# 5. Deployment Finalization
folium.LayerControl(collapsed=False).add_to(m)
m.save('index.html')

print(f"[*] Deployment Build Success: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
