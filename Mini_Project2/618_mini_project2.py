"""
DATA 618: Mini_Project 2 (Financial Machine Learning)

Author: Youqing Xiang
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn import linear_model
from collections import deque
import numpy as np

def initialize(context):
    context.security = sid(24)
    context.window_length = 12
   
    context.classifier_rf = RandomForestClassifier()
    context.classifier_svm = svm.SVC()
    context.classifier_lg = linear_model.LogisticRegression()
    
    context.recent_prices = deque(maxlen=context.window_length + 2)
    context.recent_value = deque(maxlen=context.window_length + 2) 
    context.X = deque(maxlen=500)
    context.Y = deque(maxlen=500)
    
    context.prediction_rf = 0
    context.prediction_svm = 0
    context.prediction_lg = 0
        
def handle_data(context, data):
    context.recent_prices.append(data.current(context.security, 'price')) 
    context.recent_value.append([data.current(context.security, 'price'),
                                 data.current(context.security, 'volume'), 
                                 data.history(context.security, 'price', 20, '1d').mean()])
    
    if len(context.recent_prices) == context.window_length + 2: 
        
        changes = np.diff(context.recent_prices) > 0
        values = np.array(context.recent_value).flatten()
        context.X.append(values[:-1]) 
        context.Y.append(changes[-1]) 
        
        log.info(values[:-1]) 
        log.info(changes[-1])  
        
        if len(context.Y) >= 500: 
            
            context.classifier_rf.fit(context.X, context.Y) 
            context.classifier_svm.fit(context.X, context.Y)
            context.classifier_lg.fit(context.X, context.Y)
            context.prediction_rf = context.classifier_rf.predict(values[1:]) 
            context.prediction_svm = context.classifier_svm.predict(values[1:])
            context.prediction_lg = context.classifier_lg.predict(values[1:])
            
            final_prediction = int(context.prediction_svm) + int(context.prediction_rf) + int(context.prediction_lg)
            
            if final_prediction >= 2:
                order_target_percent(context.security, 1)
                record(prediction=final_prediction)
            elif final_prediction <= 1:
                order_target_percent(context.security, 0)
                record(prediction=int(final_prediction))
            else:
                record('do nothing')
