

import numpy as np
import datetime as dt
import pandas as pd
import util as ut
import indicators as ind
import QLearner as ql
from marketsimcode import compute_portvals

class StrategyLearner(object):
    SHORT_POS = -1
    LONG_POS = 1
    CASH_POS = 0

    SELL = -1
    BUY = 1
    HOLD = 0

    # constructor
    def __init__(self, verbose = False, impact=0, window = 8, epochs = 250, num_bins = 10, fix_shares = 1000,
                 converge_end = 5, num_states = 3500, num_actions = 3, **kwargs):
        self.verbose = verbose
        self.impact = impact
        self.window = window
        self.epochs = epochs
        self.num_bins = num_bins
        self.num_states = num_states
        self.num_actions = num_actions
        self.indicator = ind.indicators(verbose = False, window = self.window)
        self.qlearner = ql.QLearner(num_states = self.num_states, num_actions = self.num_actions, **kwargs)
        self.fix_shares = fix_shares
        self.converge_end =  converge_end

    def check_converge(self, crs):
        end_returns = crs[-self.converge_end:]
        avg = np.mean(end_returns)
        if all(x == end_returns[0] for x in end_returns):
            return True
        elif avg == crs[-1:]:
            return True
        else:
            return False

    def next_position(self, action, cur_pos):
        if action == self.SELL and cur_pos > self.SHORT_POS:
            next_pos = self.SHORT_POS
        elif action == self.BUY and cur_pos < self.LONG_POS:
            next_pos = self.LONG_POS
        else:
            next_pos = self.CASH_POS
        return next_pos

    def discretize(self, day_indicators, thresholds, position):

        position = position+1
        state = position * pow(self.num_bins, len(day_indicators))
        for i in range(len(day_indicators)):
            threshold = thresholds[i][thresholds[i] >= day_indicators[i]][0]
            threshold_i = np.where(thresholds == threshold)[1][0]
            state += threshold_i * pow(self.num_bins, i)
        return state



    def transfer_df_trades(self, all_trade, symbol):
        final_trade = pd.DataFrame(columns=['Shares', 'Order', 'Symbol'])
        for date in all_trade.index:
            if all_trade.loc[date] == self.CASH_POS:
                continue
            elif all_trade.loc[date] == self.LONG_POS:
                new_row = pd.DataFrame([[self.fix_shares, 'BUY', symbol], ], columns=['Shares', 'Order', 'Symbol'],
                                       index=[date, ])
                final_trade = final_trade.append(new_row)
            elif all_trade.loc[date] == self.SHORT_POS:
                new_row = pd.DataFrame([[self.fix_shares, 'SELL', symbol], ], columns=['Shares', 'Order', 'Symbol'], index=[date, ])
                final_trade = final_trade.append(new_row)
            #print  final_trade.shape[0], final_trade.shape[1]
        return final_trade

    def get_df_trades(self, all_trade):
        final_trade = pd.DataFrame(columns=['Shares'])
        for date in all_trade.index:
            if all_trade.loc[date] == self.LONG_POS:
                new_row = pd.DataFrame([[self.fix_shares], ], columns=['Shares'],
                                       index=[date, ])
                final_trade = final_trade.append(new_row)
            elif all_trade.loc[date] == self.SHORT_POS:
                new_row = pd.DataFrame([[-self.fix_shares], ], columns=['Shares'],
                                       index=[date, ])
                final_trade = final_trade.append(new_row)
            elif all_trade.loc[date] == self.CASH_POS:
                continue
            # print  final_trade.shape[0], final_trade.shape[1]
        return final_trade

    def cal_reward(self, prev_price, curr_price, impact, pos):
        reward = pos * ((curr_price/ prev_price) - 1)
        if np.bool(reward.values > 0):
            return reward * (1-impact)
        else:
            return reward * (1 + impact)


    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), sv = 10000):

        # add your code to do learning here

        # example usage of the old backward compatible util function
        syms=[symbol]
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        if self.verbose: print prices
        all_indicators = self.indicator.combine_all_indicators(prices)
        if self.verbose: print all_indicators
        cumulative_return = []
        thresholds = self.indicator.cal_thresholds(all_indicators, self.num_bins)
        for epoch in range(0, self.epochs):
            if self.verbose: print epoch
            pos = self.CASH_POS
            trade = pd.Series(index = all_indicators.index)
            for day, date in enumerate(all_indicators.index):
                if self.verbose: print date
                state = self.discretize(all_indicators.loc[date], thresholds, pos)
                if date == all_indicators.index[-1]:
                    new_pos = -pos
                elif date == all_indicators.index[0]:
                    action = self.qlearner.querysetstate(state)
                    new_pos = self.next_position(action - 1, pos)
                else:
                    reward = self.cal_reward(prices.iloc[day - 1], prices.loc[date], self.impact, pos)
                    action = self.qlearner.query(state, reward)
                    new_pos = self.next_position(action - 1, pos)
                trade.loc[date] = new_pos
                pos = pos + new_pos
                if self.verbose: print pos

            port_val = compute_portvals(self.transfer_df_trades(trade, symbol), start_val = sv, commission = 0, impact = self.impact)
            cr = port_val.iloc[-1, 0]/port_val.iloc[0, 0]  - 1
            if self.verbose: print cr
            cumulative_return.append(cr)
            if epoch > self.converge_end:
                if self.check_converge(cumulative_return):
                    final_val = port_val
                    non_cash_trade = trade[trade!= self.CASH_POS]
                    trade_num = non_cash_trade.shape[0]
                    return final_val, trade_num

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "IBM", sd=dt.datetime(2009,1,1), ed=dt.datetime(2010,1,1), sv = 10000):

        # here we build a fake set of trades
        # your code should return the same sort of data
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        prices = prices_all[symbol]  # only portfolio symbols
        all_indicators = self.indicator.combine_all_indicators(prices)
        trade = pd.Series(index = all_indicators.index)
        pos = self.CASH_POS
        thresholds = self.indicator.cal_thresholds(all_indicators, self.num_bins)
        for date in all_indicators.index:
            state = self.discretize(all_indicators.loc[date], thresholds,
                                    pos )
            action = self.qlearner.querysetstate(state)
            if date != all_indicators.index[-1]:
                new_pos = self.next_position(action - 1, pos)
            else:
                new_pos = -pos
            trade.loc[date] = new_pos
            pos += new_pos
        return self.get_df_trades(trade)

if __name__=="__main__":
    print "One does not simply think up a strategy"
