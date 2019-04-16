import argparse
import os
import pandas as pd
import datetime

from OHLC import OHLC
from OHLC import ComputeOHLC
from ReadH5 import ReadH5
from Utils import Utils

class EvalData:

    def __init__(self):
        self.header="event,date,beginD,endD,O,H,L,C,R,T,V,N,CD,TD,F,P,A,pre_date,pre_R,pre_T,pre_V"
        self.dd={h:[] for h in self.header.split(",")}
        self.df=None

    def todf(self):
        self.df=pd.DataFrame(data=self.dd)        
        return self.df

    def update(self, o, p, event=""):
        self.dd["event"].append(event)
        self.dd["date"].append(o.D)
        self.dd["beginD"].append(o.beginD)
        self.dd["endD"].append(o.endD)
        self.dd["O"].append(o.O)
        self.dd["H"].append(o.H)
        self.dd["L"].append(o.L)
        self.dd["C"].append(o.C)
        self.dd["R"].append(o.R)
        self.dd["T"].append(o.T)
        self.dd["V"].append(o.V)
        self.dd["N"].append(o.N)
        self.dd["CD"].append(o.CD)
        self.dd["TD"].append(o.TD)
        self.dd["F"].append(o.Forecast)
        self.dd["P"].append(o.Prev)
        self.dd["A"].append(o.Act)
        self.dd["pre_date"].append(p.D)
        self.dd["pre_R"].append(p.R)
        self.dd["pre_T"].append(p.T)
        self.dd["pre_V"].append(p.V)


class EvalDates:

    def __init__(self, dataDir, symbol, before, after, pre):
        self.reader = ReadH5(dataDir, reportNoData=False)
        self.symbol = symbol
        self.before = before
        self.after = after
        self.pre = pre
        self.dd = EvalData()
        self.TickSize = Utils.tickSize(symbol)
        self.TickValue = Utils.tickValue(symbol)

    def run(self, event, dates, actual=None, forecast=None, previous=None):
        for i,date in enumerate(dates):
            tickdf = self.reader.readh5(self.symbol, date)
            if tickdf is not None:
                preT = Utils.todt(date) - datetime.timedelta(seconds=pre)
                p = ComputeOHLC.calc(tickdf, preT, self.before, self.after, self.TickSize, self.TickValue)
                ai,fi,pi = None,None,None
                if actual is not None : ai, fi, pi = actual[i], forecast[i], previous[i]
                o = ComputeOHLC.calc(tickdf, date, self.before, self.after, self.TickSize, self.TickValue, ai, fi, pi)
                self.dd.update(o, p, event)

    def todf(self):
        return self.dd.todf()


    def save(self, outdir):
        outstr="{}_{}_{}_{}".format(self.symbol, self.pre, self.before, self.after)
        outfile = os.path.join(outdir, "{}.{}".format(outstr, "csv"))
        if self.dd.df is None: self.dd.todf()
        df = self.dd.df
        df.to_csv(outfile, index=False)
        self.outfile=outfile
        return self.outfile

if __name__ == "__main__":
    # Note the CME Futures Data Timestamps are in Central Time
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Dates')
    parser.add_argument('--dataDir', help='specify tick data directory', default= os.path.join(os.getenv("HOME"),"TickData/splits"))
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-b','--before', help='before window seconds ', default=60, type=int)
    parser.add_argument('-a','--after', help='after window seconds', default=60*10, type=int)
    parser.add_argument('-p','--pre', help='pre time return', default=60*60, type=int)
    parser.add_argument('-o','--outdir', help='output dir', default=None)
    parser.add_argument('-i','--inputs', help='input file of dates', default="../data/cleaned_events.h5")
    parser.add_argument('-e','--event', help="event or file of eventsnames", default=None)
    parser.add_argument('--start', help='start date', default=None)
    parser.add_argument('--end', help='end date', default=None)
    parser.add_argument('-l','--list', help='list events', action='store_true', default = False)
    args = parser.parse_args()

    inputs, dataDir, symbol, before, after, event, outdir, pre = args.inputs, args.dataDir, args.symbol, args.before, args.after, args.event, args.outdir, args.pre
    assert os.path.exists(dataDir), "tick data directory %s does not exist" % dataDir
    assert os.path.exists(inputs), "announcement file %s does not exist" % inputs
    assert os.path.exists(outdir), "output directory %s does not exist" % outdir
    ann=pd.read_hdf(args.inputs, 'table')
    if args.list :
        uv = sorted(ann.event.unique())
        for u in uv:
            print(u)
    else:
        print(dataDir,symbol,before, after,pre)
        eval=EvalDates(dataDir, symbol, before, after, pre)
        if os.path.exists(event):
            eventFile = event
            with open(eventFile) as f :
                for line in f:
                    line=line.strip()
                    if len(line) == 0 : continue
                    event = line.split(",")[0].strip()
                    if len(event.split("/")) > 1 : continue #event names with / cause problemes
                    eventdf = ann[ann["event"]==event]
                    if len(eventdf) > 0:
                        print("running %s n=%d" % (event, len(eventdf)))
                        eval.run(event, eventdf.dt.values, eventdf.actual.values, eventdf.forecast.values, eventdf.previous.values)
        else:
            eventdf = ann[ann["event"]==event]
            if len(eventdf) > 0:
                print("running %s n=%d" % (event, len(eventdf)))
                eval.run(event, eventdf.dt.values, eventdf.actual.values, eventdf.forecast.values, eventdf.previous.values)
        outfile=eval.save(outdir)
        print("file saved to %s" % outfile)

    
