import pandas as pd
import datetime
import numpy as np
import requests
import concurrent.futures

from geopy import Nominatim
from meteostat import Daily, Stations
from statsmodels.tsa.seasonal import seasonal_decompose 

class Model:
    def __init__(self):

        # API
        self.BASE_URL = 'http://api.weatherapi.com/v1/'
        self.API_KEY = 'f106d21a9b3b4934baf130600231101'
        self.TYPE = 'forecast.json?'
        self.response = None
        self.dates = None
        self.temps = None

        # Weather Station
        self.weather_station = None

        # Date Range
        self.start = None
        self.end = None

        # Dataframe
        self.weather_df = None # Weather Dataframe
        self.df_overview = None # Described Weather Dataframe
        self.feature_df = None # Feature Dataframe
        self.feature_described = None # Feature-specific Described Dataframe

        # Figures
        # Seasonal Components
        self.sd_figure = None
        self.forecast_figure = None

        # Target Feature
        self.target = None

        # Train and Test Datasets
        self.train_df = None 
        self.test_df = None

        # Additional Regressors/Predictors
        self.regressors = None
        self.selected_regressors = None

    # Fetch API Response
    def get_api_response(self, location:str, n_forecasts=14):
        self.url = f'{self.BASE_URL}{self.TYPE}key={self.API_KEY}&q={location}&days={n_forecasts}&aqi=no&alerts=no'
        response = requests.get(self.url).json()
        self.extract_forecast_data(response)

    # Extract dates from forecastday
    def extract_dates(self, forecastday):
        dates = []
        for day in forecastday:
            for key, val in day.items():
                if key == 'date':
                    dates.append(val)
        return dates
    
    # Extract temperature
    def extract_temperature(self, forecastday):
        avgtemp_c, maxtemp_c, mintemp_c = [], [], []
        for day in forecastday:
            for key, val in day.items():
                if key == 'day':
                    for key, val in day[key].items():
                        if key == 'avgtemp_c':
                            avgtemp_c.append(val)
                        if key == 'maxtemp_c':
                            maxtemp_c.append(val)
                        if key == 'mintemp_c':
                            mintemp_c.append(val)
        return avgtemp_c, maxtemp_c, mintemp_c

    # Extract forecast data
    def extract_forecast_data(self, response):
        forecast = response['forecast']
        indices = np.arange(len(forecast['forecastday']))
        forecastday = np.array(forecast['forecastday'])[indices]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            dates = executor.submit(self.extract_dates, forecastday)
            temps = executor.submit(self.extract_temperature, forecastday)
        
        dates = dates.result()
        temps = temps.result()

        self.avgtemp = {dates[i]:temps[0][i] for i in range(len(dates))}
        self.maxtemp = {dates[i]:temps[1][i] for i in range(len(dates))}
        self.mintemp = {dates[i]:temps[2][i] for i in range(len(dates))}

    # Get the nearest weather station given location
    def nearest_weather_station(self, location:str):
        # Create new instance of Nominatim Geocode API
        locator = Nominatim(user_agent = 'GetLoc')
        get_location = locator.geocode(location)
        
        # Get Meteostat Weather Station list
        stations = Stations()

        # Get nearest weather station by latitude and longitude of specified location
        stations = stations.nearby(lat = get_location.latitude, lon = get_location.longitude)
        station_info = pd.DataFrame(stations.fetch(1))

        self.weather_station = station_info
    
    # Isolate date string components to create datetime objects
    def isolate_and_convert(self, start_entry:str, end_entry:str):
        
        # Isolate date components from date string entries
        start_sep = list(map(lambda x: int(x), start_entry.replace(' ', '').split('-')))
        end_sep = list(map(lambda x: int(x), end_entry.replace(' ', '').split('-')))

        # Check if date entries are fully formatted (Y-MM-DD) or contain only the year component
        if (len(start_sep) == 1 or len(end_sep) == 1):
            if (len(str(start_sep[0])) == 4 or len(str(end_sep[0])) == 4):
                start_date = datetime.datetime(start_sep[0], 1, 1, 0, 0)
                end_date = datetime.datetime(end_sep[0], 12, 31, 0, 0) 

        # Set fully formatted date string to datetime object
        else: 
            start_date = datetime.datetime(*start_sep, 0, 0)
            end_date = datetime.datetime(*end_sep, 0, 0)
        
        self.start, self.end = start_date, end_date
    
    # Checks for missing values in dataframe
    def contains_missing(self, df:pd.DataFrame):
        return df.isnull().all().any()

    def clean_data(self, df:pd.DataFrame):
        # Null value threshold
        null_thresh = int(0.7 * len(df))
        while self.contains_missing(df) == True:
            col_missing = df.isnull().sum()
            
            if True in np.array(col_missing.values >= null_thresh):
                # Drop columns with >= 70% missing values
                above_thresh = col_missing.loc[(col_missing >= null_thresh)]
                df = df.drop(above_thresh.keys(), axis = 1)

                self.clean_data(df)
            
            # Fill missing values by interpolation
            df = df.interpolate(option = 'time')
            break
        return df
    
    # Get weather dataframe given station, start date, and end date
    def get_weather_df(self):
        # Convert date objects to datetime objects        
        data = Daily(self.weather_station, self.start, self.end)
        weather_df = data.fetch()

        # Set dataframe frequency to inferred frequency
        weather_df = weather_df.asfreq(weather_df.index.inferred_freq)   

        # Fill missing values
        weather_df = self.clean_data(weather_df)
        self.weather_df = weather_df
    
    def create_dataframe_overview(self):
        # Total Observations 
        ttl_observations = len(self.weather_df.index)
        # Total Features
        ttl_features = len(self.weather_df.columns)
        # Number of Missing Data
        missing_data = self.weather_df.isna().sum().sum()
        # Missing Data in Percentage
        missing_data_perc = np.round((missing_data/(ttl_observations*ttl_features)), 1)
        # Number of Duplicated Rows
        duplicated_rows = self.weather_df.duplicated().sum()
        # Number of Duplicated Rows in Percentage
        duplicated_rows_perc = np.round((duplicated_rows/(ttl_observations*ttl_features)), 1)

        overview = {'Total Number of Observations' : ttl_observations,
                    'Total Number of Features' : ttl_features,
                    'Missing Data' : missing_data,
                    'Missing Data (%)' : missing_data_perc,
                    'Duplicated Rows' : duplicated_rows,
                    'Duplicated Rows (%)' : duplicated_rows_perc}
        self.df_overview = overview
    
    def create_feature_overview(self, feature:str):
        # Get described dataframe 
        df_described = self.weather_df.describe()

        # Get feature dataframe and its descriptive statistics
        self.feature_df = self.weather_df[feature]
        self.feature_described = df_described[feature].apply(lambda x: np.round(x, 1))

    def create_seasonal_decomposition(self):
        # Get component figures
        feature_decomposed = seasonal_decompose(self.feature_df, model = 'additive')
        self.sd_figure = feature_decomposed.plot(observed = False)
        self.sd_figure.set_size_inches((6.3, 3.1))

    def create_train_test_data(self, target:str):
        df = self.weather_df

        # 80% for training, 10% for testing
        split_val = int(0.8 * len(df))

        # Create 'y' and 'ds' columns (target and date)
        df['y'] = df.shift(-1)[target] 
        df['ds'] = df.index.date
        
        # Forward fill missing value in 'y' column
        df['y'].fillna(method = 'ffill', inplace = True)

        # Split into train and test sets
        train_df = df.iloc[:split_val]
        train_df.index = np.arange(len(train_df))

        test_df = df.iloc[split_val:]
        test_df.index = np.arange(len(test_df))

        self.train_df = train_df
        self.test_df = test_df
        self.regressors = self.train_df.columns[~self.train_df.columns.isin(['y', 'ds'])]
