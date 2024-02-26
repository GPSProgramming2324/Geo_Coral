# %%
import requests
import xarray as xr
import os
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


# %%
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
folder = 'GeoCoral'
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


# %%

current_date = datetime.now()
two = current_date - timedelta(days=2)
date_two = two.strftime('%Y-%m-%d')
link="https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?CRW_DHW%5B("+date_two+"T12:00:00Z):1:("+date_two+"T12:00:00Z)%5D%5B(-24):1:(20)%5D%5B(89):1:(172)%5D,CRW_SST%5B("+date_two+"T12:00:00Z):1:("+date_two+"T12:00:00Z)%5D%5B(-24):1:(20)%5D%5B(89):1:(172)%5D"
#link= "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?CRW_DHW%5B("+date_two+"T12:00:00Z):1:(2024-02-15T12:00:00Z)%5D%5B(-24.0):1:(20.0)%5D%5B(89.0):1:(172.0)%5D"
response = requests.get(link)
print(response)

# %%
#Opening NetCDF
dataset = xr.open_dataset(response.content)
dhw = dataset['CRW_DHW'][0].values
lats = dataset['latitude'].values
lons = dataset['longitude'].values

dataset_b = xr.open_dataset(response.content)
sst = dataset['CRW_SST'][0].values
lats = dataset['latitude'].values
lons = dataset['longitude'].values



# %%


# Replace this with the actual bounding box you want
target_bbox = {
    'minx': 89,
    'miny': 64,
    'maxx': 172,
    'maxy': 20
}

tiff_name = new_folder_path+"/DHW_"+date_two+".tif"
print(tiff_name)
height, width = dhw.shape

transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                        (target_bbox['maxx'] - target_bbox['minx']) / width,
                        (target_bbox['miny'] - target_bbox['maxy']) / height)

with rasterio.open(tiff_name, 'w', driver='GTiff', height=height, width=width, count=1,
                   dtype=str(dhw.dtype), crs=4326, transform=transform) as dst:
    dst.write(dhw, 1)


tiff_name_b = new_folder_path+"/SST_"+date_two+".tif"
print(tiff_name_b)
height, width = sst.shape

transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                        (target_bbox['maxx'] - target_bbox['minx']) / width,
                        (target_bbox['miny'] - target_bbox['maxy']) / height)

with rasterio.open(tiff_name_b, 'w', driver='GTiff', height=height, width=width, count=1,
                   dtype=str(sst.dtype), crs=4326, transform=transform) as dst:
    dst.write(sst, 1)

#you're now going into the database
shapefile_path = new_folder_path + '/Corals.geojson'
print(shapefile_path)
gdf = gpd.read_file(shapefile_path)
print(gdf)
new_connection = psycopg2.connect(database = "geocoral" ,user = "postgres", 
                                  password = "postgres", host = "localhost", port = "5432")
new_connection.autocommit = True
cursor = new_connection.cursor()

from shapely.wkt import dumps
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
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape, mapping  # Import the 'shape' function
from shapely.wkt import dumps
import numpy as np
import pandas as pd

def buffer_polygon(geometry, buffer_distance):
    polygon = shape(geometry)
    buffered_polygon = polygon.buffer(buffer_distance)
    return buffered_polygon

shapefile_path = new_folder_path + '/Corals.geojson'
gdf = gpd.read_file(shapefile_path)

# Create an empty list to store the results
results = []
buffer_distance= 0.025
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



import pandas as pd
csv_file_path = new_folder_path + '/database.csv'
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
from datetime import datetime

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


