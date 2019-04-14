# SocialNetworks
SocialNetworksProject

# Setting up the enviornment

1) Copy the .h5 files on the shared drive in the folder to some folder on your host
The shared folder name is called splits, assume you copy this to ~/splits

2) Plot some sample data
In the ./src directory there is a python program called PlotTickData.py, to plot some data

python ./PlotTickData.py -d 20190308 -t 073000 -s ES --title NFP --dataDir ~/splits/

This will plot the ES contract on March 8th at 7:30 am Central Time

3) ReadH5.py

This utility will find the correct .h5 file for a symbol and load it. It will keep it cached so if you load over multiple dates iit will not reload the data.

from ReadH5 import ReadH5

This will load the tick data which contains the date in dt. Each .h5 file contains several months of trade data but is easy to look up by date.

dt = datetime.datetime(2019, 3, 8, 7, 30, 0)
reader  = ReadH5(args.dataDir, reportNoData=False)
df = reader.readh5(args.symbol, dt)

Get 2 hours of data around the "datetime", dt.

before = dt - datetime.timedelta(minutes=120)
after = dt + datetime.timedelta(minutes=120)

then you can shrink the dataframe df by the following commands

 df = df[df["dt"] > before]
 df = df[df["dt"] < after]
 
 
