# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 01:59:44 2021

@author: borischen
"""
import numpy as np
import matplotlib.pyplot as plt

class IR_Futures(object):
    def __init__(self, expiry, tenor, size, kind = 'ED'):
        
        self._expiry = expiry
        self._size = size
        
        if type(tenor)==str:
            dic = {'N': 1/360, 'D': 1/360, 'W': 7/360, 'M': 1/12, 'Q': 1/4, 'Y': 1}
            if any(i.isdigit() for i in tenor):
                tenor = [int(word) for word in tenor.split(tenor[-1]) if word.isdigit()][0]*dic[tenor[-1]]
            else:
                tenor = dic[tenor[-1]]
                
        self._type = kind
        self._tenor = tenor
        
        
    def pv(self, curve = None, rate = None, asof = 0):
        if (curve==None) and (rate==None):
            print("Need argument rate or curve")
            return None
        
        if curve == None:
            rate = np.round(rate,4)
            result = 100 - 100*rate
            duration = ((100 - 100*rate-0.01)-(100 - 100*rate+0.01))/(2*0.01)
        elif rate == None:
            rate = np.round((1/curve.df(self._expiry)-1)/self._expiry, 4)
            
            result = 100 - 100*rate
            duration = ((100 - 100*rate-0.01)-(100 - 100*rate+0.01))/(2*0.01)
        self._pv = result
        self._duration = duration
        return result
    
    def get_cashflows(self, curve, asof = 0, trade_date = None):
        
        
        if trade_date == None:
            trade_date = self._expiry
            
        cashflow = []
        dv01 = self.dv01()
        trade_rate = np.round((1/curve.df(trade_date)-1)/self._expiry, 4)
        i = asof
        k = 1/360
        while i<trade_date:
            if i == asof:
                cashflow.append(-self._pv)
            else:
                cashflow.append(0) 
            i = i+k
        cashflow.append((self._pv-(100 - 100*trade_rate))*dv01)             
            
        return cashflow
    
    def cashflows_plot(self, curve, asof = 0, trade_date = None):
        
        plt.figure(figsize = (15,7))
        flows = self.get_cashflows(curve, asof, trade_date)       
        plt.plot(flows)
        plt.title('Cash Flows')
        plt.show()
    
    def dv01(self):
        
        dv = self._size*self._tenor*0.01**2
        
        return dv
    
    def duration(self):
        
        return self._duration
    
    def convexity(self, valuation_date, volatility, mean_reversion):
       
        """ Calculation of the convexity adjustment between FRAs and interest
        rate futures using the Hull-White model as described in technical note
        in link below:
        http://www-2.rotman.utoronto.ca/~hull/TechnicalNotes/TechnicalNote1.pdf
        NOTE THIS DOES NOT APPEAR TO AGREE WITH BLOOMBERG!! INVESTIGATE.
        """

        a = mean_reversion
        t0 = 0.0
        t1 = (self._expiry-2/252 - valuation_date) / 360
        t2 = (self._expiry - valuation_date) / 360
        # Hull White model for short rate dr = (theta(t)-ar) dt + sigma * dz
        # This reduces to Ho-Lee when a = 0 so to avoid divergences I provide
        # this numnerical limit
        if abs(a) > 1e-10:

            bt1t2 = (1.0 - np.exp(-a * (t2 - t1))) / a
            bt0t1 = (1.0 - np.exp(-a * (t1 - t0))) / a
            w = 1.0 - np.exp(-2.0 * a * t1)
            term = bt1t2 * w + 2.0 * a * (bt0t1**2)
            c = bt1t2 * (volatility**2) * term / (t2 - t1) / 4.0 / a

        else:
            c = t1 * t2 * (volatility**2) / 2.0

        return c