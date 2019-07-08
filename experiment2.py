

import StrategyLearner as sl
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

def strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31), sv=100000, impact=0.000):
    learner = sl.StrategyLearner(verbose=False, impact = impact)
    return learner.addEvidence(symbol=symbol, sd=sd, ed=ed, sv=sv)

def assess_portfolio(port_val, rfr=0.0, sf=252.0):

    cr = (port_val[-1]/port_val[0])-1

    daily_ret = (port_val/port_val.shift(1))-1
    daily_ret = daily_ret[1:]
    adr = daily_ret.mean()
    sddr = daily_ret.std()
    # Get portfolio statistics (note: std_daily_ret = volatility)
    sr = np.sqrt(sf)*(adr-rfr)/sddr
    ev = port_val[-1]

    return cr, adr, sddr, sr, ev


if __name__=="__main__":
    sl_result_im0, trade_num0 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1),
                                                       ed=dt.datetime(2009, 12, 31), sv=100000, impact=0.000)

    sl_result_im002, trade_num002 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1),
                                                       ed=dt.datetime(2009, 12, 31), sv=100000, impact=0.02)

    sl_result_im004, trade_num004 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31),
                                           sv=100000, impact=0.04)

    sl_result_im006, trade_num006 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31),
                                           sv=100000, impact=0.06)

    sl_result_im008, trade_num008 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31),
                                            sv=100000, impact=0.08)

    sl_result_im010, trade_num010 = strategyLearner_result(symbol="JPM", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31),
                                            sv=100000, impact=0.10)


    print trade_num0, trade_num002, trade_num004, trade_num006, trade_num008, trade_num010


    plt.title('Strategy Learner Symbol JPM With Various Impact')
    plt.ylabel('Price')
    plt.xlabel('Date')
    l1, = plt.plot(sl_result_im0.index, sl_result_im0, 'r--', label="Impact = 0")
    l2, = plt.plot(sl_result_im002.index, sl_result_im002, 'b--', label="Impact = 0.02")
    l3, = plt.plot(sl_result_im004.index, sl_result_im004, 'g--', label="Impact = 0.04")
    l4, = plt.plot(sl_result_im006.index, sl_result_im006, 'k--', label="Impact = 0.06")
    l5, = plt.plot(sl_result_im008.index, sl_result_im008, 'c--', label="Impact = 0.08")
    l6, = plt.plot(sl_result_im010.index, sl_result_im010, 'm--', label="Impact = 0.10")
    plt.legend(loc='lower right')
    plt.savefig('exp2.png')
    plt.clf()