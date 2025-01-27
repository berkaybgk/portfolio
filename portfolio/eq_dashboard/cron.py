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

    # Convert the time column to datetime, year-month-day
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d')

    # Save the data to a csv file
    df.to_csv(recent_data_path, index=False)

    return df

def update_latest_eq_data():
    try:
        # Get the yesterday's date
        yesterday = (datetime.datetime.today() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')

        # Get the date tomorrow
        tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # Get the data from the USGS API
        df = get_eq_data(yesterday, tomorrow)

        old_data = pd.read_csv(eq_data_path)

        # Iterate over the rows of the dataframe, remove the rows that are already in the csv file, by the id
        for index, row in df.iterrows():
            if row['id'] in old_data['id'].values:
                old_data.drop(old_data[old_data['id'] == row['id']].index, inplace=True)

        # Concatenate the old data with the new data
        new_data = pd.concat([old_data, df], ignore_index=True)

        # Convert the time column to datetime, year-month-day
        new_data['time'] = pd.to_datetime(new_data['time']).dt.strftime('%Y-%m-%d')

        # Sort the data by the time column
        new_data = new_data.sort_values(by='time', ascending=False)

        # Save the new data to the csv file
        new_data.to_csv(eq_data_path, index=False)


    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == '__main__':
    update_latest_eq_data()