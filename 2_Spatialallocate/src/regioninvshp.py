import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
from rasterio.transform import Affine
import xarray as xr
import sys
import numpy as np

def getdominfor(regioninv):
	filetype = regioninv.split('.')[-1]
	if filetype == 'asc':
		src = rasterio.open(regioninv)
		invaff = src.transform
		nx = src.shape[1]
		ny = src.shape[0]
	elif filetype == '.nc':
		nc = xr.open_dataset(regioninv)
		dxy = nc.spacing.values[0]
		x0 = nc.x_range.values[0]
		y0 = nc.y_range.values[0]
		nx = nc.dimension.values[0]
		ny = nc.dimension.values[1]
		invaff= Affine(dxy, 0.0, x0,0.0, -dxy, y0)
	else:
		print('uprocessing unvalid region file')
	return invaff,nx,ny

def makeshp(invaff,nx,ny,fname):
	domdata = np.random.rand(ny,nx)
	gdf = gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
	gdf['tmp']=domdata.flatten()
	results = list(shapes(domdata.astype(np.float32), transform=invaff))
	nums = len(results)
	for index, row in gdf.iterrows():
		gdf.loc[index, 'geometry'] = [shape(results[index][0])]
		gdf.loc[index,'ID'] = index
		print("Extracting domain :{}%".format(100*index//nums),end="\r")
	gdf['LON'] = gdf['geometry'].centroid.x
	gdf['LAT'] = gdf['geometry'].centroid.y
	gdfproj = gdf.to_crs('epsg:32650')
	gdf['AREA']= gdfproj['geometry'].area
	print("Calcualting LON,LAT and output")
	gdf.to_file(fname+'.shp')

regioninv=sys.argv[1]
invaff,nx,ny = getdominfor(regioninv)
makeshp(invaff,nx,ny,'./output/regioninv')

