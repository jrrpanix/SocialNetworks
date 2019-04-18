import numpy as np
import pandas as pd
import argparse
import os
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from scipy import stats


class Estimates:

    def __init__(self, event, N, r2, acc, cr):
        self.event = event
        self.N = N   # number of obs
        self.r2 = r2 # r squared
        self.acc = acc # accuracy logistic regression
        self.cr = cr[0]

def Fit(X, y, logistic= True):
    model = LogisticRegression() if logistic == True else LinearRegression()
    yf = np.where(y > 0 , 1, 0) if logistic == True else y
    model.fit(X, yf)
    yH = model.predict(X)
    score = r2_score(yf, yH) if logistic == False else accuracy_score(yf, yH)
    return score

def PredictPreMovement(df, event):
    ef = df[df["event"] == event]
    X = ef["pre_R"].values.reshape(-1,1)
    o = ef["O"].values.reshape(-1,1)
    c = ef["C"].values.reshape(-1,1)
    y = (c-o)/o
    
    r2 = Fit(X,y, logistic=False)
    acc = Fit(X,y, logistic=True)
    cr = stats.pearsonr(X, y)
    return Estimates(event, len(y), r2, acc, cr)

if __name__ == '__main__':
    defaultResultFiles=["../results/ES_3600_60_600.csv",
                        "../results/TU_3600_60_600.csv",
                        "../results/UB_3600_60_600.csv"]

    parser = argparse.ArgumentParser(description='SocialNetworks CSV to HDF5')
    parser.add_argument('-i', '--input', nargs='+', default = defaultResultFiles)
    args = parser.parse_args()

    inFiles = args.input
    print("instrument,event,n,cr,r2,acc")
    for infile in inFiles:
        df = pd.read_csv(infile)
        eventV = sorted(df.event.unique())
        instr = os.path.basename(infile.split("_")[0])
        for i in range(len(eventV)):
            e = PredictPreMovement(df, eventV[i])
            print("%s,%s,%d,%f,%f,%f" % (instr, e.event, e.N, e.cr, e.r2, e.acc))


