from rasterio.enums import Resampling

import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
import numpy as np
import sys,glob
from osgeo import gdal, gdalconst, ogr,osr
import pyproj


def shpextent(gdf):
	extent = gdf.total_bounds
	xbuff = abs(extent[2] - extent[0])*0.1
	ybuff = abs(extent[3] - extent[1])*0.1
	xmin = extent[0] -xbuff
	ymin = extent[1] -ybuff
	xmax = extent[2] +xbuff
	ymax = extent[3] +ybuff
	print('makeing xbuff:' +str(xbuff) +'  ybuff: '+str(ybuff))
	return xmin,xmax,ymin,ymax

def resample_r(src,dst_res,outpath):
	dst_width = int(src.width * src.res[0] / dst_res)
	dst_height = int(src.height * src.res[1] / dst_res)
	kwargs = src.meta.copy()
	kwargs.update({
        'crs': src.crs,
        'transform': rasterio.Affine(dst_res, 0, src.transform[2], 0, -dst_res, src.transform[5]),
        'width': dst_width,
        'height': dst_height
    })
	with rasterio.open(outpath, 'w', **kwargs) as dst:
		for i in range(1, src.count + 1):
			rasterio.warp.reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=kwargs['transform'],
                dst_crs=kwargs['crs'],
                resampling=Resampling.nearest  # 使用双线性插值进行重采样
            )
	return dst


def getshpres(shpfile):
	dx = shpfile.bounds.maxx - shpfile.bounds.minx
	dy = shpfile.bounds.maxy - shpfile.bounds.miny
	mindx = dx.min()
	mindy = dy.min()
	if mindx > mindy:
		minres = mindy
	else:
		minres = mindy
	return minres 
	
def clipraster(shp,raster_ds,outpath):
	xmin, xmax, ymin, ymax = shpextent(shp)
	x_res = raster_ds.GetGeoTransform()[1]	
	y_res = raster_ds.GetGeoTransform()[5]
	x_pixels = int((xmax - xmin) / x_res)
	y_pixels = int((ymax - ymin) / abs(y_res))
	driver = gdal.GetDriverByName('GTiff') 
	output_ds = driver.Create(outpath, x_pixels, y_pixels, 1, gdal.GDT_Float32)
	output_ds.SetGeoTransform([xmin, x_res, 0, ymax, 0, y_res]) 
	output_ds.SetProjection(raster_ds.GetProjection())
	gdal.Warp(output_ds, raster_ds, outputBounds=[xmin, ymin, xmax, ymax])
	minres = getshpres(shp)
	output_ds = None
	if minres > x_res:
		print('resolution of raster is suitable')
	else:
		resample_r(rasterio.open(outpath),minres*0.8,outpath)
	output_ds = None
	return output_ds
	
