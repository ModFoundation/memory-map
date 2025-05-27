import streamlit as st
import pandas as pd
import os
import base64
import requests
from PIL import Image
from io import BytesIO
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Memory Map: Geotagged Images with Thumbnails")

# Load CSV
csv_path = "geotag_test_csv.csv"
df = pd.read_csv(csv_path)

# Thumbnail directory
thumbnail_dir = "thumbnails"
os.makedirs(thumbnail_dir, exist_ok=True)

# Function to download and create thumbnail
def create_thumbnail(url, output_path, size=(128, 128)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Error creating thumbnail for {url}: {e}")
        return False

# Generate thumbnails if not already done
df['thumbnail_path'] = None
for index, row in df.iterrows():
    image_url = row['word_presslink']
    if pd.notnull(image_url):
        image_name = row['image_name']
        thumbnail_filename = f"{image_name}_thumbnail.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        if not os.path.exists(thumbnail_path):  # Avoid redownloading
            if create_thumbnail(image_url, thumbnail_path):
                df.loc[index, 'thumbnail_path'] = thumbnail_path
        else:
            df.loc[index, 'thumbnail_path'] = thumbnail_path

# Create the map
m = leafmap.Map(center=[12.9716, 77.5946], zoom=12)

# Create popup HTML with embedded thumbnail
def create_popup_html(row):
    image_name = row['image_name']
    thumbnail_path = row['thumbnail_path']
    if pd.notnull(thumbnail_path) and os.path.exists(thumbnail_path):
        with open(thumbnail_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        return f'<b>{image_name}</b><br><img src="data:image/jpeg;base64,{encoded_string}" width="100">'
    else:
        return f'<b>{image_name}</b><br>No thumbnail available'

# Add markers
for index, row in df.iterrows():
    if pd.notnull(row['lat']) and pd.notnull(row['lomg']):
        m.add_marker(
            location=(row['lat'], row['lomg']),
            popup=create_popup_html(row),
            tooltip=row['image_name']
        )

# Display the map in Streamlit
m.to_streamlit(height=700)

