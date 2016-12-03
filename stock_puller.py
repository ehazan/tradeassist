import matplotlib.dates as mdates
import numpy as np

class StockPuller():

    def __init(self)__:
        self.stock_file = []
        pass

    def bytes_update2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter

    def pull_stock(stock):
        url_to_visit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1y/csv'
        try:
            source_code = urllib.request.urlopen(url_to_visit).read().decode()
            split_source = source_code.split('\n')
            for each_line in split_source:
                split_line = each_line.split(',')
                if len(split_line)==6:
                    if 'values' not in each_line:
                        self.stock_file.append(each_line)
            # Update last day
            share_today = Share(stock)
            tm = share_today.get_trade_datetime().split()[0]
            today_date = tm.replace("-","")

            l_date = self.stock_file[-1].split(',')[0]

            if l_date != today_date:
                today_close_price = share_today.get_price()
                today_high_price = share_today.get_days_high()
                today_low_price = share_today.get_days_low()
                today_open_price = share_today.get_open()
                today_volume = share_today.get_volume()
                last_row = today_date+','+ today_close_price+','+today_high_price+','+today_low_price +','+today_open_price+','+today_volume
                stock_file.append(last_row)

            return np.loadtxt(self.stock_file, delimiter=',', unpack=True,
                              converters={ 0: self.bytes_update2num('%Y%m%d')})


        except Exception as e:
            print(str(e), 'failed to organize pulled data.')

