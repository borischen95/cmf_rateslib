# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 01:59:44 2021

@author: borischen
"""

import matplotlib.pyplot as plt

class IR_Futures(object):
    def __init__(self, expiry, tenor, size):
        
        self._expiry = expiry
        self._size = size
        
        if type(tenor)==str:
            dic = {'N': 1/360, 'D': 1/360, 'W': 7/360, 'M': 1/12, 'Q': 1/4, 'Y': 1}
            if any(i.isdigit() for i in tenor):
                tenor = [int(word) for word in tenor.split(tenor[-1]) if word.isdigit()][0]*dic[tenor[-1]]
            else:
                tenor = dic[tenor[-1]]
        self._tenor = tenor
        
        
    def pv(self, curve, asof = 0):
        result = 100 - 100*curve.fwd_rate(self._expiry, self._tenor)
        return result
    
    def get_cashflows(self, curve, asof = 0):
        
        cashflow = []
        dv01 = self.dv01()
        i = asof
        k = 1/360
        while i<self._expiry:
            if i == asof:
                cashflow.append(-self.pv(curve, asof))
            else:
                cashflow.append(100*(curve.fwd_rate(i, self._tenor)-(curve.fwd_rate(i-k, self._tenor)))*dv01) 
            i = i+k
                                 
        return cashflow
    
    def cashflows_plot(self, curve, asof = 0):
        
        plt.figure(figsize = (15,7))
        flows = self.get_cashflows(curve, asof)       
        plt.plot(flows)
        plt.title('Cash Flows')
        plt.show()
    
    def dv01(self):
        
        dv = self._size*self._tenor*0.01**2
        
        return dv