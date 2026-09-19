import geopandas as gpd

# Load the shapefile and convert to lat and long
gdf = gpd.read_file("CamaSummary.shp").to_crs(epsg=4326)

# Get lat and long
gdf['Longitude'] = gdf.geometry.centroid.x
gdf['Latitude'] = gdf.geometry.centroid.y

# Get rid of geometry and save as CSV
gdf.drop(columns=['geometry']).to_csv("/Users/tej/Documents/Deepak Project/fort_bend_properties.csv", index=False)
