"""
DATA 618: Mini_Project 2 (Financial Machine Learning)

Author: Youqing Xiang
"""

def initialize(context):
    context.security = sid(24) 
    context.window_length = 20 
   
    context.classifier = RandomForestClassifier() 
    

    context.recent_prices = deque(maxlen=context.window_length + 2)
    context.recent_value = deque(maxlen=context.window_length + 2) 
    context.X = deque(maxlen=300) 
    context.Y = deque(maxlen=300) 
    
    context.prediction = 0                  
    
def handle_data(context, data):
    context.recent_prices.append(data.current(context.security, 'price'))
    context.recent_value.append([data.current(context.security, 'price'),
                                 data.current(context.security, 'volume'), 
                                 data.history(context.security, 'price', 30, '1d').mean(),
                                 data.history(context.security, 'price', 15, '1d').mean()])
    
    if len(context.recent_prices) == context.window_length + 2: 
        
        
        changes = np.diff(context.recent_prices) > 0
        values = np.array(context.recent_value).flatten()
        context.X.append(values[:-1]) 
        context.Y.append(changes[-1]) 
        
        log.info(values[:-1]) 
        log.info(changes[-1]) 
        
        if len(context.Y) >= 300: 
            
            context.classifier.fit(context.X, context.Y) 
            
            context.prediction = context.classifier.predict(values[1:]) 
            
            order_target_percent(context.security, context.prediction)
                
            record(prediction=int(context.prediction))
