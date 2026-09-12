import geopandas as gpd

# Load the shapefile and convert coordinates in one step
gdf = gpd.read_file("CamaSummary.shp").to_crs(epsg=4326)

# Get the center points (Latitude and Longitude)
gdf['Longitude'] = gdf.geometry.centroid.x
gdf['Latitude'] = gdf.geometry.centroid.y

# Drop the map shapes and save directly to CSV
gdf.drop(columns=['geometry']).to_csv("/Users/tej/Documents/Deepak Project/fort_bend_properties.csv", index=False)