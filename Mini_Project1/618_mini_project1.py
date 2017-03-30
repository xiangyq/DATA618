"""
DATA 618: Mini_Project 1 (Pairs Trading)

Author: Youqing Xiang
"""

from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q1500US


Volume = 1000

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # create the list of paired securities with information
    context.s1 = sid(700)
    context.s2 = sid(1335)
    context.pair= [context.s1, context.s2, False, 1, 1]
    # context.pair = [stock1,stock2,is_cointegrated,ave,stdev]
    
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    data1 = data.history(context.pair[0], 'close', 30, '1d')
    data2 = data.history(context.pair[1], 'close', 30, '1d')
    data1_s = not_stationary(data1)
    data2_s = not_stationary(data2)
        
    if(data1_s and data2_s):
            
        p_coint = coint(data1, data2)[1]
        if(p_coint < 0.05):
            diff = data1 - data2
            ave = diff.mean()
            sd = diff.std()
            context.pair[2] = True
            context.pair[3] = ave
            context.pair[4] = sd

def not_stationary(data, cutoff=0.05):

    pvalue = adfuller(data)[1]
    if pvalue < cutoff:
        return True
    else:
        return False
 
def handle_data(context,data):
    """
    Called every minute.
    """
    global volume
    if context.pair[2]:
        p1 = data.current(context.pair[0], 'price')
        p2 = data.current(context.pair[1], 'price')
        diff = p1 - p2
        if diff > (context.pair[3] + context.pair[4]):
            if data.can_trade(context.s1) and data.can_trade(context.s2):
                order(context.s1, Volume)
                order(context.s2, -Volume)
        elif diff < (context.pair[3] - context.pair[4]):
            if data.can_trade(context.s1) and data.can_trade(context.s2):
                order(context.s1, -Volume)
                order(context.s2, +Volume)
