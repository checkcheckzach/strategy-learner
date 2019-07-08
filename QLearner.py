

import numpy as np
import random as rand

class QLearner(object):

    def __init__(self, \
        num_states=3500, \
        num_actions = 3, \
        alpha = 0.5, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.s = 0
        self.a = 0
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna

        qshape=(num_states, num_actions)
        self.Q = np.zeros(shape=qshape)

    def querysetstate(self, s):
  
        self.s = s
        rnum = rand.uniform(0.0, 1.0)
        if rnum >= self.rar:
           action = self.Q[s, :].argmax()
        elif rnum < self.rar:
           action = rand.randint(0, self.num_actions-1)
        self.a = action
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self,s_prime,r):
       
        oldValue = self.Q[self.s, self.a]
        newValue = (r + self.gamma* self.Q[s_prime, self.Q[s_prime, :].argmax()])
        self.Q[self.s, self.a] = (1 - self.alpha) * oldValue  + self.alpha * newValue


        action = self.querysetstate(s_prime)
        self.rar = self.rar * self.radr
        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        return action


if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
