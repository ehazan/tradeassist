from indicator import Indicator
from stock_puller import StockPuller
import numpy as np
import matplotlib.dates as mdates
import plot
import pdb

class Screener():
    def __init__(self, strategy, in_file):
        self.strategy = strategy
        self.in_file = in_file
        self.indicator = Indicator()
        self.puller = StockPuller()

    def bytes_update2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter

    def screen(self):
        # Go through the list and plot the stock that meets the criteria
        with open(self.in_file, 'r') as f_obj:
            stock_lines = f_obj.read()
            stock_list = stock_lines.split()
            for stock in stock_list:
                stock_file = self.puller.pull_data(stock)

                if not stock_file:
                    continue

                date, closep, highp, lowp, openp, volume = np.loadtxt(stock_file, delimiter=',', unpack=True,
                                                                  converters={ 0: self.bytes_update2num('%Y%m%d')})
                hh, _ = self.indicator.hh_ll(closep, 5)

                vol_ma = self.indicator.moving_average(volume, 20)

                rsi = self.indicator.rsi_func(closep)
                if  hh[-1] == closep[-1] and volume[-1] > vol_ma[-1]*2 and rsi[-1] > 80 : # overbought
                    plot_ticker = plot.PlotTicker()
                    plot_ticker.graph_data(stock, 12, 22)

if __name__ == '__main__':
    file_name = input("Enter file name: ")
    screener = Screener("stam", file_name)
    screener.screen()

