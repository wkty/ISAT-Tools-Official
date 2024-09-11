import geopandas as gpd
import numpy as np
import sys,glob
import pyproj
import pandas as pd
import geopandas as gpd

##########main ###########
def extractSA_l(regionpath,lineshppath,lineshpfile,lineref,varname,opt='yes'):
	profile = pd.read_csv(lineref)
	casename = 'SA_'+lineshppath.split('/')[-1][:-4]+'_'+varname+'_'+regionpath.split('/')[-1]
	regionfile = gpd.read_file(regionpath).to_crs('epsg:4326')
	regionfile['FID'] = pd.Series(range(len(regionfile)))
	com_region = gpd.overlay(regionfile,lineshpfile,how="intersection",keep_geom_type=False).to_crs('epsg:32650')
	com_region['length'] = com_region.length
	line_region=com_region.merge(profile,left_on='fclass',right_on='Type',how='left')
	line_region[varname]=line_region['length']*line_region['Weight']
	sa_line = line_region.groupby(['FID'])[varname].sum().reset_index()
	sa_output = regionfile.merge(sa_line,how='left')
	if opt == 'yes':
		sa_output.to_file('./tmp/'+casename)
	else:
		print('The line SA shpfile not saved ')
	return sa_output

################



def CallineSA(target,com_region_contain,com_region_int,line_path,inputinv,outname,lineref,poplist):
	print('reading line shp')
	lineshpfile = gpd.read_file(line_path)
	print('line shp loaded')
	targetshp = gpd.read_file(target)
	SA_intersect=extractSA_l(com_region_int,line_path,lineshpfile,lineref,'SA_INT').fillna(0)
	SA_total=extractSA_l(com_region_contain,line_path,lineshpfile,lineref,'SA_TOT')[['ID_left','SA_TOT']].fillna(0)
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
	#print(targetshp,SA_out)
	targetshp.to_file('./output/Emis_'+outname+'.shp')
	targetshp.drop(columns=['geometry'],inplace=True)
	targetshp.to_csv('./output/Emis_'+outname+'.csv')
