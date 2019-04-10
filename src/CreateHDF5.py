import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse

"""
Convert CME Trade Tick Data to hdf5 files indexe by date-time
Format allows for rapid read into pandas
"""

class ToHDF5:

    def __init__(self):
        self.usecols = [0,1,2,3,4]
        self.names = ["date","time","price","qty","status"]
        self.dtypes={'date':'str','time':'str','price':'float','qty':'int','status':'str'}
        
    def convert(self, infile, outdir, lines):
        if infile.split(".")[-1] == "h5":
            print("ignoring file: %s already in h5 format" % infile)
            return
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
        outfiles = self.chunkDataFrame(df, ToHDF5.getSymbol(infile), outdir, lines)
        df = None
        return outfiles

    def getSymbol(infile):
        return os.path.basename(infile).split("_")[0]

    def splitFile(self, infile, outdir, lines, forceWrite=True):
        df = pd.read_hdf(infile, 'table')
        if len(df) <= lines and forceWrite == False:
            return []
        return self.chunkDataFrame(df, ToHDF5.getSymbol(infile), outdir, lines)

    def chunkDataFrame(self, df, symbol, outdir, lines):
        b, e, outfiles = 0, lines, []
        while b < len(df):
            e = min(len(df), e)
            dfi = df.iloc[b:e]
            sys.stdout.flush()
            ofile = self.writeFile(dfi, symbol, outdir)
            outfiles.append(ofile)
            b = e
            e = min(len(df), e + lines)
            dfi = None
        return outfiles

    def writeFile(self, df, symbol, outdir):
        mins,maxs = df['dt'].min().strftime("%Y%m%d"), df['dt'].max().strftime("%Y%m%d")
        outfile = os.path.join(outdir, symbol + "_" + mins + "_" + maxs + ".h5")
        df.to_hdf(outfile, 'table', table=True, complevel=9, complib='zlib', mode='w')
        print("created file=%s, records=%d" % (outfile, len(df)))
        sys.stdout.flush()
        return outfile
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SocialNetworks CSV to HDF5')
    parser.add_argument('--idir', help='specify input directory or input file', default=None)
    parser.add_argument('--odir', help='output directory')
    parser.add_argument('--ifile', help='specify input directory or input file', default=None)
    parser.add_argument('--lines', type=int, default=10000000, help='number of lines per file')
    parser.add_argument('--split', action='store_true', help='split the file into smaller chunks', default=False)
    args = parser.parse_args()
    assert args.odir is not None
    assert os.path.exists(args.odir)
    assert args.ifile is not None and args.idir is None or args.ifile is None and args.idir is not None
    assert len(sys.argv) > 2
    idir, ifile, lines, splitFile, odir = args.idir, args.ifile, args.lines, args.split, args.odir
    h5 = ToHDF5()
    if splitFile:
        if idir is not None:
            for f in os.listdir(idir):
                ofiles = h5.splitFile(os.path.join(idir, f), odir, lines)
                if ofiles:
                    print("sucessfully split " ,os.path.join(idir, f), "to", ofiles)
        else:
            ofiles = h5.splitFile(ifile, odir, lines)
            if ofiles:
                print("sucessfully split ",  os.path.join(idir, f) , "to", ofiles)
    else:
        if idir is not None:
            for f in os.listdir(idir):
                ofile = h5.convert(os.path.join(idir, f), odir, lines)
                if ofile is not None:
                    print("converted file %s" % ofile)
                    sys.stdout.flush()
        else:
            ofile = h5.convert(ifile, odir, lines)
            print("converted file %s" % ofile)
