import numpy as np
import pandas as pd
import time
import datetime
import re
from utilities import CensusTractFinder
from utilities import Weather
from utilities import AFFData

INCIDENTS_FNAME = 'Police_Department_Incidents.csv'
WEATHER_FNAME = 'Weather_Data.csv'
POVERTY_FNAME = 'ACS_16_5YR_S1701_with_ann.csv'

dateformat = '%m/%d/%Y'
ref_date = time.mktime(time.strptime('01/01/2018', dateformat))
p_date = re.compile('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')

def getTimeFromString(s):
    date_matches = p_date.match(s)

    return int(date_matches.group(3)), int(date_matches.group(2)), int(date_matches.group(4)), int(date_matches.group(5))

cs = CensusTractFinder()
cs.LoadData()

w = Weather()

aff_data = AFFData()

data_incidents = pd.read_csv(INCIDENTS_FNAME, quotechar='"')
d = np.array(data_incidents.loc[data_incidents['Descript'].str.contains('THEFT FROM LOCKED AUTO')][['Descript', 'DayOfWeek', 'Date', 'Time', 'X', 'Y']].dropna().values.astype(str))

weather_data = pd.DataFrame(columns=['temperature','pressure','precip','event'])
temporal_data =pd.DataFrame(columns=['hour_of_day', 'day_of_week', 'day_of_year'])
demographic_data = pd.DataFrame(columns=['CensusTract', 'population', 'poverty', 'unemployment'])
cencus_tract = pd.DataFrame(columns=['CensusTract'])
poverty_level = pd.DataFrame(columns=['poverty'])
for i, dt in enumerate(d):
    date_time = datetime.datetime.strptime('%s %s'%(dt[2],dt[3]), '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
    
    weekday = datetime.datetime.strptime(dt[2], dateformat).weekday()
    
    t_day, t_month, t_hour, t_minute = getTimeFromString(date_time)
    
    if t_month == 2 and t_day == 29:
        t_day = 28
    
    month = time.mktime(time.strptime('%02i/%02i/2018'%(t_month, t_day), dateformat))
    
    time_of_day = (float(t_hour)*60 + float(t_minute))/60
    time_of_year = (time_of_day + (month - ref_date)/3600)/24
    time_of_week = (time_of_day + weekday*24)/24
    
    weather_data.loc[i] = w.GetWeatherForDate(date_time)

    temporal_data.loc[i] = [time_of_day, time_of_week, time_of_year]
    
    ct = cs.FindCensusTract(float(dt[4]), float(dt[5]))

    population = aff_data.GetPopulationForCensusTract(ct)
    poverty_level = aff_data.GetPovertyForCensusTract(ct)
    unemployment = aff_data.GetUnemploymentForCensusTract(ct)

    demographic_data.loc[i] = [ct, population, poverty_level, unemployment]

    if i%100 == 0:
        print('%i events processed'%i)

df = pd.DataFrame(d[:,2:], columns=['Date', 'Time', 'X', 'Y'])
df = pd.concat([df, weather_data, temporal_data, demographic_data], axis=1)
df.to_csv('Car_Break_Ins_Clean_3.csv', index=False)
