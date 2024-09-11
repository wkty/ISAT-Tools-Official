import configparser
import sys
sys.path.insert(0,'.')
from src.ex_sa_raster import *
from src.ex_sa_line import *
from src.ex_sa_point import *
from src.ex_sa_area import *
config = configparser.ConfigParser()
config.read('par.ini')
########reading domains########
poplist=config['Domain']['poplist'].split(',')
target=config['Domain']['target']
region=config['Domain']['region']
targetshp = gpd.read_file(target).to_crs('EPSG:4326')
com_region_int_tmp = gpd.overlay(gpd.read_file(region).to_crs('EPSG:4326'),gpd.read_file(target).to_crs('EPSG:4326'), how='intersection')  #ID_left -region  #ID_right target
com_region_int='./tmp/regions_int_'+target.split('/')[-1][:-4]+region.split('/')[-1]
com_region_int_tmp.to_file(com_region_int)
com_region_contain_tmp = gpd.sjoin(gpd.read_file(region).to_crs('EPSG:4326'),gpd.read_file(target).to_crs('EPSG:4326'), how='inner', predicate='intersects').dissolve(['ID_left'])
 #ID_left -region  #ID_right target#
com_region_contain='./tmp/regions_contain_'+target.split('/')[-1][:-4]+region.split('/')[-1]
com_region_contain_tmp.to_file(com_region_contain)
########### Raster ##########################
print('Running SA based on Raster data')
rasteron = config['R_Proxy']['raster_on']
rasterpath = config['R_Proxy']['rasterpath'].split(',')
inputinv_r = config['R_Proxy']['inputinv_r'].split(',')
outname_r = config['R_Proxy']['outname_r'].split(',')
if rasteron == 'True':
	if len(rasterpath) == 0 :
		print('No raster task need to run')
	else: 
		for i in range(0,len(rasterpath)):
			print('Running Raster SA task :' + outname_r[i])
			CalrasterSA(target,com_region_contain,com_region_int,rasterpath[i],inputinv_r[i],outname_r[i],poplist)
else:
	print('raster SA off')
##########Point ##############################
print('Runing SA based on point data')
pointon = config['P_Proxy']['point_on']
pointpath = config['P_Proxy']['pointpath'].split(',')
inputinv_p = config['P_Proxy']['inputinv_p'].split(',')
outname_p = config['P_Proxy']['outname_p'].split(',')
key = config['P_Proxy']['key'].split(',')
if pointon == 'True':
	if len(pointpath) == 0 :
		print('No raster task need to run')
	else:
		for i in range(0,len(pointpath)):
			print('Running Point SA task:'+outname_p[i])
			CalpointSA(targetshp,com_region_contain,com_region_int,pointpath[i],inputinv_p[i],outname_p[i],key[i],poplist)
else:
	print('point SA off')
########Line#################################
print('Runing SA based on line data')
lineon = config['L_Proxy']['line_on']
linepath = config['L_Proxy']['linepath'].split(',')
lineref = config['L_Proxy']['lineref'].split(',')
inputinv_l = config['L_Proxy']['inputinv_l'].split(',')
outname_l = config['L_Proxy']['outname_l'].split(',')
if lineon == 'True':
	if len(linepath) == 0 :
		print('No Lineshp task need to run')
	else:
		for i in range(0,len(linepath)):
			print('Running Line SA task:'+outname_l[i])
			CallineSA(target,com_region_contain,com_region_int,linepath[i],inputinv_l[i],outname_l[i],lineref[i],poplist)
else:
	print('line SA off')
##########Area#################################
print('Runing SA based on area')
area_on = config['A_Proxy']['area_on']
inputinv_a = config['A_Proxy']['inputinv_a'].split(',')
outname_a = config['A_Proxy']['outname_a'].split(',')
if area_on == 'True':
	if len(inputinv_a) == 0 :
		print('No AREA task need to run')
	else:
		for i in range(0,len(inputinv_a)):
			print('Running AREA SA task:'+outname_a[i])
			CalareaSA(targetshp,com_region_contain,com_region_int,inputinv_a[i],outname_a[i],poplist)
else:
	print('area SA off')
#out=extractSA('./tmp/intersect.shp',raster_path)

print('SA tasks finished')
