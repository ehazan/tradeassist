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
from yahoo_finance import Share
import pdb



class PlotTicker():
    def __init__(self):
        matplotlib.rcParams.update({'font.size': 9})

    def rsiFunc(self, prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed>=0].sum()/n
        down = -seed[seed<0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1.+rs)

        for i in range(n, len(prices)):
            delta = deltas[i-1] # cause the diff is 1 shorter

            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(n-1) + upval)/n
            down = (down*(n-1) + downval)/n

            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)

        return rsi

    def moving_average(self, values, window):
        weigths = np.repeat(1.0, window)/window
        smas = np.convolve(values, weigths, 'valid')
        return smas # as a numpy array


    def exp_moving_average(self, values, window):
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        a =  np.convolve(values, weights, mode='full')[:len(values)]
        a[:window] = a[window]
        return a


    def computeMACD(self, x, slow=26, fast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.exp_moving_average(x, slow)
        emafast = self.exp_moving_average(x, fast)
        return emaslow, emafast, emafast - emaslow


    def bytespdate2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter


    def on_move(self, event):
        # get the x and y pixel coords
        x, y = event.x, event.y

        if event.inaxes:
            ax = event.inaxes  # the axes instance
            print('data coords %f %f' % (event.xdata, event.ydata))

    def on_click(self, event):
        # get the x and y coords, flip y from top to bottom
        x, y = event.x, event.y
        if event.button == 1:
            if event.inaxes is not None:
                print('data coords %f %f' % (event.xdata, event.ydata))



    def graph_data(self, stock, MA1, MA2):

        '''
            Use this to dynamically pull a stock:
        '''
        try:
            print('Currently Pulling',stock)
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1y/csv'
            stockFile =[]
            try:
                sourceCode = urllib.request.urlopen(urlToVisit).read().decode()
                splitSource = sourceCode.split('\n')
                for eachLine in splitSource:
                    splitLine = eachLine.split(',')
                    if len(splitLine)==6:
                        if 'values' not in eachLine:
                            stockFile.append(eachLine)
                # Update last day
                share_today = Share(stock)
                tm = share_today.get_trade_datetime().split()[0]
                today_date = tm.replace("-","")

                l_date = stockFile[-1].split(',')[0]

                if l_date != today_date:
                    today_close_price = share_today.get_price()
                    today_high_price = share_today.get_days_high()
                    today_low_price = share_today.get_days_low()
                    today_open_price = share_today.get_open()
                    today_volume = share_today.get_volume()
                    last_row = today_date+','+ today_close_price+','+today_high_price+','+today_low_price +','+today_open_price+','+today_volume
                    stockFile.append(last_row)

            except Exception as e:
                print(str(e), 'failed to organize pulled data.')
        except Exception as e:
            print(str(e), 'failed to pull pricing data')

        try:
            date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile, delimiter=',', unpack=True,
                                                                  converters={ 0: self.bytespdate2num('%Y%m%d')})
            x = 0
            y = len(date)
            newAr = []
            while x < y:
                appendLine = date[x],openp[x],highp[x],lowp[x],closep[x],volume[x]
                newAr.append(appendLine)
                x+=1

            Av1 = self.moving_average(closep, MA1)
            Av2 = self.moving_average(closep, MA2)

            SP = len(date[MA2-1:])


            fig = plt.figure(figsize=(20,10), facecolor='#565353')

            ax1 = plt.subplot2grid((6,4), (0,0), rowspan=4, colspan=4, axisbg='#565353')
            candlestick_ohlc(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

            Label1 = str(MA1)+' SMA'
            Label2 = str(MA2)+' SMA'

            ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
            ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)

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
            rsi = self.rsiFunc(closep)
            rsiCol = '#c1f9f7'
            posCol = '#386d13'
            negCol = '#8f2020'

            ax3.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
            ax3.axhline(70, color=negCol)
            ax3.axhline(30, color=posCol)
            ax3.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
            ax3.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
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
            #plt.subplots_adjust(left=0.11, bottom=0.24, right=0.87, top=0.90, wspace=0.2, hspace=0)



            plt.subplots_adjust(left=.04, bottom=.10, right=.96, top=.95, wspace=.20, hspace=0)

    ###########################
            #binding_id = plt.connect('motion_notify_event', on_move)
            #plt.connect('button_press_event', on_click)
    ###############

            plt.show()
            fig.savefig('example.png',facecolor=fig.get_facecolor())

        except Exception as e:
            print('main loop',str(e))

    #while True:
        #stock = input('Stock to plot: ')
        #graph_data(stock,10,50)
