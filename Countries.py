import geopandas as gpd

def filter_and_save_countries(input_geopackage, output_geojson, countries_of_interest):
    """
    Filter countries from a GeoPackage based on a list of countries and save the result as GeoJSON.

    Parameters:
        input_geopackage (str): Path to the input GeoPackage file.
        output_geojson (str): Path to save the output GeoJSON file.
        countries_of_interest (list): List of countries to select.

    Returns:
        None
    """

    countries_of_interest = ['Indonesia', 'Philippines', 'Malaysia', 'Thailand', 'Myanmar', 'East Timor', 'Vietnam', 'Singapore']

    # Read the GeoPackage into a GeoDataFrame
    #input_geopackage = ""
    gdf = gpd.read_file(input_geopackage)

    # Filter the GeoDataFrame based on the 'SOVEREIGN1' column
    selected_gdf = gdf[gdf['SOVEREIGN1'].isin(countries_of_interest)]

    # Save the selected GeoDataFrame as GeoJSON
    selected_gdf.to_file(output_geojson, driver='GeoJSON')
    output_geojson = "Data\Boundaries\selected_boundaries.geojson"

    print(f"Filtered countries saved to {output_geojson}")
    print(selected_gdf)

# Example usage:
input_geopackage = "Data\Boundaries\Boundaries.gpkg" 
output_geojson = "Data\Boundaries\selected_boundaries.geojson"
countries_of_interest = ['Indonesia', 'Philippines', 'Malaysia', 'Thailand', 'Myanmar', 'East Timor', 'Vietnam', 'Singapore']

filter_and_save_countries(input_geopackage, output_geojson, countries_of_interest)



