import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
import numpy as np
import sys,glob
from osgeo import gdal, gdalconst, ogr,osr
import pyproj
from rasterio.enums import Resampling

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
	with rasterio.open(outpath,'w', **kwargs) as dst:
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
	#说明目前的做法，可能导致边缘位置得到的空间分配因子偏高，请注意这个问题,将来应该判断各网格的面积和栅格面积的比值，排重新调整栅格值。
	dx = shpfile.bounds.maxx - shpfile.bounds.minx
	dy = shpfile.bounds.maxy - shpfile.bounds.miny 
	mindx = dx.mean()
	mindy = dy.mean()
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
	#print(output_ds.crs)
	output_ds = None
	if minres > x_res:
		print('resolution of raster is suitable')
		out_res = minres
	else:
		print('minres:'+str(minres)+' x_res:'+str(x_res))
		output_ds = resample_r(rasterio.open(outpath),minres*0.5,outpath)
#		print(output_ds.crs)
		out_res = minres*0.5
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
	raster_res = src.res
#	print(raster_data.shape)
	for i in range(0,len(gdf)):
		print("Extracking SA for target grid :{}%".format(100*i//len(gdf)),end="\r")
		mask = geometry_mask([gdf.geometry[i]], out_shape=raster_data.shape, transform=raster_transform, invert=True)
		gridarea = gdf.geometry[i].area
		ratio = min(1,gridarea/(raster_res[0]**2))
#		在这里增加一个面积判断！
		tmp=np.where(mask, 1, 0) *raster_data*ratio
		gdf.loc[i,indexname]= tmp.sum()



##########main ###########
def extractSA_raster_multi(shpfile_path,raster_path,lutype=[11,12]):
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
		timename = rasterlist[i].split('/')[-1][:-4]
		outpath = './tmp/tmpasc_'+timename+'.tiff'
		raster_ds = gdal.Open(raster, gdalconst.GA_ReadOnly)
		clip_ds=clipraster(gdf,raster_ds,outpath)
		src= rasterio.open(outpath) 
		sumval(gdf, src,timename,lutype,formattype)
	gdf.to_crs('epsg:4326')
	gdf.to_file('./output/'+casename)
	return gdf

def extractSA_r(shpfile_path,raster_path,varname,lutype=[11,12]):
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
	casename = 'SA_'+varname+shpfile_path.split('/')[-1]
	raster = rasterlist[0]
	outpath = './tmp/tmpasc_'+varname+'.tiff'
	raster_ds = gdal.Open(raster, gdalconst.GA_ReadOnly)
	clip_ds=clipraster(gdf,raster_ds,outpath)
	src= rasterio.open(outpath) 
	sumval(gdf, src,varname,lutype,formattype)
	gdf.to_crs('epsg:4326')
	gdf.to_file('./output/'+casename)
	return gdf

def CalrasterSA(target,com_region_contain,com_region_int,raster_path,inputinv,outname,poplist):
	targetshp = gpd.read_file(target)
	SA_intersect=extractSA_r(com_region_int,raster_path,'SA_INT')
	SA_total=extractSA_r(com_region_contain,raster_path,'SA_TOT')[['ID_left','SA_TOT']]
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
	targetshp = targetshp.merge(emisfinal,left_on='ID',right_on='ID_2',how='left')
	targetshp.fillna(0,inplace=True)
	targetshp.drop(columns=['ID_1','ID_2','Ratio'],inplace=True)
	#print(targetshp,SA_out)
	targetshp.to_file('./output/Emis_'+outname+'.shp')
	targetshp.drop(columns=['geometry'],inplace=True)
	targetshp.to_csv('./output/Emis_'+outname+'.csv')
