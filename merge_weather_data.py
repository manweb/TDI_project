import glob
import pandas as pd

fnames = glob.glob('./KSFO*.csv')
fnames.sort()

l = []
for f in fnames:
    df = pd.read_csv(f, index_col=None, header=0)
    l.append(df)

frame = pd.concat(l)
frame.to_csv('Weather_Data.csv', index=False)
