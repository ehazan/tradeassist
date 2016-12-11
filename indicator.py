import numpy as np
import pdb

class Indicator():
    def __init__(self):
        pass

    def hh_ll(self, closep, tf):
        hh = []
        ll = []
        x = tf

        while x <= len(closep):
            cons_high = closep[x-tf:x]
            cons_low = closep[x-tf:x]

            highest_high = max(cons_high)
            lowest_low = min(cons_low)

            hh.append(highest_high)
            ll.append(lowest_low)
            
            x+=1

        return hh, ll

    def rsi_func(self, prices, n=14):
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

