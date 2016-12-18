import urllib.request, urllib.error, urllib.parse
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc
import matplotlib
import pylab
#from yahoo_finance import Share
from indicator import Indicator
from stock_puller import StockPuller
import pdb

class PlotTicker():
    def __init__(self):
        matplotlib.rcParams.update({'font.size': 9})
        self.indicator = Indicator()
        self.puller = StockPuller()

    def bytes_update2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter

    def graph_data(self, stock, MA1, MA2, date_range='1y'):
        try:
            stock_file = self.puller.pull_data(stock, date_range)

            if not stock_file:
                return None

            date, closep, highp, lowp, openp, volume = np.loadtxt(stock_file, delimiter=',', unpack=True,
                                                                  converters={ 0: self.bytes_update2num('%Y%m%d')})
            x = 0
            y = len(date)
            new_ar = []
            while x < y:
                append_line = date[x],openp[x],highp[x],lowp[x],closep[x],volume[x]
                new_ar.append(append_line)
                x+=1

            av1 = self.indicator.exp_moving_average(closep, MA1)
            av2 = self.indicator.exp_moving_average(closep, MA2)

            SP = len(date[MA2-1:])

            fig = plt.figure(figsize=(20,10), facecolor='#565353')

            ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#565353')
            candlestick_ohlc(ax1, new_ar[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

            Label1 = str(MA1)+' EMA'
            Label2 = str(MA2)+' EMA'

            ax1.plot(date[-SP:],av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
            ax1.plot(date[-SP:],av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)

            ax1.grid(True, color='w')
            ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.yaxis.label.set_color("w")
            ax1.spines['bottom'].set_color("#5998ff")
            ax1.spines['top'].set_color("#5998ff")
            ax1.spines['left'].set_color("#5998ff")
            ax1.spines['right'].set_color("#5998ff")
            ax1.tick_params(axis='y', colors='w')
            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
            ax1.tick_params(axis='x', colors='w')
            plt.ylabel('Stock price and Volume')

            maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                       fancybox=True, borderaxespad=0.)
            maLeg.get_frame().set_alpha(0.4)
            textEd = pylab.gca().get_legend().get_texts()
            pylab.setp(textEd[0:5], color = 'w')

            fig = pylab.gcf()
            fig.canvas.set_window_title(stock + \
                ' Daily scale' if date_range == '1y' else stock + ' Weekly Scale')

            volumeMin = 0

            ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#565353')
            rsi = self.indicator.rsi_func(closep)
            rsiCol = '#c1f9f7'
            posCol = '#386d13'
            negCol = '#8f2020'

            ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
            ax0.axhline(70, color=negCol)
            ax0.axhline(30, color=posCol)
            ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
            ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
            ax0.set_yticks([30,70])
            ax0.yaxis.label.set_color("w")
            ax0.spines['bottom'].set_color("#5998ff")
            ax0.spines['top'].set_color("#5998ff")
            ax0.spines['left'].set_color("#5998ff")
            ax0.spines['right'].set_color("#5998ff")
            ax0.tick_params(axis='y', colors='w')
            ax0.tick_params(axis='x', colors='w')
            plt.ylabel('RSI')

            ax1v = ax1.twinx()
            ax1v.fill_between(date[-SP:],volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.4)
            ax1v.axes.yaxis.set_ticklabels([])
            ax1v.grid(False)
            ###Edit this to 3, so it's a bit larger
            ax1v.set_ylim(0, 3*volume.max())
            ax1v.spines['bottom'].set_color("#5998ff")
            ax1v.spines['top'].set_color("#5998ff")
            ax1v.spines['left'].set_color("#5998ff")
            ax1v.spines['right'].set_color("#5998ff")
            ax1v.tick_params(axis='x', colors='w')
            ax1v.tick_params(axis='y', colors='w')
            ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#565353')
            fillcolor = '#00ffe8'
            nslow = 26
            nfast = 12
            nema = 16

            maslow, mafast, macd = self.indicator.compute_macd(closep)

            ma16 = self.indicator.moving_average(macd, nema)

            ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
            ax2.plot(date[-SP:], ma16[-SP:], color='#e1edf9', lw=1)
            #ax2.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
            ax2.spines['bottom'].set_color("#5998ff")
            ax2.spines['top'].set_color("#5998ff")
            ax2.spines['left'].set_color("#5998ff")
            ax2.spines['right'].set_color("#5998ff")
            ax2.tick_params(axis='x', colors='w')
            ax2.tick_params(axis='y', colors='w')
            plt.ylabel('MACD', color='w')
            ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
            for label in ax2.xaxis.get_ticklabels():
                label.set_rotation(45)

            plt.suptitle(stock.upper(),color='w')
            plt.setp(ax0.get_xticklabels(), visible=False)
            plt.setp(ax1.get_xticklabels(), visible=False)
            bbox_props = dict(boxstyle='round',fc='w', ec='k',lw=1)
            ax1.annotate(str(closep[-1]), (date[-1], closep[-1]),
            xytext = (date[-1]+4, closep[-1]), bbox=bbox_props)

            plt.subplots_adjust(left=.04, bottom=.10, right=.96, top=.95, wspace=.20, hspace=0)

            plt.show()

        except Exception as e:
            print('main loop',str(e))


if __name__ == '__main__':
    ticker = input("Enter a ticker :")
    plot_ticker = PlotTicker()
    plot_ticker.graph_data(ticker, 10, 20)


