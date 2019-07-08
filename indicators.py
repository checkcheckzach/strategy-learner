
import numpy as np
import pandas as pd
import datetime as dt
import util as ut
import matplotlib.pyplot as plt

class indicators(object):

    # constructor
    def __init__(self, verbose=False, window = 8):
        self.verbose = verbose
        self.window = window

    def cal_psma(self, price, rolling_mean):
        return price / rolling_mean - 1
    def cal_bollinger_value(self, price, rolling_mean, rolling_std):
        top_band = rolling_mean + 2*rolling_std
        bottom_band = rolling_mean - 2*rolling_std
        return (price - bottom_band ) / (top_band - bottom_band)

    def cal_momentum(self, price):
        #momentum = pd.Series(np.nan, index=price.index)
        momentum = price/price.shift(self.window) -1
        return momentum


    def combine_all_indicators(self, price):
        r_mean = price.rolling(window = self.window, min_periods = self.window).mean()
        r_std =  price.rolling(window = self.window, min_periods = self.window).std()
        psma = self.cal_psma(price, r_mean)
        bollinger_val = self.cal_bollinger_value(price, r_mean, r_std)
        momentum = self.cal_momentum(price)
        all_indicators = pd.concat([momentum , psma], axis = 1)
        all_indicators = pd.concat([all_indicators, bollinger_val], axis=  1)
        all_indicators.columns = ["indicator{}".format(i)
                               for i in range(len(all_indicators.columns))]
        all_indicators.dropna(inplace = True)
        #all_indicators.fillna(method='bfill', inplace=True);
        return all_indicators

    def cal_thresholds(self, all_indicators, num_bins):
        data_length = all_indicators.shape[0]
        step_size = int(round(data_length / num_bins))
        thresholds = np.zeros(shape=(all_indicators.shape[1], num_bins))
        ind_copy = all_indicators.copy()
        for i, ind in enumerate(all_indicators.columns):
            ind_copy.sort_values(by=[ind], inplace=True)
            for j in range(0, num_bins):
                if j == (num_bins - 1):
                    thresholds[i, j] = ind_copy[ind].iloc[-1]
                elif j < num_bins - 1:
                    thresholds[i, j] = ind_copy[ind].iloc[(j + 1) * step_size]

        if self.verbose: print thresholds

        return thresholds

if __name__=="__main__":
    print "plot the indicators"

    symbol = "JPM"
    syms = [symbol]
    sd = dt.datetime(2008, 1, 1)
    ed = dt.datetime(2009, 12, 31)
    dates = pd.date_range(sd, ed)
    prices_all = ut.get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    normalp = prices / prices.ix[0, :];
    indicator = indicators(verbose=False, window=8)

    #momentum
    momentum = indicator.cal_momentum(prices);
    momentum.dropna(inplace=True)
    normalm = momentum / momentum.ix[0, :];
    plt.title('Momentum Window = 8 Indicator')
    plt.ylabel('Value')
    plt.xlabel('Date')
    l1, = plt.plot(normalm.index, normalm, 'b--', label="Momentum")
    plt.legend(loc='lower right')
    plt.savefig('momen.png')
    plt.clf()

    #p/sma
    sma = prices .rolling(window=8, min_periods=8).mean()
    sma.dropna(inplace=True)
    nsma =  sma /sma.ix[0, :];
    psma = indicator.cal_psma(prices,sma)
    psma.dropna(inplace=True)
    npsma = psma / psma.ix[0, :];
    plt.title('psma, sma, price Window = 8 Indicator')
    plt.ylabel('Value')
    plt.xlabel('Date')
    l1, = plt.plot(prices.index, prices, 'b--', label="Price")
    l2, = plt.plot(sma.index, sma, 'r--', label="SMA")
    l3, = plt.plot(psma.index, psma, 'k--', label="Price/SMA")
    plt.legend(loc='lower right')
    plt.savefig('psma1.png')
    plt.clf()


    plt.title('psma Window = 8 Indicator')
    plt.ylabel('Value')
    plt.xlabel('Date')
    l1, = plt.plot(psma.index, psma, 'k--', label="Price/SMA")
    plt.legend(loc='lower right')
    plt.savefig('psma2.png')
    plt.clf()

    #bollinger_value
    r_mean = prices.rolling(window=8, min_periods=8).mean()
    r_std = prices.rolling(window=8, min_periods=8).std()
    top_band = r_mean + 2 * r_std
    bottom_band = r_mean - 2 * r_std
    bollinger_value = indicator.cal_bollinger_value(prices,r_mean, r_std)
    bollinger_value.dropna(inplace=True)
    plt.title('Price Value with Bollinger Band Window = 8 Indicator')
    plt.ylabel('Value')
    plt.xlabel('Date')
    l1, = plt.plot(prices.index, prices, 'k--', label="Price")
    l2, = plt.plot(bottom_band.index, bottom_band, 'r--', label="Bottom Band")
    l3, = plt.plot(top_band.index, top_band, 'b--', label="Top Band")
    plt.legend(loc='lower right')
    plt.savefig('bv1.png')
    plt.clf()

    plt.title('Bollinger Value Window = 8 Indicator')
    plt.ylabel('Value')
    plt.xlabel('Date')
    l1, = plt.plot(bollinger_value.index, bollinger_value, 'k--', label="Bollinger Value")
    plt.legend(loc='lower right')
    plt.savefig('bv2.png')
    plt.clf()
