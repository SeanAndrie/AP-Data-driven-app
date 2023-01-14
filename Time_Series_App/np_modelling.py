import numpy as np

from model import Model
from neuralprophet import NeuralProphet

class NeuralProphet_Model:
    def __init__(self):
        self.app_model = Model()

        self.required_cols = ['ds', 'y']

        self.fitted_model = None
        self.forecast  = None
        self.history = None
        
        # Fit parameters
        self.freq = 'D'
        self.checkpointing = True
        self.early_stopping = True

        # Model parameters
        self.learning_rate = 0.03
        self.epochs = 200
        self.batch_size = 128
        self.num_hidden_layers = 3
        self.optimizer = 'SGD'

        self.daily_seasonality = True
        self.yearly_seasonality = True

        self.collect_metrics = ['MAE', 'RMSE', 'MSE']

        self.params = {'daily_seasonality' : self.daily_seasonality,
                        'yearly_seasonality' : self.yearly_seasonality,
                        'collect_metrics' : self.collect_metrics,
                        'num_hidden_layers' : self.num_hidden_layers,
                        'learning_rate' : self.learning_rate,
                        'epochs' : self.epochs,
                        'batch_size' : self.batch_size,
                        'optimizer' : self.optimizer}
    
    # Fits model on set data
    def fit_model(self, data, add_regressors = None, regressors = None):
        # Initialize variables
        model = None
        df = None
        
        # Regressors are specified
        if add_regressors == True:
            print('With Regressors')
            model = NeuralProphet(n_lags = 2, **self.params) 
            model = model.add_lagged_regressor(regressors)

            col_concat = np.concatenate((self.required_cols, regressors), axis = 0)
            df = data[col_concat]
        
        # No regressors
        else:
            print('Without Regressors')
            model = NeuralProphet(n_forecasts = 365, **self.params) # Collect metrics
            df = data[self.required_cols]

        history = model.fit(df,
                             freq = self.freq,
                             checkpointing = self.checkpointing,
                             early_stopping = self.early_stopping)

        self.history = history
        self.fitted_model = model
        
        print(df)
        print(history.tail())
        print(self.fitted_model)

    def make_predictions(self, data, add_regressors, value, periods = None, regressors = None):
        forecast = None
        df = None

        print(f'Value - make_predictions(): ')
        if value == 0:
            if add_regressors == True:
                cols_concat = np.concatenate((self.required_cols, regressors), axis = 0)
                df = data[cols_concat]
            else:
                df = data[self.required_cols]
        else:
            df = self.fitted_model.make_future_dataframe(data[self.required_cols], periods = periods, n_historic_predictions=True)
        
        forecast = self.fitted_model.predict(df)

        self.forecast = forecast
        print(self.forecast)