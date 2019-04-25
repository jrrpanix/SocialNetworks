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

    def __init__(self, instr, event, N, r2, acc, acc_svm, cr, s, meanX, label):
        self.instr = instr
        self.event = event
        self.N = N   # number of obs
        self.r2 = r2 # r squared
        self.acc = acc # accuracy logistic regression
        self.acc_svm = acc_svm # accuracy logistic regression
        self.cr = cr # correlation coeff
        self.s = s # std dev of response
        self.meanX = np.abs(meanX)
        self.label = label


def runFits(X, y, event, instr, label):
    def Fit(X, y, model, scoreF, classification= True):
        yf = np.where(y > 0 , 1, 0) if classification == True else y
        if np.sum(yf) == len(yf) or np.sum(yf) == 0: return 0
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
    return Estimates(instr, event, len(y), r2, acc, acc_svm, cr, sy/sx, np.mean(X), label)

def postEventReturn(ef):
    o = ef["O"].values
    c = ef["C"].values
    y = (c-o)/o
    return y
 
def RunPreMove(inFiles):
    inFiles = args.input
    print("%-3s, %-25s, %9s, %7s, %7s, %4s, %4s, %7s, %7s" % 
          ("I", "EVENT", "pR:1s/as", "acc1sd","accall","n1sd","nall", "r21sd", "r2all"))
    for infile in inFiles:
        df = pd.read_csv(infile)
        df["post_R"] = postEventReturn(df)
        eventV = sorted(df.event.unique())
        instr = os.path.basename(infile.split("_")[0])
        allCount, sCount = 0, 0
        for i in range(len(eventV)):
            event = eventV[i]
            ef = df[df["event"] == event]
            X = ef["pre_R"].values.reshape(-1,1)
            y = ef["post_R"].values
            eAll = runFits(X, y, event, instr, "ALL-MOVES")

            big_T = ef["T"].mean()  + ef["T"].std()
            ef = ef[ef["T"] > big_T]
            X = ef["pre_R"].values.reshape(-1,1)
            y = ef["post_R"].values
            e1Std = runFits(X, y, event, instr, "1STD-MOVES")
            ratio = e1Std.meanX / eAll.meanX
            if e1Std.acc_svm > .1:
                print("%-3s, %-25s, %9.2f, %7.5f, %7.5f, %4d, %4d, %7.5f, %7.5f" % 
                      (instr, event, ratio, e1Std.acc_svm, eAll.acc_svm, e1Std.N, eAll.N, e1Std.r2, eAll.r2))



if __name__ == '__main__':
    defaultResultFiles=["../results/ES_3600_60_600.csv","../results/TU_3600_60_600.csv","../results/UB_3600_60_600.csv"]
    parser = argparse.ArgumentParser(description='SocialNetworks CSV to HDF5')
    parser.add_argument('-i', '--input', nargs='+', default = defaultResultFiles)
    parser.add_argument('--model', default = "pre")
    args = parser.parse_args()
    if args.model == "pre":
        RunPreMove(args.input)
    


