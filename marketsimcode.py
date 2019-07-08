

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data, plot_data

def compute_portvals(orders,  start_val = 1000000, commission=9.95, impact=0.005):

    og_orders = orders
    #print og_orders
    #sort og_order by index date
    order = og_orders.sort_index();
    #print order
    index = order.index;
    start_date, end_date = index.min(), index.max()
    #print start_date, end_date
    symbols = list(order.Symbol.unique())
    #print symbols
    price = get_data(symbols, pd.date_range(start_date, end_date), addSPY=True, colname='Adj Close');
    price["CASH"] = 1.0
    del price["SPY"]
    price.fillna(method="ffill", inplace=True)
    price.fillna(method="bfill", inplace=True)
    #print price
    tradeZero = np.zeros(price.shape);
    trade = pd.DataFrame(tradeZero, price.index, price.columns)
    #print trade
    for index, row in order.iterrows():
        if row["Shares"] <= 0:
            print "negative shares!"
        if row["Order"] == "SELL":
            #print trade.loc[index, "CASH"]
            trade.loc[index, "CASH"] = trade.loc[index, "CASH"] + price.loc[index, row["Symbol"]]*(1-impact) * row["Shares"] - commission
            # print trade.loc[index, "CASH"]
            #print trade.loc[index, row["Symbol"]], row["Shares"]
            trade.loc[index, row["Symbol"]] = trade.loc[index, row["Symbol"]] - row["Shares"]
            #print trade.loc[index, row["Symbol"]]
        elif row["Order"] == "BUY":
            # print trade.loc[index, "CASH"]
            trade.loc[index, "CASH"] = trade.loc[index, "CASH"] - price.loc[index, row["Symbol"]] * (1 + impact) * row[
                "Shares"] - commission
            # print trade.loc[index, "CASH"]
            # print trade.loc[index, row["Symbol"]], row["Shares"]
            trade.loc[index, row["Symbol"]] = trade.loc[index, row["Symbol"]] + row["Shares"]
            # print trade.loc[index, row["Symbol"]]
        else:
            print "Wrong order type!"
    #print trade
    holding = pd.DataFrame(tradeZero, price.index, price.columns)
    for k in range(len(holding)):
        if k !=0 :
            holding.ix[k] = holding.ix[k] + holding.ix[k-1]
        elif k == 0 :
            holding.ix[0, -1] = holding.ix[0, -1] + start_val
            holding.ix[0, :-1] = trade.ix[0, :-1]

    #print holding
    value = price * holding
    #print value
    return pd.DataFrame(value.sum(axis=1), value.index, ["Portfolio_Value"])


if __name__ == "__main__":
    print "marketsim"