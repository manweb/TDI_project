import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as cl
from matplotlib.colors import LogNorm
import time
import datetime
import re
from utilities import CensusTractFinder
from utilities import AFFData
from utilities import Geometry

fname = 'Car_Break_Ins_Clean.csv'

data = pd.read_csv(fname, quotechar='"')

dateformat = '%m/%d/%Y'
ref_date = time.mktime(time.strptime('01/01/2018', dateformat))
p_date = re.compile('(\d{2})/(\d{2})/(\d{4})')
p_time = re.compile('(\d{2}):(\d{2})')
t = []
w = []
m = []
for entry in np.array(data[['Date', 'Time']].as_matrix().astype(str)):
    weekday = datetime.datetime.strptime(entry[0], dateformat).weekday()
    
    date_matches = p_date.match(entry[0])
    time_matches = p_time.match(entry[1])
    
    if int(date_matches.group(1)) == 2 and int(date_matches.group(2)) == 29:
        continue
    
    month = time.mktime(time.strptime('%02i/%02i/2018'%(int(date_matches.group(1)), int(date_matches.group(2))), dateformat))
    
    time_of_day = (float(time_matches.group(1))*60 + float(time_matches.group(2)))/60
    time_of_year = (time_of_day + (month - ref_date)/3600)/24
    time_of_week = (time_of_day + weekday*24)/24

    t.append(time_of_day)
    w.append(weekday)
    m.append(time_of_year)

loc = np.array(data[['X', 'Y']].as_matrix().astype(float))

geom = Geometry()

SF_boundaries_x, SF_boundaries_y = geom.GetSFBoundaries()

fig, (ax1,ax2,ax3) = plt.subplots(1,3,figsize=(12,4))

ax3.hist2d(loc[:,0], loc[:,1],bins=(100,100),range=[[-122.53,-122.35],[37.7,37.83]], norm=LogNorm())
ax3.plot(SF_boundaries_x, SF_boundaries_y, color='red')
ax1.hist(loc[:,0],bins=100,range=[-122.53,-122.35])
#ax2.hist(loc[:,1],bins=100,range=[37.7,37.83])
#ax3.imshow(np.flip(h1.T,0), interpolation='nearest', aspect='auto', extent=[-122.53,-122.35,37.7,37.82])

ax2.plot(SF_boundaries_x, SF_boundaries_y, color='red')

data_census_tracts = pd.read_csv('Census_2010_Tracts_coords.csv', quotechar='"').as_matrix().astype(str)

aff_data = AFFData()

cmap = plt.cm.get_cmap('viridis', 100)

for dt in data_census_tracts:
    census_tract = float(dt[0])
    census_tract_str = str(census_tract)
    if census_tract - np.floor(census_tract) == 0:
        census_tract_str = '%.0f'%census_tract
    print dt[0]
    print census_tract_str
    poverty_data = aff_data.GetPovertyForCensusTract(census_tract_str)
    circle = plt.Circle((float(dt[2]), float(dt[1])), radius=0.5, color=cl.rgb2hex(cmap(poverty_data)[:3]))
    ax2.add_patch(circle)

fig.subplots_adjust(left=0.05, right=0.95, bottom=0.11, top=0.88, wspace=0.25, hspace=0.2)

#ax1.hist(t, bins=24, facecolor='lightblue', edgecolor='black')
#ax2.hist(w, bins=7, facecolor='lightblue', edgecolor='black')
#ax3.hist(m, bins=12, facecolor='lightblue', edgecolor='black')

#h1, _, _, _ = ax1.hist2d(t,m,bins=(24,24))
#h2, _, _, _ = ax2.hist2d(t,w,bins=(24,7))
#plt.clf()
#ax1.imshow(np.flip(h1.T,0), interpolation='gaussian', aspect='auto', extent=[0,24,0,365])
#ax2.imshow(np.flip(h2.T,0), interpolation='gaussian', aspect='auto', extent=[0,24,0,7])

plt.show()
