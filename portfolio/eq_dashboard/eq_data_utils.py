import pandas as pd
import os

# Get the absolute path to the resources directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # The directory of cron.py
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

class EqUtils:
    def __init__(self):
        self.data_path = os.path.join(RESOURCES_DIR, 'eq_data.csv')

    def get_data(self, lookback_days: int, min_magnitude: float = 4.0) -> pd.DataFrame:
        data = pd.read_csv(self.data_path)

        # Convert the time column to datetime
        data['time'] = pd.to_datetime(data['time'])

        # Get the earthquake data for the last lookback_days, 'time' column is in the format 'year-month-day'
        data = data[data['time'] >= pd.Timestamp.now().normalize() - pd.DateOffset(days=lookback_days)]

        data.drop(columns=[
            'depthError', 'dmin', 'gap', 'horizontalError', 'id', 'magError', 'magNst',
            'magSource', 'magType', 'net', 'nst', 'rms', 'status', 'type', 'updated', 'locationSource',
        ], inplace=True)

        # Filter the data based on the minimum magnitude
        data = data[data['mag'] >= min_magnitude]

        # Rename the columns, time -> date, mag -> magnitude
        data.rename(columns={'time': 'date', 'mag': 'magnitude'}, inplace=True)

        # Modify the date column to be in the format 'day-month-year'
        data['date'] = data['date'].dt.strftime('%d-%m-%Y')

        return data
