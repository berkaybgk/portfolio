import requests
import datetime
import pandas as pd
import os

# Get the absolute path to the resources directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # The directory of cron.py
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

recent_data_path = os.path.join(RESOURCES_DIR, 'recent_data.csv')
eq_data_path = os.path.join(RESOURCES_DIR, 'eq_data.csv')

def get_eq_data(start_date, end_date) -> pd.DataFrame:
    # Get the data from the USGS API
    response = requests.get(f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv'
                            f'&starttime={start_date}'
                            f'&endtime={end_date}&'
                            f'minmagnitude=4.0'
                            f'&minlatitude=35.50'
                            f'&maxlatitude=42.50'
                            f'&minlongitude=25.00'
                            f'&maxlongitude=45.50'
                            f'&orderby=time'
                            )

    # Save the data to a file
    with open(recent_data_path, "w") as file:
        file.write(response.text)

    # Read the data from the file
    df = pd.read_csv(recent_data_path)

    return df

def update_latest_eq_data():
    print("Updating the latest earthquake data...")
    try:
        # Get the yesterday's date
        yesterday = (datetime.datetime.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        # Get the date tomorrow
        tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # Get the data from the USGS API
        df = get_eq_data(yesterday, tomorrow)

        # Iterate over the rows of the dataframe, remove the rows that are already in the csv file, by the id
        for index, row in df.iterrows():
            if row['id'] in pd.read_csv(eq_data_path)['id'].values:
                df.drop(index, inplace=True)

        # Append the new data to the csv file
        df.to_csv(eq_data_path, mode='a', header=False, index=False)

    except Exception as e:
        print(f"An error occurred: {e}")


