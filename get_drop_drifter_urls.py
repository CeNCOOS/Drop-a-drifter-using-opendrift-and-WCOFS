import numpy as np
from datetime import datetime, timedelta
import xarray as xr
from ast import literal_eval
import pandas as pd
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_global_landmask
#from opendrift.readers import reader_ROMS_native
from opendrift.readers.reader_ROMS_native import Reader
#from opendrift.readers.reader_ROMS_native_s3 import Reader
#import s3fs
import pdb
progstart=datetime.now()
# set up URL stubs
urlpre1='https://www.ncei.noaa.gov/thredds/dodsC/model-wcofs-files/'
filepre='nos.wcofs.fields.'
urlpre2='https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/WCOFS/MODELS/'
# New NOAA NODD
#urlpre3='https://noaa-nos-ofs-pds.s3.amazonaws.com/wcofs/netcdf/'
#urlpre3='s3://noaa-nos-ofs-pds.s3.amazonaws.com/wcofs/netcdf/' # need credentials to do this
# get open drift model initiated
o=OceanDrift(loglevel=30)
# need to get the start time for the simulation
datestart=input('Enter the start date/time (yyyymmddThhmm)')
parsedstart=datetime.strptime(datestart,'%Y%m%dT%H%M')
# need to get the end time for the simulation
datestop=input('Enter the ending date/time (yyyymmddThhmm)')
parsedstop=datetime.strptime(datestop,'%Y%m%dT%H%M')
# need to get the start depth
thedepth=input('Enter the starting depth in meters: ')
thedepth=int(thedepth)
if thedepth > 0:
    thedepth=-1.0*thedepth
# This may need work as we are only allowing one specific point to be entered
# get starting point
latlon=input('Enter the start location [latitude, longitude]')
latlon=np.array(literal_eval(latlon))
latstart=latlon[0]
lonstart=latlon[1]
# create times between start and stop
istart=datetime(parsedstart.year,parsedstart.month,parsedstart.day,parsedstart.hour,parsedstart.minute,0)
istop=datetime(parsedstop.year,parsedstop.month,parsedstop.day,parsedstop.hour,parsedstop.minute,0)
jstart=datetime(parsedstart.year,parsedstart.month,parsedstart.day)+timedelta(days=1)
jstop=datetime(parsedstop.year,parsedstop.month,parsedstop.day)-timedelta(days=1)
mydt=timedelta(days=1)
somedates=np.arange(jstart,jstop+mydt,mydt)
somedates=np.insert(somedates,0,np.datetime64(istart),axis=0)
modeldaterange=np.append(somedates,np.datetime64(istop))
# Example of what we want
# 20230212T0600 to 20230216T1800
# want [20230212T0600 20230213T0000 20230214T0000 20230215T0000 20230216T1800]
#
# we need to now the current date as that will help inform which end point or points we need to use
mynow=datetime.now()
curyear=mynow.year
curmon=mynow.month
curday=mynow.day
# get ready to form URLS
# set up forecast and nowcast hours so we don't have to jump through hoops creating these strings
# now cast list is every 3 hours
nt=['003','006','009','012','015','018','021','024']
ft=['003','006','009','012','015','018','021','024','027','030','033','036','039','042','045','048','051','054','057','060','063','066','069','072']
ln=len(nt)
inow=np.arange(0,ln)
lf=len(ft)
ifor=np.arange(0,lf)
filepost='t03z.nc'
list_of_urls=[]
#
# compute the URLS for the data to load
#
icount=0
for mydate in modeldaterange:
    adate=pd.to_datetime(mydate)        
    mdays=mynow-adate
