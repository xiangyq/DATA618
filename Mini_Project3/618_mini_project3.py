"""
DATA 618: Mini_Project 3 (Signal Processing)

Author: Youqing Xiang

Note: This project is based upon the sample code provided to us on Blackboard.
"""

import numpy as np
import pytz


def initialize(context):
    context.jpm = sid(25006)
    context.axp = sid(679)
    
    context.delta = 0.00001
    context.Vw = context.delta / (1 - context.delta) * np.eye(2)
    context.Ve = 0.0001
    
    context.beta = np.zeros(2) 
    context.P = np.zeros((2, 2)) 
    context.R = None 
    
    context.pos = None 
    context.day = None 
    
  
def handle_data(context, data):
    exchange_time = get_datetime().astimezone(pytz.timezone('US/Eastern'))
    
    
    if exchange_time.hour == 15 and exchange_time.minute >= 55:
        if context.day is not None and context.day == exchange_time.day:  
            return
        context.day = exchange_time.day
        
        x = np.asarray([data.current(context.jpm, 'price'), 1.0]).reshape((1, 2))
        y = data.current(context.axp, 'price')
            
        if context.R is not None:
            context.R = context.P + context.Vw
        else:
            context.R = np.zeros((2, 2))
      
        yhat = x.dot(context.beta)
    
        Q = x.dot(context.R).dot(x.T) + context.Ve  

        sqrt_Q = np.sqrt(Q)  
        e = y - yhat 
        K = context.R.dot(x.T) / Q
        context.beta = context.beta + K.flatten() * e  
        context.P = context.R - K * x.dot(context.R) 
     
        record(beta=context.beta[0], alpha=context.beta[1]) 
        if e < 6:
            record(spread=float(e), Q_upper=float(sqrt_Q), Q_lower=float(-sqrt_Q))
    
        
        if context.pos is not None:
            if context.pos == 'long' and e > -sqrt_Q:
                order_target(context.jpm, 0)
                order_target(context.axp, 0)
                context.pos = None
            elif context.pos == 'short' and e < sqrt_Q:
                order_target(context.jpm, 0)
                order_target(context.axp, 0)
                context.pos = None
            
        if context.pos is None:
            if e < -sqrt_Q: 
                order_target_percent(context.jpm, 1)
                order_target_percent(context.axp, 0)
                context.pos = 'long'
            elif e > sqrt_Q:               
                order_target_percent(context.jpm, 0)
                order_target_percent(context.axp, 1)
                context.pos = 'short'
