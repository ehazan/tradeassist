from indicator import Indicator
from stock_puller import StockPuller
import numpy as np
import matplotlib.dates as mdates
import argparse
import plot
import sys
import pdb

class Screener():
    def __init__(self, strategy, in_file):
        try:
            self.strategy = strategy
            self.in_file = in_file
            self.indicator = Indicator()
            self.puller = StockPuller()
            self.stock_list = []

            with open(self.in_file, 'r') as f_obj:
                stock_lines = f_obj.read()
                self.stock_list = stock_lines.split()
        except Exception as e:
            print("Failed to to read stock file :", in_file)


    def bytes_update2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter

    def eyeball(self):
        for stock in self.stock_list:
            plot_ticker = plot.PlotTicker()
            plot_ticker.graph_data(stock, 10, 50, '5y')
            plot_ticker.graph_data(stock, 10, 20, '1y')


    def screen(self):
        # Go through the list and plot the stock that meets the criteria
        for stock in self.stock_list:
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

def check_arg(args=None):
     parser = argparse.ArgumentParser(description=
             'Screening Tasks.')

     parser.add_argument('-s', '--screen',
             nargs=2,
             help='Performs scan by criteria: -s type_of_scan (all for entire list) file_name_to_scan')

     results = parser.parse_args(args)

     return results.screen

def main():
    screen = check_arg(sys.argv[1:])
    print(screen)
    if screen[0] == 'all':
        screener = Screener("General", screen[1])
        screener.eyeball()
    else:
        screener = Screener("General", screen[1])
        screener.screen()


if __name__ == '__main__':
    main()