def sumval(gdf, src,indexname,lutype,dstype):
	raster_data = src.read(1)
	if dstype == 2:
		nodatavalue= src.nodata
		raster_data[raster_data==nodatavalue]=0 
		raster_data[(raster_data<lutype[0])|(raster_data>lutype[1])]=0
		raster_data[(raster_data>=lutype[0])&(raster_data<=lutype[1])]=1 
	#	indexname = 'LU_'+str(lutype[0])+'_'+str(lutype[1])
	gdf[indexname] = 0.0
	raster_transform = src.transform
	for i in range(0,len(gdf)):
		print("Extracking SA for target grid :{}%".format(100*i//len(gdf)),end="\r")
		mask = geometry_mask([gdf.geometry[i]], out_shape=raster_data.shape, transform=raster_transform, invert=True)
		tmp=np.where(mask, 1, 0) *raster_data
		gdf.loc[i,indexname]= tmp.sum()



##########main ###########
def extractSA_r_m(shpfile_path,raster_path,varname,lutype=[11,12]):
	tmprasterlist = glob.glob(raster_path+'/*')
#	print(tmprasterlist)
	if any('.asc' in s for s in tmprasterlist):
		print('asc')
		formattype = 1
	elif any('.adf' in s for s in tmprasterlist):
		formattype = 2
	elif any('.tif' in s for s in tmprasterlist):
		formattype = 3
	else:
		print('Unknown raster')
	if formattype == 1:
		rasterlist = glob.glob(raster_path+'/*.asc')
	elif formattype ==2:
		rasterlist = [raster_path+'/w001001.adf']
	elif formattype == 3:
		rasterlist = glob.glob(raster_path+'/*.tif')

	SA_crs = rasterio.open(rasterlist[0]).crs
	if SA_crs is None:
		SA_crs = 'epsg:4326'
	gdf = gpd.read_file(shpfile_path).to_crs(SA_crs)
	casename = 'SA_'+shpfile_path.split('/')[-1]
	for i in range(0,len(rasterlist)) :
		raster = rasterlist[i]
		timename = varname+'_'+rasterlist[i].split('/')[-1][:-4]
		outpath = './tmp/tmpasc_'+timename+'.tiff'
		raster_ds = gdal.Open(raster, gdalconst.GA_ReadOnly)
		clip_ds=clipraster(gdf,raster_ds,outpath)
		src= rasterio.open(outpath) 
		sumval(gdf, src,timename,lutype,formattype)
	gdf.to_crs('epsg:4326')
	gdf.to_file('./output/'+casename)
	return gdf

def CalrasterSA_m(target,com_region_contain,com_region_int,raster_path,inputinv,outname):
	targetshp = gpd.read_file(target)
	SA_intersect=extractSA_r_m(com_region_int,raster_path,'SA_INT')
	SA_total=extractSA_r_m(com_region_contain,raster_path,'SA_TOT')
	SA_totaldf = SA_total.drop(columns=['geometry'])
	SA_out=SA_intersect.merge(SA_totaldf,how='inner',left_on='ID_1',right_on='ID_left')
	tmprasterlist = glob.glob(raster_path+'/*')
#       print(tmprasterlist)
	SA_out.to_file('./output/SA_Beforecorrect_'+outname+'.shp')
	if any('.asc' in s for s in tmprasterlist):
		print('asc')
		formattype = 1
	elif any('.adf' in s for s in tmprasterlist):
		formattype = 2
	elif any('.tif' in s for s in tmprasterlist):
		formattype = 3
	else:
		print('Unknown raster')
	if formattype == 1:
		rasterlist = glob.glob(raster_path+'/*.asc')
	elif formattype ==2:
		rasterlist = [raster_path+'/w001001.adf']
	elif formattype == 3:
		rasterlist = glob.glob(raster_path+'/*.tif')
#	corratio = pd.DataFrame()
	for i in range(0,len(rasterlist)):
		varname = rasterlist[i].split('/')[-1][:-4]
		var_int_name = 'SA_INT_'+rasterlist[i].split('/')[-1][:-4]
		var_tot_name = 'SA_TOT_'+rasterlist[i].split('/')[-1][:-4]
		SA_out['tmpRatio_'+varname] = SA_out[var_int_name]/(SA_out[var_tot_name])
		SA_out['tmpRatio_'+varname] = SA_out['tmpRatio_'+varname].fillna(0)

		corratiotmp = SA_out.groupby(['ID_1'])['tmpRatio_'+varname].sum().reset_index()
		corratiotmp['rationew_'+varname] = corratiotmp['tmpRatio_'+varname].apply(lambda x:1 if x<=1 else 1/x)
		if i == 0 :
#			corratiotmp.drop(columns=['tmpRatio_'+varname],inplace=True)
			corratio = corratiotmp[['ID_1','rationew_'+varname]]

			#print(corratio)
		else:
			corratio['rationew_'+varname] = corratiotmp['rationew_'+varname]
			#print(corratio)
	corratio.to_csv('corratio.csv')
#	print(SA_out.columns)
	SA_out = SA_out.merge(corratio)
#	print(corratio)
#	print(SA_out.columns)
	for i in range(0,len(rasterlist)):
		varname = rasterlist[i].split('/')[-1][:-4]
		SA_out['Ratio_'+varname] = SA_out['tmpRatio_'+varname]*SA_out['rationew_'+varname]
	print(SA_out)
	SA_out.to_file('./output/SA_Final_'+outname+'.shp')
