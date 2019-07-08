
import StrategyLearner as sl
import datetime as dt
import pandas as pd
import util as ut
import matplotlib.pyplot as plt

def strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000):
    learner = sl.StrategyLearner(verbose=False, impact=0.000)
    return learner.addEvidence(symbol=symbol, sd=sd, ed=ed, sv=sv)

def long_short_result(symbol=['JPM'], sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000):
    dates = pd.date_range(sd, ed)
    prices_all = ut.get_data(symbol, dates)
    prices_all.fillna(method='ffill', inplace=True);
    prices_all.fillna(method='bfill', inplace=True);
    prices = prices_all[symbol]

    normalp = prices / prices.ix[0, :]
    alloced = normalp * 1
    pos_vals = alloced * sv
    port_val = pos_vals.sum(axis=1)

    return port_val


if __name__=="__main__":
    sl_result, trade_num = strategyLearner_result()
    ls_result = long_short_result()
    plt.title('Strategy Learner vs Benchmark Symbol JPM')
    plt.ylabel('Price')
    plt.xlabel('Date')
    l1, = plt.plot(ls_result.index, ls_result, 'r--', label="Benchmark")
    l2, = plt.plot(sl_result.index, sl_result, 'b--', label="Strategy Learner")
    plt.legend(loc='lower right')
    plt.savefig('exp1.png')
    plt.clf()