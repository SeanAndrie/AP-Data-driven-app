
# Dependencies
from model import Model
from np_modelling import NeuralProphet_Model
from view import View
from tkinter import messagebox
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error

import tkinter as tk
import numpy as np
import datetime
import pandas as pd
import pandastable as pt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Controller:
    def __init__(self):
        self.model = Model()
        self.neural_prophet = NeuralProphet_Model()
        self.view = View(self)

        self.temp_sd = None
        self.temp_forecast = None

        self.target_set = False
        self.add_regressors = False
        self.selected_regressors = []

    def main(self):
        self.view.main()

    def set_date_loc(self):

        extract_btn_state = 'disabled'
        
        if self.view.cal_state == 0:
            # Error Handling
            if self.view.location.get() == '':
                messagebox.showerror('Missing Location Entry',
                                    'Location entry is missing.\n\nEnter the location you wish to view weather data of.')
                extract_btn_state = 'normal'

            if (self.view.start_date_entry.get() == '' or self.view.end_date_entry.get() == ''):
                messagebox.showerror('Missing Date Entry',
                                    'Date entry is missing.\n\nPlease specify the date range of weather data you wish to view.')
                extract_btn_state = 'disabled'

            if (self.view.start_date_entry.get().isnumeric() == False) and (self.view.end_date_entry.get().isnumeric() == False):
                messagebox.showerror('Invalid Date Entry',
                                    'Date entry is invalid.\n\nPlease specify the date range of weather data you wish to view.')
                extract_btn_state = 'normal'

            if (int(self.view.start_date_entry.get()) >= int(datetime.datetime.now().strftime('%Y')) or int(self.view.end_date_entry.get()) >= int(datetime.datetime.now().strftime('%Y'))):
                messagebox.showerror('Invalid Date Entry',
                                    'Insufficient data for that date entry. Available Data: 2012 - 2022')
                extract_btn_state = 'normal'
            
        self.view.set_btn.configure(state = extract_btn_state)

        if self.view.cal_state == 1:
            self.view.start_date_frame.destroy()
            self.view.end_date_frame.destroy()    
        
        # Get date entries
        start_entry = self.view.start_date_entry.get() if self.view.cal_state == 0 else self.view.start_date.get_date()
        end_entry = self.view.end_date_entry.get() if self.view.cal_state == 0 else self.view.end_date.get_date()
        
        # Separate date string entries to date components and convert to datetime object
        self.model.isolate_and_convert(start_entry, end_entry)

        # Create date object for label (Excluding hours and mins from datetime objects)
        start_date_attr = {'year' : self.model.start.year, 
                        'month' : self.model.start.month, 
                        'day' : self.model.start.day}

        end_date_attr = {'year' : self.model.end.year, 
                        'month' : self.model.end.month, 
                        'day' : self.model.end.day}

        start_date = datetime.date(**start_date_attr)
        end_date = datetime.date(**end_date_attr)
        
        if self.model.start <= self.model.end:
            # Remove all existing entries
            self.view.start_date_entry.delete(0, len(self.view.start_date_entry.get()))
            self.view.end_date_entry.delete(0, len(self.view.end_date_entry.get()))

            # Insert date object as string to entry
            self.view.start_date_entry.insert(0, str(start_date))
            self.view.end_date_entry.insert(0, str(end_date))

            # Get nearest weather station by geophysical distance
            self.model.nearest_weather_station(self.view.location.get())
            
            self.view.weather_station_lbl.configure(text = f'Weather Station : {self.model.weather_station.name[0]}')
            self.view.extract_btn.configure(state = 'normal')

        else:
            messagebox.showerror('Error: Invalid Date Range',
                                 f'Start Date ({start_date}) preceeds End Date ({end_date}).\n\nEnsure that the Start Date always preceeds the End Date.')
    
    # Displays weather dataframe
    def show_weather_df(self):
        self.model.get_weather_df()
        self.model.create_dataframe_overview()

        self.view.extract_frame.destroy()
        self.table_df = pt.Table(self.view.df_frame,
                                 dataframe = self.model.weather_df,
                                 width = 480,
                                 height = 500,
                                 showstatusbar =True)
        self.table_df.show()
        
        self.view.plot_feature_widgets()
        self.view.df_stats_widgets(self.model.df_overview)
        self.view.overview_option_menu()

    # Pass feature option menu choice to create feature overview
    def feature_option_callback(self, choice):
        self.model.create_feature_overview(choice)
        self.view.feature_stats_labels(self.model.feature_described)
        self.model.create_seasonal_decomposition()

    # Choice handler for Statistics Option Menu widget
    def overview_callback(self, choice):
        if choice == 'Dataset Statistics':
            self.view.feature_stats_frame.destroy()
            self.view.df_stats_widgets(self.model.df_overview)
        
        else:
            self.view.dataset_stats_frame.destroy()
            self.view.feature_stats_widgets(self.model.weather_df)
            self.feature_option_callback(choice = self.view.feature_option_menu.get())

    # Display seasonal decomposition figure
    def display_seasonal_decomposition(self):
        
        # Close pre-existing canvas widget
        if self.temp_sd != None:
            plt.close()
            self.temp_sd.destroy() 

        # Create and pack canvas
        canvas = FigureCanvasTkAgg(self.model.sd_figure, self.view.canvas_frame)
        widget = canvas.get_tk_widget()
        widget.pack(fill = 'both', expand = True)

        self.temp_sd = widget

    # Open NeuralProphet Modelling Frame
    def neuralprophet_modelling_frame(self):
        self.view._modelling_frame(self.model.weather_df)
        self.view.temporary_regressor_widgets()
        self.view._temp_forecast_results()
        self.view._temp_train_results()
        self.view._results_tabs()

    # Set target feature and create train/test split on dataset
    def set_target_feature(self):
        if self.target_set == False:

            self.target_set = True
            print(f'Target Set: {self.target_set}')

            self.view.forecast_test_btn.configure(state = 'normal')
            self.view.forecast_future_btn.configure(state = 'normal')
            
            self.view.confirm_target_btn.configure(fg_color = '#31A24C', hover_color = '#31784C')
            self.view.confirm_target_btn.configure(text = 'Target: Set')
            self.view.add_reg_checkbox.configure(state = tk.NORMAL)

            self.view.forecast_test_btn.configure(state = tk.NORMAL)
            self.view.forecast_future_btn.configure(state = tk.NORMAL)

            target = self.view.target_option_menu.get()
            self.model.target = target

            self.add_log(f'Target => {self.model.target}')

            self.model.create_train_test_data(target)
            self.add_log(f'\nTrain Data:\n\n{self.model.train_df}\nTest Data:\n\n{self.model.test_df}')

        else:
            print(f'Target Set: {self.target_set}')
            self.view.forecast_btn.configure(state = 'disabled')

            self.view.confirm_target_btn.configure(fg_color = '#E41E3F', hover_color = '#8C1E3F')
            self.view.confirm_target_btn.configure(text = 'Target: Not Set')
            self.view.add_reg_checkbox.configure(state = tk.DISABLED)

            self.view.forecast_test_btn.configure(state = tk.DISABLED)
            self.view.forecast_future_btn.configure(state = tk.DISABLED)

            self.target_set = False
            print(f'Target: None')
            self.model.target = None

    # Fetch regressors from generated train dataset
    def get_regressors(self):
        # Enable additional regressors
        if self.view.add_reg_checkbox_var.get() == 'on':
            self.add_regressors = True

            self.add_log(f'Additional Regressors => ENABLED')
            self.view.forecast_future_btn.configure(state = 'disabled')

            self.view.temp_regressors_frame.destroy()
            regressors = self.model.regressors

            self.view._regressors_check_boxes(regressors)
            self.temp_checkbox = self.view.checbox_list

        # Disable additonal regressors
        else:
            self.view.forecast_future_btn.configure(state = 'normal')

            self.add_log(f'Additional Regressors => DISABLED')

            self.add_regressors = False
            self.view.checkbox_list.clear()

            self.view.checkbox_frame.destroy()
            self.view.temporary_regressor_widgets()
    
    # Add regressors to pass into Neural Prophet Model
    def add_regressor(self):
        regressor_widgets = self.view.checkbox_list
        
        selected_indices = np.array([idx for idx, widget in enumerate(regressor_widgets) if widget.get() == 'on'])
        selected_cols = self.model.regressors[selected_indices].to_list()

        self.add_log(f'Selected Regressors => {selected_cols}')
        self.model.selected_regressors = selected_cols
    
    def forecast_future(self):
        self.btn_val = 1
        self.add_log(f'Fitting Model on Future Data . . . ')
        self.fit_model(self.btn_val)

    def forecast_test(self):
        self.btn_val = 0
        self.add_log(f'Fitting Model on Test Data . . .')
        self.fit_model(self.btn_val)

    # Decides whether to fit model on:
    # 1. Train data with regressors, or
    # 2. Combination of train and test data without regressors
    def fit_model(self, value):
        self.view.add_reg_checkbox.configure(state = tk.DISABLED)

        for widget in self.view.checkbox_list:
            widget.configure(state = tk.DISABLED)
        
        print(f'Value fit_model(): {value}')
        # If forecasting on test data
        if value == 0:
            # Check if regressors were selected
            if self.add_regressors == True:
                self.neural_prophet.fit_model(self.model.train_df, regressors = self.model.selected_regressors, add_regressors = self.add_regressors)
            else:
                self.neural_prophet.fit_model(self.model.train_df, add_regressors = self.add_regressors)

        # If forecasting on future data
        else:
            self.view.forecast_test_btn.configure(state = tk.DISABLED)

            # self.view.year_entry.configure(state = tk.NORMAL)
            combined_df = pd.concat([self.model.train_df, self.model.test_df], axis = 0)
            combined_df.reset_index()
            self.neural_prophet.fit_model(combined_df, add_regressors = self.add_regressors)
        
        self.add_log(f'Training COMPLETE\n\n{self.neural_prophet.history}')
        self.view.forecast_btn.configure(state = tk.NORMAL)
            
    def predict(self, value):
        print(f'Value predict(): {value}')
        self.add_log('Generating Forecast . . .')
        if value == 0:
            self.neural_prophet.make_predictions(data = self.model.test_df, 
                                                regressors = self.model.selected_regressors, 
                                                add_regressors = self.add_regressors, value = value)
        else:
            combined_df = pd.concat([self.model.train_df, self.model.test_df], axis = 0)
            combined_df.reset_index()
            self.neural_prophet.make_predictions(data = combined_df, 
                                                 add_regressors = self.add_regressors,
                                                 periods = 365, value = value)
        
        self.model.forecast_figure = self.neural_prophet.fitted_model.plot(self.neural_prophet.forecast)
        self.model.forecast_figure.set_size_inches((7, 2.5))
       
        self.view.plots_btn.configure(state = tk.DISABLED)
        self.view.log_btn.configure(state = tk.NORMAL)
        self.view.forecast_btn.destroy()

        self.view._result_plots_tab()
        self.display_forecast_figure()

        self.add_log('Forecast GENERATED\n\n{}'.format(self.neural_prophet.forecast[['ds', 'y', 'yhat1']]))
        self.model.get_api_response(self.view.location.get())

        offset = 2 if self.btn_val == 0 else 0

        forecast_start_date = str(self.neural_prophet.forecast['ds'].iloc[offset].date())
        forecast_end_date = str(self.neural_prophet.forecast['ds'].iloc[-1].date())
        self.view._forecast_results_widgets(forecast_start_date, forecast_end_date)

    def add_log(self, text_to_insert):
        curr_time = datetime.datetime.now().strftime('%H:%M:%S')

        self.view.train_log.configure(state = 'normal')
        self.view.train_log.insert('end', f'{curr_time} : {text_to_insert}\n\n')
        self.view.train_log.configure(state = 'disabled')

        self.view.train_log.yview('end')

    def display_forecast_figure(self):

        if self.temp_forecast != None:
            plt.close()
            self.temp_forecast.destroy()

        canvas = FigureCanvasTkAgg(self.model.forecast_figure, self.view.forecast_canvas_frame)
        widget = canvas.get_tk_widget()
        widget.pack(fill = 'both', expand = True)

        self.temp_forecast = widget

    def switch_tab(self, val):
        if val == 'logs':
            plt.close()
            self.temp_forecast.destroy()

            self.view.result_plots_base.destroy()

            self.view.log_btn.configure(state = 'disabled')
            self.view.plots_btn.configure(state = 'normal')
        else:
            self.view._result_plots_tab()
            self.display_forecast_figure()
            # plt.show()
            self.view.log_btn.configure(state = 'normal')
            self.view.plots_btn.configure(state = 'disabled')
    
    def evaluation_metrics(self, y_true, y_pred):
        mae = np.round(mean_absolute_error(y_true, y_pred), 2)
        mse = np.round(mean_squared_error(y_true, y_pred), 2)
        rmse = np.round(np.sqrt(mean_squared_error(y_true, y_pred)), 2)

        return {'MAE' : mae,
                'MSE' : mse,
                'RMSE' : rmse}
    
    def display_pred_actual(self):
        valid_val = None
        metrics_dict = None

        self.view.forecast_info.destroy()

        forecast_df = self.neural_prophet.forecast
        forecast_df.index = forecast_df['ds'].apply(lambda date: pd.to_datetime(date))

        target = self.model.target
        date = self.view.get_pred_entry.get().replace(' ', '').split('-')
        format_date = '-'.join(date)

        # Specified date + 13 days
        int_date = [int(comp) for comp in date]
        two_weeks = (datetime.date(*int_date) + datetime.timedelta(days = 13)).strftime("%Y-%m-%d")
        
        # Get prediction and validation values
        pred = np.round(forecast_df['yhat1'].loc[format_date], 1)
        valid_val = 'Actual: {}'.format(np.round(forecast_df['y'].loc[format_date], 1))

        # If model was trained on the entire dataset
        if self.btn_val == 1:
            if format_date in self.model.avgtemp.keys():
                if target == 'tavg':
                    valid_val = f'Weather API: {self.model.avgtemp[format_date]}'
                    metrics_dict = self.evaluation_metrics(list(self.model.avgtemp.values()), forecast_df['yhat1'].loc[format_date:two_weeks])
                    print(metrics_dict)

                if target == 'tmin':
                    valid_val = f'Weather API: {self.model.mintemp[date]}'
                    metrics_dict = self.evaluation_metrics(list(self.model.mintemp.values()), forecast_df['yhat1'].loc[format_date:two_weeks])
                    print(metrics_dict)

                if target == 'tmax':
                    valid_val = f'Weather API: {self.model.maxtemp[date]}'
                    metrics_dict = self.evaluation_metrics(list(self.model.maxtemp.values()), forecast_df['yhat1'].loc[format_date:two_weeks])
                    print(metrics_dict)

            else:
                yhat = forecast_df['yhat1'].iloc[:-365]
                metrics_dict = self.evaluation_metrics(forecast_df['y'].iloc[:-365], yhat) 
                print(metrics_dict)

        else:
            yhat = forecast_df['yhat1'].fillna(method = 'backfill')
            metrics_dict = self.evaluation_metrics(forecast_df['y'], yhat)
            print(metrics_dict)
        
        self.view._forecast_results_labels(f'{pred}°C', f'ŷ | {format_date}', validation = valid_val, metrics = metrics_dict)

    def restart_program(self):
        prompt = messagebox.askokcancel('Create New Dataframe',
                               'The current dataframe will be deleted.\n\nDo you wish to continue?')

        # Destroy root and reinitialize app
        if prompt: 
            self.view.destroy()
            app = Controller()
            app.main()

if __name__ == '__main__':
    app = Controller()
    app.main()