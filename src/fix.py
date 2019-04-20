import pandas as pd
import os


def fix(df, s, tickVal):
    df['Symbol'] =s 
    df['VolumeR'] = df['V_mean'] / df['preV_mean']
    df['TickR'] = df['EventTickMean'] / df['NonEventTickMean']
    df['StdR'] = df['R_std'] / df['preR_std']
    df['TickMaxR'] = df['EventMaxTicks'] / df['preT_max']
    #df['PreMarket$'] = df['preT_mean'] * tickVal #* df['preV_mean']
    #df['EventMarket$'] = df['T_mean'] * tickVal #* df['V_mean'] 
    #df['$Ratio'] = df['EventMarket$'] / df['PreMarket$']

def load():

    uc =[0,3,4,6,7,8,13,17,18,20,21]
    n = ['Event',
         'EventMaxTicks',
         'EventTickMean',
         'N',
         'preT_max',
         'NonEventTickMean',
         'R_std',
         'preR_std',
         'TD_max',
         'V_mean',
         'preV_mean'
         ]
    files = ["../results/tu.csv",
             "../results/ub.csv",
             "../results/es.csv"]
    tick_val =[ 1/128.0*2000, 1/32.0*1000, 12.50]
    data = []
    for T, f in zip(tick_val,files):
        df = pd.read_csv(f, usecols=uc, names=n)
        s, ex = os.path.splitext(os.path.basename(f))
        fix(df, s.upper(),T)
        #df = df[["Symbol","Event","TickR","StdR","VolumeR","TickMaxR","PreMarket$","EventMarket$","$Ratio"]]
        df = df[["Symbol","Event",
                 "N",
                 "EventMaxTicks",
                 "EventTickMean","NonEventTickMean",
                 "TickR","StdR","VolumeR","TickMaxR"
                 ]]
        data.append(df)
    combo = pd.concat(data, ignore_index=True)
    combo.sort_values(["Symbol","TickR"], inplace=True, ascending=False)
    print(combo)
    combo.to_csv("../results/ranking.csv", index=False)

load()

#d1['symbol'] = 'TU'
#d2['symbol'] = 'UB'
#d3['symbol'] = 'ES'

#print(d2)
