import pandas as pd
import os

# Get the absolute path to the resources directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # The directory of cron.py
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

class EqUtils:
    def __init__(self):
        self.data_path = os.path.join(RESOURCES_DIR, 'eq_data.csv')

    def get_data(self, lookback_days: int, min_magnitude: float = 4.0) -> (pd.DataFrame, pd.DataFrame):
        data = pd.read_csv(self.data_path)

        # Convert the time column to datetime
        data['time'] = pd.to_datetime(data['time'])

        # Get the earthquake data for the last lookback_days
        current_time = pd.Timestamp.now().normalize()
        lookback_cutoff = current_time - pd.DateOffset(days=lookback_days)
        trend_cutoff = current_time - pd.DateOffset(days=lookback_days * 2)

        # Filter current period data
        data = data[data['time'] >= lookback_cutoff].copy()

        data.drop(columns=[
            'depthError', 'dmin', 'gap', 'horizontalError', 'id', 'magError', 'magNst',
            'magSource', 'magType', 'net', 'nst', 'rms', 'status', 'type', 'updated', 'locationSource',
        ], inplace=True)

        # Filter the data based on the minimum magnitude
        data = data[data['mag'] >= min_magnitude]

        # Rename the columns and format date
        data.rename(columns={'time': 'date', 'mag': 'magnitude'}, inplace=True)
        data['date'] = data['date'].dt.strftime('%d-%m-%Y')

        # Filter trend period data
        trend_data = data.copy()  # Start with a fresh copy
        trend_data = pd.read_csv(self.data_path)
        trend_data['time'] = pd.to_datetime(trend_data['time'])

        # Create mask for trend period
        trend_mask = (trend_data['time'] >= trend_cutoff) & (trend_data['time'] < lookback_cutoff)
        trend_data = trend_data[trend_mask].copy()

        trend_data.drop(columns=[
            'depthError', 'dmin', 'gap', 'horizontalError', 'id', 'magError', 'magNst',
            'magSource', 'magType', 'net', 'nst', 'rms', 'status', 'type', 'updated', 'locationSource',
        ], inplace=True)

        trend_data = trend_data[trend_data['mag'] >= min_magnitude]

        trend_data.rename(columns={'time': 'date', 'mag': 'magnitude'}, inplace=True)
        trend_data['date'] = trend_data['date'].dt.strftime('%d-%m-%Y')

        return data, trend_data