import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
import numpy as np
import sys,glob
from osgeo import gdal, gdalconst, ogr,osr
import pyproj
import pandas as pd
from shapely.geometry import Point

def makepointshp(incsv,keyname):
	data = pd.read_csv(incsv)
	geometry = [Point(xy) for xy in zip(data['LON'], data['LAT'])]
	gdf = gpd.GeoDataFrame(data, geometry=geometry)
	gdf.crs = "EPSG:4326"  
	gdf[keyname] =1
	if keyname in data.columns:
		gdf[keyname]=data[keyname]
	return gdf

##########main ###########
def extractSA_p(shpfile_path,csv_path,varname,keyname='Value',opt='yes'):
	pointfile = makepointshp(csv_path,keyname)
	regionfile= gpd.read_file(shpfile_path).to_crs('EPSG:4326')
	regionfile['FID'] = pd.Series(range(len(regionfile)))
	casename = 'SA_'+csv_path.split('/')[-1][:-4]+'_'+shpfile_path.split('/')[-1]
	com_region = gpd.sjoin(regionfile,pointfile,how="inner")
	sa_point = com_region.groupby(['FID'])[keyname].sum().reset_index()
	sa_output = regionfile.merge(sa_point,how='left')
	sa_output[varname] = sa_output[keyname]
	if opt == 'yes':
		sa_output.to_file('./tmp/'+casename)
	else:
		print('The line SA shpfile not saved ')
	return sa_output

################
def CalpointSA(targetshp,com_region_contain,com_region_int,point_path,inputinv,outname,keyname,poplist):
	SA_intersect=extractSA_p(com_region_int,point_path,'SA_INT',keyname).fillna(0)
	SA_total=extractSA_p(com_region_contain,point_path,'SA_TOT',keyname)[['ID_left','SA_TOT']].fillna(0)
	SA_out=SA_intersect.merge(SA_total,left_on='ID_1',right_on='ID_left')
	SA_out['tmpRatio'] = SA_out['SA_INT']/(SA_out['SA_TOT'])
	SA_out['tmpRatio'] = SA_out['tmpRatio'].fillna(0)
	corratio = SA_out.groupby(['ID_1'])['tmpRatio'].sum().reset_index()
	corratio['rationew'] = corratio['tmpRatio'].apply(lambda x:1 if x<=1 else 1/x)
	corratio.drop(columns=['tmpRatio'],inplace=True)
	SA_out = SA_out.merge(corratio)
	SA_out['Ratio'] = SA_out['tmpRatio']*SA_out['rationew']
	SA_final = SA_out[['ID_1','ID_2','Ratio','geometry']]
	SA_final.to_file('./output/SA_Final_'+outname+'.shp')
	emisinv = pd.read_csv(inputinv,encoding='gbk')
#	poplist = emisinv.columns[5:]
	Emistmp = SA_final.merge(emisinv,left_on='ID_1',right_on='ID')
	for i in range(0,len(poplist)):
		SA_final[poplist[i]] = SA_final['Ratio']*Emistmp[poplist[i]]
	emisfinal = SA_final.groupby('ID_2').sum().reset_index()
	targetout = targetshp.merge(emisfinal,left_on='ID',right_on='ID_2',how='left')
	targetout.fillna(0,inplace=True)
	targetout.drop(columns=['ID_1','ID_2','Ratio'],inplace=True)
	targetout.to_file('./output/Emis_'+outname+'.shp')
	targetout.drop(columns=['geometry'],inplace=True)
	targetout.to_csv('./output/Emis_'+outname+'.csv')
