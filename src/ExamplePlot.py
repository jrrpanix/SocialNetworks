from ReadH5 import ReadH5
from Utils import Utils
from Events import Events
from PlotTickData import PlotEvent
import os

your_tick_data_dir=os.path.join(os.getenv("HOME"),"TickData/splits") # this will be set to whereever your local tickdata is
reader  = ReadH5(your_tick_data_dir, reportNoData=False)
ef = Events() # will load the events into a dataframe
symbol = "ES"
event = "Non-farm Payrolls"
window = 120 # 2 hours
approximateDate = "20190301" # we want the one in March
PlotEvent(event, approximateDate, symbol, window, ef, reader)
