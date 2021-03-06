import datetime
import numpy as np

class Utils:
    
    def tickSize(symbol):
        if symbol in ["ES", "NQ"] : return 0.25
        if symbol in ["US", "UB"] : return 1/32.0
        if symbol in ["FV", "TY"] : return 1/64.0
        if symbol in ["TU"] : return 1/128.0
        if symbol in ["EC"] : return 0.00005
        assert False, "Future %s not in Split Directory" % symbol

    def tickValue(symbol):
        if symbol in ["ES"] : return 12.50
        if symbol in ["NQ"] : return 20*0.25
        if symbol in ["US", "UB"] : return 1/32.0*1000
        if symbol in ["FV", "TY"] : return 1/64.0*1000
        if symbol in ["TU"] : return 1/128.0*2000
        if symbol in ["EC"] : return 0.00005*125000
        assert False, "Future %s not in Split Directory" % symbol

    def fmt(i=0,f=["%Y%m%d","%m-%d-%Y %H:%M:%S","%m-%d-%YT%H:%M:%S.%f","%Y%m%d %H%M%S"]):
        return f[i]

    def dt(dstr,i=0,f=None,np64=False):
        f = f if f is not None else Utils.fmt(i)
        dt=datetime.datetime.strptime(dstr, f)
        if np64:
            return np.datetime64(dt)
        return dt

    def todt(date):
        if type(date) == datetime.datetime : return date
        ts = (date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.datetime.utcfromtimestamp(ts)
        
