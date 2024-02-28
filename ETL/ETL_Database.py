import os
import requests
import xarray as xr
import gdown
import zipfile
import rasterio
from datetime import datetime, timedelta
import geopandas as gpd
from shapely.geometry import box
from shapely.wkt import dumps
import netCDF4 as nc
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject, Resampling
import psycopg2
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape, mapping 
from shapely.wkt import dumps
import numpy as np
import pandas as pd
from shapely.wkt import dumps
from datetime import datetime
import folium
import json


# %%
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
folder = 'Geocoral'
new_folder_path = os.path.join(desktop, folder)
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f"Folder '{folder}' created successfully at {desktop}")
else:
    print(f"Folder '{folder}' already exists at {desktop}")

# %%
def download_file_from_google_drive(file_id, dest_path):
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, dest_path, quiet=False)

def extract_zip(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

file_id = '1vhB18xV4v-DK634o85Ax_GH1FFwnieN4'
zip_destination = 'Corals.zip'
download_file_from_google_drive(file_id, zip_destination)
extraction_folder = new_folder_path
if not os.path.exists(extraction_folder):
    os.makedirs(extraction_folder)
extract_zip(zip_destination, extraction_folder)

# Builds the API call for NOOA

current_date = datetime.now()
two = current_date - timedelta(days=2)
date_two = two.strftime('%Y-%m-%d')
link = ("https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?"
        f"CRW_DHW%5B({date_two}T12:00:00Z):1:({date_two}T12:00:00Z)%5D%5B(-24):1:(20)%5D%5B(89):1:(172)%5D,"
        f"CRW_SST%5B({date_two}T12:00:00Z):1:({date_two}T12:00:00Z)%5D%5B(-24):1:(20)%5D%5B(89):1:(172)%5D")
print("Links for NOOA's API")
print(link)
response = requests.get(link)
print(response)

# %%
# Opening the measurements for Degree heat week 
dataset = xr.open_dataset(response.content)
dhw = dataset['CRW_DHW'][0].values
lats = dataset['latitude'].values
lons = dataset['longitude'].values

#this module separates the measurements for Sea surface temperature
dataset_b = xr.open_dataset(response.content)
sst = dataset['CRW_SST'][0].values
lats = dataset['latitude'].values
lons = dataset['longitude'].values

# %%


# Bounding box to mask raster
target_bbox = {
    'minx': 89,
    'miny': 64,
    'maxx': 172,
    'maxy': 20
}

tiff_name = os.path.join(new_folder_path, "DHW_" + date_two + ".tif")
print(tiff_name)
print("files have been created")
height, width = dhw.shape

transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                        (target_bbox['maxx'] - target_bbox['minx']) / width,
                        (target_bbox['miny'] - target_bbox['maxy']) / height)

with rasterio.open(tiff_name, 'w', driver='GTiff', height=height, width=width, count=1,
                   dtype=str(dhw.dtype), crs=4326, transform=transform) as dst:
    dst.write(dhw, 1)

tiff_name_b = os.path.join(new_folder_path, "SST_" + date_two + ".tif")
print(tiff_name_b)
height, width = sst.shape

transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                        (target_bbox['maxx'] - target_bbox['minx']) / width,
                        (target_bbox['miny'] - target_bbox['maxy']) / height)

with rasterio.open(tiff_name_b, 'w', driver='GTiff', height=height, width=width, count=1,
                   dtype=str(sst.dtype), crs=4326, transform=transform) as dst:
    dst.write(sst, 1)

# You're now going into the database
shapefile_path = os.path.join(new_folder_path, 'Corals.geojson')
print(shapefile_path)
gdf = gpd.read_file(shapefile_path)
print(gdf)
new_connection = psycopg2.connect(database="geocoral", user="postgres",
                                  password="postgres", host="localhost", port="5432")
new_connection.autocommit = True
cursor = new_connection.cursor()

for index, row in gdf.iterrows():
    geom_wkt = dumps(row['geometry'])
    idc_value = row['Idc']
    insert_query = (
        "INSERT INTO coral (id, geometry) VALUES (%s, ST_GeomFromText(%s, 4326))"
    )
    cursor.execute(insert_query, (row['Idc'], geom_wkt))

new_connection.commit()
cursor.close()
new_connection.close()

# %%

def buffer_polygon(geometry, buffer_distance):
    polygon = shape(geometry)
    buffered_polygon = polygon.buffer(buffer_distance)
    return buffered_polygon

