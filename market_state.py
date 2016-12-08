import numpy as np
import matplotlib.dates as mdates
from enum import Enum
from indicator import Indicator
from stock_puller import StockPuller

class MarketState():
    def __init__(self):
        self.market_condition = Enum('market_condition', \
                ['none' ,'uptrend', 'sideways', 'downtrend'])
        self.indicator = Indicator()
        self.puller = StockPuller()

    #TODO: To move this function into Indicator or Puller class
    def bytes_update2num(self, fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)
        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)
        return bytesconverter

    def get_todays_ma(self ,stock, type, period):
        stock_file = self.puller.pull_data(stock)

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

        ma = self.indicator.moving_average(closep, period) if type == 'simple' else \
             self.indicator.exp_moving_average(closep, period)

        return ma[-1], closep[-1]

    def get_state(self):
        iwm_10_ema, closep_iwm = self.get_todays_ma('IWM', 'exponetial', 10)
        spy_10_ema, closep_spy = self.get_todays_ma('SPY', 'exponetial', 10)
        mdy_10_ema, closep_mdy = self.get_todays_ma('MDY', 'exponetial', 10)
        qqq_10_ema, closep_qqq = self.get_todays_ma('QQQ', 'exponetial', 10)

        spy_50_sma, _  = self.get_todays_ma('SPY', 'exponetial', 50)
        mdy_50_sma, _  = self.get_todays_ma('MDY', 'exponetial', 50)
        iwm_50_sma, _  = self.get_todays_ma('IWM', 'exponetial', 50)
        qqq_50_sma, _  = self.get_todays_ma('QQQ', 'exponetial', 50)

        if closep_iwm > iwm_10_ema and closep_spy > spy_50_sma and \
           closep_mdy > mdy_50_sma and closep_qqq > qqq_50_sma and \
           closep_iwm > iwm_50_sma:
           self.market_condition = 'uptrend'
        elif closep_iwm < iwm_10_ema and closep_spy < spy_50_sma and \
             closep_mdy < mdy_10_ema and closep_mdy < mdy_50_sma and \
             closep_qqq < qqq_10_ema and closep_qqq < qqq_50_sma and \
             closep_spy < spy_10_ema and closep_spy < spy_50_sma:
             self.market_condition = 'uptrend'
        else:
            self.market_condition = 'sideways'

        return self.market_condition

def main():
    state = MarketState()
    print('Market condition today : {}'.format(state.get_state()))

if __name__ == '__main__':
    main()