##    icount=1
##    startdate=adate-timedelta(days=1)
##    urls=urlpre3+str(startdate.year)+str(startdate.month).zfill(2)+'/'+filepre
##    fmid='n'+nt[-1]+'.'+str(startdate.year)+str(startdate.month).zfill(2)+str(startdate.day).zfill(2)
##    theurl=urls+fmid+'.'+filepost
##    list_of_urls.append(theurl)
##    #
##    urls=urlpre3
##    urls=urls+str(adate.year)+str(adate.month).zfill(2)+'/'+filepre   
##    for jnow in inow:
##        fmid='n'+nt[jnow]+'.'+str(adate.year)+str(adate.month).zfill(2)+str(adate.day).zfill(2)
##        theurl=urls+fmid+'.'+filepost
##        list_of_urls.append(theurl)
##    pdb.set_trace()        
    

    
    if mdays > timedelta(days=7):
        if adate.hour==0 and icount==0:
            icount=1
            startdate=adate-timedelta(days=1)
            urls=urlpre1+str(startdate.year)+'/'+str(startdate.month).zfill(2)+'/'+filepre
            fmid='n'+nt[-1]+'.'+str(startdate.year)+str(startdate.month).zfill(2)+str(startdate.day).zfill(2)
            theurl=urls+fmid+'.'+filepost
            list_of_urls.append(theurl)
 #           print(theurl)
        urls=urlpre1
        urls=urls+str(adate.year)+'/'+str(adate.month).zfill(2)+'/'+filepre
        # is this the first day of the simulation? If so we may not need to load all of the now casts
        # for the moment ignore sofistication
        for jnow in inow:
            fmid='n'+nt[jnow]+'.'+str(adate.year)+str(adate.month).zfill(2)+str(adate.day).zfill(2)
            theurl=urls+fmid+'.'+filepost
            list_of_urls.append(theurl)
#            print(theurl)
    else:
        if adate.hour==0 and icount==0:
            icount=1
            startdate=adate-timedelta(days=1)
            urls=urlpre2+str(startdate.year)+'/'+str(startdate.month).zfill(2)+'/'+str(startdate.day).zfill(2)+'/'+filepre
            fmid='n'+nt[-1]+'.'+str(startdate.year)+str(startdate.month).zfill(2)+str(startdate.day).zfill(2)
            theurl=urls+fmid+'.'+filepost
            list_of_urls.append(theurl)
 #           print(theurl)
        urls=urlpre2+str(adate.year)+'/'+str(adate.month).zfill(2)+'/'+str(adate.day).zfill(2)+'/'+filepre
        if(mdays >= timedelta(days=0)):
            urls=urlpre2+str(adate.year)+'/'+str(adate.month).zfill(2)+'/'+str(adate.day).zfill(2)+'/'+filepre
#        if (mdays < timedelta(days=1) and mdays < timedelta(days=-1)):
            for jnow in inow:
                fmid='n'+nt[jnow]+'.'+str(adate.year)+str(adate.month).zfill(2)+str(adate.day).zfill(2)
                theurl=urls+fmid+'.'+filepost
                list_of_urls.append(theurl)
 #               print(theurl)
        else:
            urls=urlpre2+str(adate.year)+'/'+str(adate.month).zfill(2)+'/'+str(curday).zfill(2)+'/'+filepre

            for jfor in ifor:
                fmid='f'+ft[jfor]+'.'+str(curyear)+str(curmon).zfill(2)+str(curday).zfill(2)
                theurl=urls+fmid+'.'+filepost
                list_of_urls.append(theurl)
#                print(theurl)
# Set up the seeding parameters
# this is the line to run the model data reader
modeldata=Reader(list_of_urls)
# number of points, depth, radius and start time
# the line below won't work since we don't have opendrift installed but it is an attempt at writing the startup
o.seed_elements(lonstart,latstart,z=thedepth,radius=0,number=1,time=parsedstart)
#o.seed_elements(lonstart,latstart,z=thedepth,radius=5000,number=50,time=parsedstart)
o.add_reader([modeldata])
outputvars=['time',
           'sea_water_temperature',
           'sea_water_salinity',
           'age_seconds',
           'land_binary_mask',
           'lat',
           'lon',
           'z',
           'x_sea_water_velocity',
           'y_sea_water_velocity',
           'status',
           'trajectory',
           'upward_sea_water_velocity']
# Model run call
theduration=parsedstop-parsedstart
durationdays=theduration.days
durationsecs=theduration.seconds
durationhour=durationsecs/60/60
durationdays=durationdays+durationhour/24
afilename='test_run.nc'
o.run(time_step=timedelta(hours=1),duration=timedelta(days=durationdays),export_variables=outputvars,outfile=afilename)
progend=datetime.now()
print(progend-progstart)
