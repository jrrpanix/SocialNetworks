import h5py
import numpy as np
import pandas as pd
import os

class ToHDF5:

    def __init__(self):
        self.usecols = [0,1,2,3,4]
        self.names = ["date","time","price","qty","status"]
        self.dtypes={'date':'str','time':'str','price':'float','qty':'int','status':'str'}
        
    def convert(self, infile, outdir):
        df = pd.read_csv(infile, 
                         usecols=self.usecols,
                         header=None, 
                         names=self.names,
                         dtype=self.dtypes,
                         sep=",")
        df['dt'] = df['date'] + " " + df['time']
        df=df.drop(['date','time'], axis=1)
        df['dt'] = pd.to_datetime(df['dt'],format="%m/%d/%Y %H:%M:%S.%f")
        df.set_index('dt')
        mins,maxs = df['dt'].min().strftime("%Y%m%d"), df['dt'].max().strftime("%Y%m%d")
        base = os.path.basename(infile)
        outfile = os.path.join(outdir, base.split("_")[0] + "_" + mins + "_" + maxs + ".h5")
        df.to_hdf(outfile, 'table', table=True, complevel=9, complib='zlib', mode='w')
        return outfile


name="/Users/john/TickData/gz/EC_2018_20190315.csv.gz"
h5 = ToHDF5()
h5.convert(name, "./")
