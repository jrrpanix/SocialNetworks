import argparse
import os
import pandas as pd
import datetime

from OHLC import OHLC
from OHLC import ComputeOHLC
from ReadH5 import ReadH5
from Utils import Utils

class EvalDates:

    def __init__(self, dataDir, dates, event, symbol, before, after, outdir):
        self.reader = ReadH5(dataDir, reportNoData=False)
        self.dates = dates
        self.event = event
        self.symbol = symbol
        self.before = before
        self.after = after
        self.outdir = outdir
        self.TickSize = Utils.tickSize(symbol)
        self.outstr = "{}_{}_{}_{}".format(symbol, before, after, event)
        self.run()
        print("Eval Complete output file %s" % self.outfile)

    def run(self):
        self.outfile = os.path.join(self.outdir, "{}.{}".format(self.outstr,"csv"))
        fd=open(self.outfile, "w")
        header="date,beginD,endD,O,H,L,C,R,T,V,N"
        fd.write( "%s\n" % header)
        for date in self.dates:
            tickdf = self.reader.readh5(self.symbol, date)
            if tickdf is not None:
                o = ComputeOHLC.calc(tickdf, date, self.before, self.after, self.TickSize)
                fd.write("%s,%s,%s%f,%f,%f,%f,%f,%f,%f,%f\n" %
                         (o.D, o.beginD, o.endD, o.O, o.H, o.L, o.C, o.R, o.Ticks, o.V, o.N))
        fd.close()

def RunEvent(dataDir, ann, event, symbol, before, after, outdir) :
    eventdf = ann[ann["event"]==event] if event is not None else None
    if len(eventdf) == 0 : print("no data for event %s" % event)
    else:
        print("Running Event %s" % event)
        EvalDates(dataDir, eventdf.dt.values, event, symbol, before, after, outdir)

if __name__ == "__main__":
    # Note the CME Futures Data Timestamps are in Central Time
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Dates')
    parser.add_argument('--dataDir', help='specify tick data directory', default= os.path.join(os.getenv("HOME"),"TickData/splits"))
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-b','--before', help='before window seconds ', default=60, type=int)
    parser.add_argument('-a','--after', help='after window seconds', default=60*10, type=int)
    parser.add_argument('-o','--outdir', help='output dir', default=None)
    parser.add_argument('-i','--inputs', help='input file of dates', default="../data/dailyfx.h5")
    parser.add_argument('-e','--event', help="event or file of eventsnames", default=None)
    parser.add_argument('--start', help='start date', default=None)
    parser.add_argument('--end', help='end date', default=None)
    parser.add_argument('-l','--list', help='list events', action='store_true', default = False)
    args = parser.parse_args()

    inputs, dataDir, symbol, before, after, event, outdir = args.inputs, args.dataDir, args.symbol, args.before, args.after, args.event, args.outdir
    assert os.path.exists(dataDir), "tick data directory %s does not exist" % dataDir
    assert os.path.exists(inputs), "announcement file %s does not exist" % inputs
    assert os.path.exists(outdir), "output directory %s does not exist" % outdir
    ann=pd.read_hdf(args.inputs, 'table')
    if args.list :
        uv = sorted(ann.event.unique())
        for u in uv:
            print(u)
    else:
        if os.path.exists(event):
            with open(event) as f :
                for line in f:
                    line=line.strip()
                    if len(line) == 0 : continue
                    e = line.split(",")[0].strip()
                    # some 
                    if len(e.split("/")) > 1 : continue #event names with / cause problemes
                    RunEvent(dataDir, ann, e, symbol, before, after, outdir)
        else:
            RunEvent(dataDir, ann, event, symbol, before, after, outdir)

    
