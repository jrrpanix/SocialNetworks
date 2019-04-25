import numpy as np
import pandas as pd
import argparse
import os
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import r2_score
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt
from scipy import stats

"""
  Determine if the pre-event price movement is a predictor of event 
  price movement.  

"""


class Estimates:

    def __init__(self, event, N, r2, acc, acc_svm, cr, s):
        self.event = event
        self.N = N   # number of obs
        self.r2 = r2 # r squared
        self.acc = acc # accuracy logistic regression
        self.acc_svm = acc_svm # accuracy logistic regression
        self.cr = cr # correlation coeff
        self.s = s # std dev of response


def runFits(X, y, event=None):
    def Fit(X, y, model, scoreF, classification= True):
        yf = np.where(y > 0 , 1, 0) if classification == True else y
        model.fit(X, yf)
        yH = model.predict(X)
        score = scoreF(yf, yH)
        return score

    r2 = Fit(X,y, model=LinearRegression(), scoreF=r2_score, classification=False)
    acc = Fit(X,y, model=LogisticRegression(solver='lbfgs'), scoreF=accuracy_score, classification=True)
    acc_svm = Fit(X,y, model=LinearSVC(), scoreF=accuracy_score, classification=True)
    cr = stats.pearsonr(X, y.reshape(-1,1))[0]
    sy = np.std(y)
    sx = np.std(X)
    return Estimates(event, len(y), r2, acc, acc_svm, cr, sy/sx)

def postEventReturn(ef):
    o = ef["O"].values
    c = ef["C"].values
    y = (c-o)/o
    return y
 
def RunPreMove(inFiles):
    inFiles = args.input
    print("instrument,event,n,cr,r2,acc,acc_svm,std")
    for infile in inFiles:
        df = pd.read_csv(infile)
        eventV = sorted(df.event.unique())
        instr = os.path.basename(infile.split("_")[0])
        for i in range(len(eventV)):
            event = eventV[i]
            ef = df[df["event"] == event]
            X = ef["pre_R"].values.reshape(-1,1)
            y = postEventReturn(ef)
            e = runFits(X, y, event)
            print("%s,%s,%d,%f,%f,%f,%f,%f" % (instr, e.event, e.N, e.cr, e.r2, e.acc, e.acc_svm, e.s))
    


if __name__ == '__main__':
    defaultResultFiles=["../results/ES_3600_60_600.csv","../results/TU_3600_60_600.csv","../results/UB_3600_60_600.csv"]
    parser = argparse.ArgumentParser(description='SocialNetworks CSV to HDF5')
    parser.add_argument('-i', '--input', nargs='+', default = defaultResultFiles)
    parser.add_argument('--model', default = "pre")
    args = parser.parse_args()
    if args.model == "pre":
        RunPreMove(args.input)
    


