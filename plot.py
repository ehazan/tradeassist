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

    def graph_data(self, stock, MA1, MA2):
        try:
            stock_file = self.puller.pull_data(stock)

            if stock == 'HEIA':
                pdb.set_trace()

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

            av1 = self.indicator.moving_average(closep, MA1)
            av2 = self.indicator.moving_average(closep, MA2)

            SP = len(date[MA2-1:])


            fig = plt.figure(figsize=(20,10), facecolor='#565353')

            ax1 = plt.subplot2grid((6,4), (0,0), rowspan=4, colspan=4, axisbg='#565353')
            candlestick_ohlc(ax1, new_ar[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

            Label1 = str(MA1)+' SMA'
            Label2 = str(MA2)+' SMA'

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
            fig.canvas.set_window_title(stock)

            volumeMin = 0

            ax2 = plt.subplot2grid((6,4), (4,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#565353')
            ax2.plot(date[-SP:], volume[-SP:], '#00ffe8', linewidth=.8)
            ax2.fill_between(date[-SP:], volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.5)
            ax2.axes.yaxis.set_ticks([])
            ax2.grid(True)
            ax2.spines['bottom'].set_color("#5998ff")
            ax2.spines['top'].set_color("#5998ff")
            ax2.spines['left'].set_color("#5998ff")
            ax2.spines['right'].set_color("#5998ff")
            ax2.tick_params(axis='x', colors='w')
            ax2.tick_params(axis='y', colors='w')

            plt.ylabel('Volume', color='w')

            ax3 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#565353')
            rsi = self.indicator.rsi_func(closep)
            rsi_col = '#c1f9f7'
            pos_col = '#386d13'
            neg_col = '#8f2020'

            ax3.plot(date[-SP:], rsi[-SP:], rsi_col, linewidth=1.5)
            ax3.axhline(70, color=neg_col)
            ax3.axhline(30, color=pos_col)
            ax3.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=neg_col, edgecolor=neg_col, alpha=0.5)
            ax3.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=pos_col, edgecolor=pos_col, alpha=0.5)
            ax3.set_yticks([30,70])

            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
            ax3.spines['bottom'].set_color("#5998ff")
            ax3.spines['top'].set_color("#5998ff")
            ax3.spines['left'].set_color("#5998ff")
            ax3.spines['right'].set_color("#5998ff")
            ax3.tick_params(axis='x', colors='w')
            ax3.tick_params(axis='y', colors='w')
            plt.ylabel('RSI', color='w')
            ax3.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))

            for label in ax3.xaxis.get_ticklabels():
                label.set_rotation(45)

            plt.suptitle(stock.upper(),color='w')
            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax2.get_xticklabels(), visible=False)


            plt.suptitle(stock.upper(),color='w')
            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax2.get_xticklabels(), visible=False)

            bbox_props = dict(boxstyle='round',fc='w', ec='k',lw=1)
            ax1.annotate(str(closep[-1]), (date[-1], closep[-1]),
            xytext = (date[-1]+4, closep[-1]), bbox=bbox_props)

            plt.subplots_adjust(left=.04, bottom=.10, right=.96, top=.95, wspace=.20, hspace=0)

            plt.show()
            fig.savefig('example.png',facecolor=fig.get_facecolor())

        except Exception as e:
            print('main loop',str(e))
