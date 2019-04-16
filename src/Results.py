import argparse
import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Dates')
    parser.add_argument('-i','--inputFile')
    parser.add_argument('-o','--output')
    args = parser.parse_args()

    df=pd.read_csv(args.inputFile)
    g=df.groupby(['event'])
    a=g.agg({
            'date':['min','max'],
            'T':['max','mean','std', 'count'],
            'pre_T':['max','mean','std'],
            'R':['max','min','mean','std'],
            'pre_R':['max','min','mean','std'],
            'TD':['max','mean'],
            'V':['mean'],
            'pre_V':['mean']
             })
    print(a.columns)
    d2=pd.DataFrame(data=a)
    d2.to_csv(args.output)
    

    