shapefile_path = os.path.join(new_folder_path, 'Corals.geojson')
gdf = gpd.read_file(shapefile_path)

# Create an empty list to store the results
results = []
buffer_distance = 0.025
# Open both rasters at the same time
with rasterio.open(tiff_name) as src1, rasterio.open(tiff_name_b) as src2:
    # Create an iterator for both features in parallel
    for index, row in gdf.iterrows():
        # Access and print the 'Idc' field
        idc_value = row['Idc']

        # Access the geometry
        geometry = row['geometry']

        # Convert the geometry to WKT for printing or further use if needed
        geom_wkt = dumps(geometry)

        # Buffer the geometry if needed
        buffered_geometry = buffer_polygon(geometry, buffer_distance)

        # Masking for the first raster
        out_image_1, _ = mask(src1, [buffered_geometry], crop=True)
        average_value = np.nanmax(out_image_1)

        # Masking for the second raster
        out_image_2, _ = mask(src2, [buffered_geometry], crop=True)
        average_value_b = np.nanmax(out_image_2)

        # Append the results to the list
        results.append({
            'Coral_ID': idc_value,
            'DHW': average_value,
            'SST': average_value_b,
            'Date': date_two
        })

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(results)
print(df)

new_connection_b = psycopg2.connect(
    database="geocoral",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
new_connection_b.autocommit = True
cursor_b = new_connection_b.cursor()

for index, row in df.iterrows():
    coral = row['Coral_ID']
    date_formatted = row['Date']
    sst = row['SST']
    DHW = row['DHW']

    insert_query = "INSERT INTO temperature (coral_id, date, temperature, dhw) VALUES (%s, %s, %s,%s)"
    cursor_b.execute(insert_query, (coral, date_formatted, sst, DHW))

# Commit changes and close the connection
new_connection_b.commit()
cursor_b.close()
new_connection_b.close()


csv_file_path = os.path.join(new_folder_path, 'database.csv')
df_b = pd.read_csv(csv_file_path, delimiter=';')

new_connection_c = psycopg2.connect(
    database="geocoral",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
new_connection_c.autocommit = True
cursor_c = new_connection_c.cursor()


for index, row in df_b.iterrows():
    coral_b = row['IDC']
    date_str_b = row['Date']
    sst_b = row['SST']
    DHW_b = row['DHW']

    # Convert the date string to the correct format
    date_formatted_b = datetime.strptime(date_str_b, '%d/%m/%Y').strftime('%Y-%m-%d')

    insert_query = "INSERT INTO temperature (coral_id, date, temperature, dhw) VALUES (%s, %s, %s, %s)"
    cursor_c.execute(insert_query, (coral_b, date_formatted_b, sst_b, DHW_b))

# Commit changes and close the connection
new_connection_c.commit()
cursor_c.close()
new_connection_c.close()

new_connection_d = psycopg2.connect(database='geocoral', user="postgres", password="postgres", host="localhost", port="5432")
new_connection_d.autocommit = True
cursor_d = new_connection_d.cursor()

# Example query to fetch temperature data along with coral geometries
temperature_query = """
SELECT t.ID, t.Coral_ID, t.Date, t.Temperature, t.DHW, ST_AsGeoJSON(c.Geometry) 
FROM Temperature t
JOIN Coral c ON t.Coral_ID = c.ID
WHERE t.Temperature > 30 AND t.DHW > 3;
"""

cursor_d.execute(temperature_query)

temperature_data = cursor_d.fetchall()

if not temperature_data:
    print("No temperature data found for the given conditions")
else:
    result_list = [{
        'ID': data[0],
        'Coral_ID': data[1],
        'Date': data[2].strftime("%Y-%m-%d"),
        'Temperature': data[3],
        'DHW': data[4],
        'Geometry': json.loads(data[5])  
    } for data in temperature_data]

    # Create Folium map centered around Indonesia with a dark background
    m = folium.Map(location=[-7.5489, 131.0149], zoom_start=10, tiles='CartoDB dark_matter')

    for result in result_list:
        folium.GeoJson(
            result['Geometry'],
            name=f"Coral_{result['Coral_ID']}",
            tooltip=f"Coral ID: {result['Coral_ID']}, Temperature: {result['Temperature']}, Date: {result['Date']}, DHW: {result['DHW']}"
        ).add_to(m)

    # Save the map to an HTML file on the desktop
    m.save(os.path.join(new_folder_path, 'Corals.html'))

# Close the database connection
cursor_d.close()
new_connection_d.close()