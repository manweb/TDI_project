import numpy as np
import pandas as pd
import datetime
from utilities import CensusTractFinder
from utilities import Weather
from utilities import AFFData

INCIDENTS_FNAME = 'Police_Department_Incidents.csv'
WEATHER_FNAME = 'Weather_Data.csv'
POVERTY_FNAME = 'ACS_16_5YR_S1701_with_ann.csv'

cs = CensusTractFinder()
cs.LoadData()

w = Weather()

aff_data = AFFData()

data_incidents = pd.read_csv(INCIDENTS_FNAME, quotechar='"')
d = np.array(data_incidents[['Descript', 'DayOfWeek', 'Date', 'Time', 'X', 'Y']].dropna().as_matrix().astype(str))

ids = [i for i, val in enumerate(d[:,0]) if 'THEFT FROM LOCKED AUTO' in val]
d = d[ids]

weather_data = pd.DataFrame(columns=['temperature','pressure','precip','event'])
cencus_tract = pd.DataFrame(columns=['CensusTract'])
poverty_level = pd.DataFrame(columns=['poverty'])
for i, dt in enumerate(d):
    date_time = datetime.datetime.strptime('%s %s'%(dt[2],dt[3]), '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
    weather_data.loc[i] = w.GetWeatherForDate(date_time)
    
    ct = cs.FindCensusTract(float(dt[4]), float(dt[5]))
    cencus_tract.loc[i] = ct
    
    poverty_level.loc[i] = aff_data.GetPovertyForCensusTract(ct)

    if i%100 == 0:
        print('%i events processed'%i)

df = pd.DataFrame(d, columns=['Descript', 'DayOfWeek', 'Date', 'Time', 'X', 'Y'])
df = pd.concat([df, weather_data, cencus_tract, poverty_level], axis=1)
df.to_csv('Car_Break_Ins_Clean_2.csv', index=False)
