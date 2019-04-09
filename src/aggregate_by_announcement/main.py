import sys
import group

def main():
    if len(sys.argv) < 2:
        print("Error : usage <ohlc_file.csv.gz>")
        quit()
    records = group.record_reader(sys.argv[1])
    events = group.event_reader("../../data/announcements-dailyfx.csv")
    # records and events are iterable of OHLC and Announcement objects in ascending order
    # before and after are lists of OHLC objects from 10 minutes before to 60 minutes after
    # announcement has properties datatime, currency, title, priority, actual, forecast, previous
    for (announcement, before, after) in group.group(events, records, 10, 60):
        if before and after:
            bfchange = max(before, key=lambda x: x.H).H - min(before, key=lambda x: x.L).L
            afchange = max(after, key=lambda x: x.H).H - min(after, key=lambda x: x.L).L
            print(announcement.datetime, announcement.title, bfchange, afchange)
    
if __name__ == '__main__':
    main()