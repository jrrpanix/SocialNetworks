import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def correlate(df, symbol):
    hints = ('preT','a-f')
    xlbls = ('pre-event movement','actual-forecast')
    xgetters = (lambda d: d['pre_T'], lambda d: [a-f for a,f in zip(d['A'],d['F'])])

    for ev, data in df.groupby(['event']):
        y = data['T']
        for hint, xlbl, xgetter in zip(hints, xlbls, xgetters):
            x = xgetter(data)
            cr = stats.pearsonr(x, y)
            
            plt.title(symbol+' '+ev+'\ncor='+str(cr[0]))
            plt.plot(x,y,'x')
            plt.xlabel(xlbl)
            plt.ylabel('movement')
            plt.savefig("../results/correlation/"+symbol+"_"+hint+"_"+ev+".png")
            plt.clf()

def run(symbol):
    file = '../results/{}_3600_60_600.csv'.format(symbol)
    df=pd.read_csv(file,dtype={'O':float,'H':float,'L':float,'C':float,'R':float,'T':float,'V':float,'N':float,'CD':float,'TD':float,'F':float,'P':float,'A':float,'pre_R':float,'pre_T':float,'pre_V':float})
    df = df.dropna(subset=['A','F','T','pre_T'])
    correlate(df,symbol)

if __name__ == "__main__":
    run('UB')
    run('TU')
    run('ES')
