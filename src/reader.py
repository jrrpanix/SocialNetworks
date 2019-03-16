import gzip
import sys
import os
import binascii
import datetime


def getDateTime(d, t):
    dv = d.split("/")
    tv = t.split(":")
    try:
        h,m,s,us = int(tv[0]), int(tv[1]), int(tv[2].split(".")[0]), int(tv[2].split(".")[-1])*1000
    except:
        print("error", t, d)
        return datetime.datetime(2018,1,1)
    return datetime.datetime(int(dv[2]), int(dv[0]), int(dv[1]), h,m,s,us)

def main():
    assert len(sys.argv) > 1
    fname = sys.argv[1]
    assert os.path.exists(fname)
    with gzip.open(fname) as fr:
        p29 , p30, p31 = False, False, False
        for i, line in enumerate(fr):
            if i == 0 : continue
            data = line.decode('ascii')
            data = data.strip()
            dv = data.split(",")
            dt = getDateTime(dv[0], dv[1])
            px , qty = float(dv[2]), float(dv[3])
            if dt.weekday() == 4 and dt.month == 4:
                if dt.hour == 7:
                    if dt.minute == 29 and not p29:
                        print(dt, px, qty, dt.weekday())
                        p29 = True
                    if dt.minute == 30 and not p30:
                        print(dt, px, qty, dt.weekday())
                        p30 = True
                    if dt.minute == 31 and not p31:
                        print(dt, px, qty, dt.weekday())
                        p31 = True
                        break
            

if __name__ == '__main__':
    main()
