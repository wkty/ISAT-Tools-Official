import configparser
import geopandas as gpd
import pandas as pd
import shapely
import numpy as np
import time 
def findcent(latin1,latin2,shpath):
    shpd01 = gpd.read_file(shpath)
    print(latin1,latin2,shpath,shpd01)
    lon01tmp = shpd01.to_crs('EPSG:32650').centroid.x[0]

    lat01tmp = shpd01.to_crs('EPSG:32650').centroid.y[0]
    gdft = gpd.GeoDataFrame({'point':['center'],'geometry':[shapely.geometry.Point(lon01tmp,lat01tmp)]},crs='EPSG:32650')
    lon01 = gdft.to_crs(epsg=4326)['geometry'].x[0]
    lat01 = gdft.to_crs(epsg=4326)['geometry'].y[0]
    ind = 1
    shpd02=shpd01.to_crs('+proj=lcc +lat_1='+str(latin1)+' +lat_2='+str(latin2)+' +lat_0='+str(lat01)+' +lon_0='+str(lon01)+' +a=6370000 +b=6370000 ')
    lon02,lat02 = findprojcent(shpd02)
    ind = abs(lon02-lon01+lat02-lat01)
    num = 1
    while ind>0.01 :
        shpd03=shpd01.to_crs('+proj=lcc +lat_1='+str(latin1)+' +lat_2='+str(latin2)+' +lat_0='+str(lat02)+' +lon_0='+str(lon02)+' +a=6370000 +b=6370000 ')
        lon03,lat03 = findprojcent(shpd03)
        ind = abs(lon02-lon03+lat02-lat03)
        lon02 = lon03
        lat02 = lat03
        num = num +1
    return lon03,lat03,shpd03

def findprojcent(shpd02):
    gdft = gpd.GeoDataFrame({'point':['center'],'geometry':[shapely.geometry.Point((shpd02.total_bounds[0]+shpd02.total_bounds[2])/2,(shpd02.total_bounds[1]+shpd02.total_bounds[3])/2)]},crs=shpd02.crs)
    x = gdft.to_crs(epsg=4326)['geometry'].x[0]
    y = gdft.to_crs(epsg=4326)['geometry'].y[0]
    return x,y
def callatlon(x0,x1,y0,y1,crsin):
    gdft = gpd.GeoDataFrame({'point':['center'],'geometry':[shapely.geometry.Point((x0+x1)/2,(y0+y1)/2)]},crs=crsin)
    lon = gdft.to_crs(epsg=4326)['geometry'].x[0]
    lat = gdft.to_crs(epsg=4326)['geometry'].y[0]
    return lon,lat


def bound_parent(shpd01,dx,xladd,xradd,ytadd,ydadd):
    disx = shpd01.total_bounds[2] - shpd01.total_bounds[0]
    disy = shpd01.total_bounds[3] - shpd01.total_bounds[1]
    numx = int(1+disx/dx) + xradd+xladd
    numy = int(1+disy/dx) + ytadd+ydadd
    xmin = -(numx*dx)/2
    ymin = -(numy*dx)/2
    xstart = 0
    ystart = 0
    return xmin,ymin,numx,numy,xstart,ystart

def bound_son(shpd01,shpath,dxson,dxpar,xladd,xradd,ytadd,ydadd,xpar,ypar):
    shpd02 = gpd.read_file(shpath)
    shptmp = shpd02.to_crs(shpd01.crs)
    disx = shptmp.total_bounds[2] - shptmp.total_bounds[0]
    disy = shptmp.total_bounds[3] - shptmp.total_bounds[1]
    numx = int(1+disx/dxson) + (xladd + xradd) + getdiff(shptmp.total_bounds[0],xpar,dxson,dxpar)
    numy = int(1+disy/dxson) + (ytadd + ydadd) + getdiff(shptmp.total_bounds[1],ypar,dxson,dxpar)
    numx = modifygridnum(numx,dxson,dxpar)
    numy = modifygridnum(numy,dxson,dxpar)
    xmin = getmin(shptmp.total_bounds[0],xpar,dxson,dxpar,xladd)
    ymin = getmin(shptmp.total_bounds[1],ypar,dxson,dxpar,ydadd)
    xstart = (xmin - xpar)/dxpar
    ystart = (ymin - ypar)/dxpar
    return xmin,ymin,numx,numy,xstart,ystart


def createbox(xmin,ymin,numx,numy,dx,crsin,name):
    x = np.arange(xmin,xmin+numx*dx,dx)
    y = np.arange(ymin,ymin+numy*dx,dx)
    colt = np.arange(0,numx,1)
    rowt = np.arange(0,numy,1)
    col,row = np.meshgrid(colt,rowt)
    x0,y0 = np.meshgrid(x,y)
    x0=x0.flatten()
    y0=y0.flatten()
    col=col.flatten()
    row = row.flatten()
    x1 = x0 + dx
    y1 = y0 + dx
    numid = np.arange(0,numx*numy,1)
    gdft = gpd.GeoDataFrame({'point':numid,'geometry':gpd.points_from_xy((x0+x1)/2, (y0+y1)/2)},crs=crsin)
    lon = gdft.to_crs(epsg=4326)['geometry'].x
    lat = gdft.to_crs(epsg=4326)['geometry'].y
    grid_cells=[]
    for i in range(0,int(numx*numy)):
        grid_cells.append(shapely.geometry.box(x0[i],y0[i],x1[i],y1[i]))
    df = pd.DataFrame({'id':numid,'row':row,'col':col,'LAT':lat,'LON':lon,'geometry':grid_cells})
    cell = gpd.GeoDataFrame(df,crs=crsin)
    cell.to_file('./output/wrf_'+name+'.shp')
    cell[['id','row','col','LAT','LON']].to_csv('./output/wrf_'+name+'.csv')
    return cell

