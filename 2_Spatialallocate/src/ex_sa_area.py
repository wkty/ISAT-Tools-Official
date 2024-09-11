import geopandas as gpd
import numpy as np
import sys,glob
import pyproj
import pandas as pd
import geopandas as gpd

def CalareaSA(targetshp,com_region_contain,com_region_int,inputinv,outname,poplist):
	SA_intersect= gpd.read_file(com_region_int).to_crs('EPSG:32650')
	SA_totaltmp = gpd.read_file(com_region_contain).to_crs('EPSG:32650')
	SA_intersect['SA_INT']= SA_intersect['geometry'].area
	SA_totaltmp['SA_TOT']= SA_totaltmp['geometry'].area
#	print(SA_totaltmp.columns)
	SA_total=SA_totaltmp[['ID_left','SA_TOT']]
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
	emisinv = pd.read_csv(inputinv)
#	poplist = emisinv.columns[5:]
	Emistmp = SA_final.merge(emisinv,left_on='ID_1',right_on='ID')
	for i in range(0,len(poplist)):
		SA_final[poplist[i]] = SA_final['Ratio']*Emistmp[poplist[i]]
	emisfinal = SA_final.groupby('ID_2').sum().reset_index()
	targetshp = targetshp.merge(emisfinal,left_on='ID',right_on='ID_2',how='left')
	targetshp.fillna(0,inplace=True)
	targetshp.drop(columns=['ID_1','ID_2','Ratio'],inplace=True)
	targetshp.to_file('./output/Emis_'+outname+'.shp')
	targetshp.drop(columns=['geometry'],inplace=True)
	targetshp.to_csv('./output/Emis_'+outname+'.csv')
