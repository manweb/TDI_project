from PIL import Image
import urllib
import StringIO
import matplotlib.pyplot as plt
import pandas as pd

fname = 'Car_Break_Ins_Clean.csv'
data = pd.read_csv(fname, quotechar='"')[['X', 'Y']]
data = data.loc[~((data['Y'] > 37.775) & (data['Y'] < 37.7755)) & (data['Y'] < 38) & (data['Y'] > 35)]
loc = data.values.astype(float)

url = 'https://maps.googleapis.com/maps/api/staticmap?'
url2 = 'https://maps.googleapis.com/maps/api/streetview?'

for i in range(4):
	pars = urllib.urlencode({'center': '%f,%f'%(loc[i,1], loc[i,0]),
				 'zoom': '19',
				 'size': '400x400',
				 'maptype': 'satellite',
				 'key': 'AIzaSyBPuq0ATTnjllDj0kaRN4TxLRD6drXU0gs'})
	pars2 = urllib.urlencode({'size': '400x400',
				  'location': '%f,%f'%(loc[i,1], loc[i,0]),
				  'fov': '90',
				  'heading': '270',
				  'pitch': '0',
				  'key': 'AIzaSyBPuq0ATTnjllDj0kaRN4TxLRD6drXU0gs'})
	
	f = urllib.urlopen(url+pars)
	im = Image.open(StringIO.StringIO(f.read()))
	
	f2 = urllib.urlopen(url2+pars2)
	im2 = Image.open(StringIO.StringIO(f2.read()))
	
	im.show()
	im.save('Maps/Satellite_%i.png'%i)
	
	im2.show()
	im2.save('Maps/StreetView_%i.png'%i)

