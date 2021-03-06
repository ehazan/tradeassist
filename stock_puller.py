import urllib.request, urllib.error, urllib.parse
import matplotlib.dates as mdates
from yahoo_finance import Share
import numpy as np
import pdb

class StockPuller():
    def __init_(self):
        pass

    def pull_data(self, stock, date_range):
        print('Currently Pulling',stock)
        url_to_visit = 'http://chartapi.finance.yahoo.com/instrument/1.0/' \
                        +stock+'/chartdata;type=quote;range='+date_range+'/csv'

        try:
            data = []
            source_code = urllib.request.urlopen(url_to_visit).read().decode()
            split_source = source_code.split('\n')
            
            # Search for data reading errors
            for word in split_source:
                if 'errorid' in word:
                    print("Error reading data for :", stock)
                    return None

            for each_line in split_source:
                split_line = each_line.split(',')
                if len(split_line)==6 and split_line[0].isnumeric():
                    if 'values' not in each_line:
                        data.append(each_line)

            if data is None:
                return None

            # Update last day
            share_today = Share(stock)

            try:
                if share_today:
                    tm = share_today.get_trade_datetime().split()[0]
                    today_date = tm.replace("-","")

                    l_date = data[-1].split(',')[0]

                    if data and l_date < today_date:
                        today_close_price = share_today.get_price()
                        today_high_price = share_today.get_days_high()
                        today_low_price = share_today.get_days_low()
                        today_open_price = share_today.get_open()
                        today_volume = share_today.get_volume()

                        if today_close_price != None and today_high_price != None and \
                           today_open_price != None and today_volume != None:

                           last_row = today_date+','+ today_close_price+',' \
                                   +today_high_price+','+today_low_price +',' \
                                   +today_open_price+','+today_volume

                           data.append(last_row)
            except Exception as e:
                print("Error occured while accessing last date ", e)
            
            return data

        except Exception as e:
            pdb.set_trace()
            print(str(e), 'failed to organize pulled data.')
