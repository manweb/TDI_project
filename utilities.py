import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

CENSUS_TRACT_FNAME = 'Census_2010_Tracts_Clean.csv'
SF_BOUNDARIES_FNAME = 'SF_boundaries2.txt'
WEATHER_FNAME = 'Weather_Data_Clean.csv'
POVERTY_FNAME = 'aff_download/ACS_16_5YR_S1701_with_ann.csv'

class CensusTractFinder(object):
    def __init__(self):
        self.TractData = {}

    def LoadData(self):
        data = pd.read_csv(CENSUS_TRACT_FNAME, quotechar='"').as_matrix().astype(str)
        
        self.TractData = {}
        for d in data:
            tract = float(d[0])
            plg = d[1].replace('MULTIPOLYGON (((','').replace(')))', '').split(', ')
            plg_arr = [(float(s.split(' ')[0]), float(s.split(' ')[1])) for s in plg]
            
            tract_str = str(tract)
            if tract - np.floor(tract) == 0:
                tract_str = '%.0f'%tract

            self.TractData[tract_str] = Polygon(plg_arr)

    def IsInCensusTract(self, lat, lon, key):
        p = Point(lon, lat)
    
        return self.TractData[key].contains(p)
    
    def FindCensusTract(self, lon, lat):
        p = Point(lon, lat)
    
        for key, value in self.TractData.items():
            if value.contains(p):
                return key

        return None
    
    def GetCoordinates(self, key):
        p = self.TractData[key]
    
        return p.exterior.coords.xy

    def __getitem__(self,key):
        return self.TractData[key]

class Geometry(object):
    def __init__(self):
        self.data_sf_boundaries = pd.read_csv(SF_BOUNDARIES_FNAME).as_matrix()

    def GetSFBoundaries(self):
        return self.data_sf_boundaries[:,0], self.data_sf_boundaries[:,1]

class Weather(object):
    def __init__(self):
        self.data = pd.read_csv(WEATHER_FNAME, quotechar='"')
        self.data.fillna(0, inplace=True)

    def CleanData(self):
        self.data = pd.read_csv(WEATHER_FNAME, quotechar='"')[['date', 'time', 'temperature', 'pressure', 'precip', 'event']]

        df = pd.DataFrame(columns=['timestamp', 'date', 'time', 'temperature', 'pressure', 'precip', 'event'])
        dateformat = '%Y-%m-%d %H:%M:%S'
        timestamps = []
        for d in self.data.as_matrix().astype(str):
            timestamps.append(str(time.mktime(time.strptime('%s %s'%(d[0], d[1]), dateformat))))

        self.data['timestamp'] = pd.Series(timestamps, index=self.data.index)

        self.data.to_csv('Weather_Data_Clean.csv', index=False)

    def GetWeatherForDate(self, d):
        dateformat = '%Y-%m-%d %H:%M:%S'
        t = time.mktime(time.strptime(d, dateformat))

        id = np.argsort(np.abs(self.data['timestamp'].as_matrix()-t))[0]

        return self.data.as_matrix()[id,2:6]

class AFFData(object):
    def __init__(self):
        self.data_poverty = pd.read_csv(POVERTY_FNAME, quotechar='"', skiprows=[1])[['GEO.display-label', 'HC03_EST_VC01']]

    def GetPovertyForCensusTract(self, census_tract):
        try:
            row = self.data_poverty.loc[self.data_poverty['GEO.display-label'] == 'Census Tract %s, San Francisco County, California'%census_tract, 'HC03_EST_VC01'].as_matrix()[0]
        except:
            print('Problem with census tract %s'%census_tract)
            return 0

        return float(row)