def createboxmod(xmin,ymin,numx,numy,dx,crsin,name,clipn):
    print('clip x or y direction by '+str(clipn)+' grid')
    xmin = xmin +clipn*dx
    ymin = ymin +clipn*dx
    numx = numx -2*clipn
    numy = numy -2*clipn
    x = np.arange(xmin,xmin+numx*dx,dx)
    y = np.arange(ymin,ymin+numy*dx,dx)
    colt = np.arange(0,numx,1)
    rowt = np.arange(0,numy,1)
    col,row = np.meshgrid(colt,rowt)
    x0,y0 = np.meshgrid(x,y)
    x0=x0.flatten()
    y0=y0.flatten()
    col=col.flatten()
    row = row.flatten()
    x1 = x0 + dx
    y1 = y0 + dx
    numid = np.arange(0,numx*numy,1)
    gdft = gpd.GeoDataFrame({'point':numid,'geometry':gpd.points_from_xy((x0+x1)/2, (y0+y1)/2)},crs=crsin)
    lon = gdft.to_crs(epsg=4326)['geometry'].x
    lat = gdft.to_crs(epsg=4326)['geometry'].y
    grid_cells=[]
    for i in range(0,int(numx*numy)):
        grid_cells.append(shapely.geometry.box(x0[i],y0[i],x1[i],y1[i]))
    df = pd.DataFrame({'ID':numid,'rownum':row,'colnum':col,'LAT':lat,'LON':lon,'geometry':grid_cells})
    cell = gpd.GeoDataFrame(df,crs=crsin)
    cell.to_file('./output/aqm_'+name+'.shp')
    cell[['ID','rownum','colnum','LAT','LON']].to_csv('./output/aqm'+name+'.csv')
    return cell

def getmin(xminson,xminpar,dxson,dxpar,xladd):
    minx = (((int((xminson-xminpar)/dxpar))*dxpar)+xminpar)-(dxson*xladd)    #ratio dx
    return minx

def modifygridnum(numx,dxson,dxpar):
    ratio = dxpar/dxson
    if numx%ratio == 0:
        print('no modify gridnum')
    else:
        numx = numx+ratio-numx%ratio
        print('modifying gridnum')
    return numx

def getdiff(xminson,xminpar,dxson,dxpar):
    diffgrid = int((xminson-((int((xminson-xminpar)/dxpar)*dxpar)+xminpar))/dxson)+1
    return diffgrid

def main(shpath,latin1,latin2,domnum,dx,xladd,xradd,ytadd,ydadd,modelclip,fname,outname):
    loncent,latcent,shpd01= findcent(latin1,latin2,shpath[0])
    print('LCC projection:  mid lon:'+str(loncent)+',mid lat:'+str(latcent) )
    gridname,xmin,ymin,numx,numy,xstart,ystart,centlon,centlat = np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum),np.zeros(domnum)
    iddom=0
    for i in range(0,domnum):
        centlon[i]=loncent
        centlat[i]=latcent
        print('processing Domain ID:' + str(i))
        if i == 0 :
            print('getting gridding parameters for Domain:' + str(i))
            xmin[i],ymin[i],numx[i],numy[i],xstart[i],ystart[i]= bound_parent(shpd01,int(dx[0]),int(xladd[0]),int(xradd[0]),int(ytadd[0]),int(ydadd[0]))
            print('creating fishnet for WRF of WRF:' + str(i))
            createbox(xmin[i],ymin[i],numx[i],numy[i],int(dx[i]),shpd01.crs,fname[i])
            print('creating fishnet for AQM of AQM:' + str(i))
            createboxmod(xmin[i],ymin[i],numx[i],numy[i],int(dx[i]),shpd01.crs,fname[i],int(modelclip[i]))
        else:
            print('getting gridding parameters for Domain:' + str(i))
            xmin[i],ymin[i],numx[i],numy[i],xstart[i],ystart[i]= bound_son(shpd01,shpath[i],int(dx[i]),int(dx[i-1]),int(xladd[i]),int(xradd[i]),int(ytadd[i]),int(ydadd[i]),int(xmin[i-1]),int(ymin[i-1]))
            print('creating fishnet for WRF of Domain:' + str(i))
            createbox(xmin[i],ymin[i],numx[i],numy[i],int(dx[i]),shpd01.crs,fname[i])
            print('creating fishnet for AQM of Domain:' + str(i))
            createboxmod(xmin[i],ymin[i],numx[i],numy[i],int(dx[i]),shpd01.crs,fname[i],int(modelclip[i]))
        gridname[i]=iddom
        iddom+=1
    output = pd.DataFrame({'domid':gridname,'centlon':centlon,'centlat':centlat,'xmin':xmin,'ymin':ymin,'numx':numx,'numy':numy,'xstart':xstart,'ystart':ystart})
    output.to_csv('./output/'+outname+'_gridinfo.csv',index=False)
    print('finish')

import configparser
config = configparser.ConfigParser()
config.read('par.ini')
latin1=float(config['projection']['lat1'])
latin2 = float(config['projection']['lat2'])
domnum = int(config['domain']['numdom'])
shpath = config['domain']['shpath'].split(',')
dx = config['domain']['dx'].split(',')
domname = config['domain']['domname'].split(',')
casename = config['domain']['casename']
xladd = config['domain']['xladd'].split(',')
xradd = config['domain']['xradd'].split(',')
ytadd = config['domain']['ytadd'].split(',')
ydadd = config['domain']['ydadd'].split(',')
modelclip = config['domain']['model_clip'].split(',')

main(shpath,latin1,latin2,domnum,dx,xladd,xradd,ytadd,ydadd,modelclip,domname,casename)
