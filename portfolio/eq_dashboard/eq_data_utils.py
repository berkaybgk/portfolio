from django.utils import timezone
from datetime import timedelta
from .models import EarthquakeDataUSGS, EarthquakeDataAFAD
from typing import Tuple
import pandas as pd
from django.db.models import QuerySet


class EqUtils:
    @staticmethod
    def queryset_to_dataframe(queryset: QuerySet) -> pd.DataFrame:
        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(queryset))
        if not df.empty:
            # Rename mag to magnitude
            df.rename(columns={'mag': 'magnitude', 'time': 'date'}, inplace=True)
            # Format date
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%d-%m-%Y')
        return df

    def get_data(self, lookback_days: int, min_magnitude: float = 4.0) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # Calculate the cutoff dates
        current_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        lookback_cutoff = current_time - timedelta(days=lookback_days)
        trend_cutoff = current_time - timedelta(days=lookback_days * 2)

        # Get current period data
        current_data = (
            EarthquakeDataUSGS.objects
            .filter(
                time__gte=lookback_cutoff,
                mag__gte=min_magnitude
            )
            .values('time', 'latitude', 'longitude', 'depth', 'mag', 'place')
        )

        # Get trend period data
        trend_data = (
            EarthquakeDataUSGS.objects
            .filter(
                time__gte=trend_cutoff,
                time__lte=lookback_cutoff,
                mag__gte=min_magnitude
            )
            .values('time', 'latitude', 'longitude', 'depth', 'mag', 'place')
        )

        return self.queryset_to_dataframe(current_data), self.queryset_to_dataframe(trend_data)

    def get_interval_data(self, interval_start:str, interval_end:str, min_magnitude: float = 4.0) -> (pd.DataFrame, pd.DataFrame):
        # Get data for the specified interval
        data = (
            EarthquakeDataUSGS.objects
            .filter(
                time__gte=interval_start,
                time__lte=interval_end,
                mag__gte=min_magnitude
            )
            .values('time', 'latitude', 'longitude', 'depth', 'mag', 'place')
        )

        # Calculate the previous period
        interval_start = pd.to_datetime(interval_start)
        interval_end = pd.to_datetime(interval_end)
        previous_period_start = interval_start - (interval_end - interval_start)
        previous_period_start = previous_period_start.strftime('%Y-%m-%d %H:%M:%S')

        # Get data for the previous period
        previous_data = (
            EarthquakeDataUSGS.objects
            .filter(
                time__gte=previous_period_start,
                time__lt=interval_start,
                mag__gte=min_magnitude
            )
            .values('time', 'latitude', 'longitude', 'depth', 'mag', 'place')
        )

        return self.queryset_to_dataframe(data), self.queryset_to_dataframe(previous_data)

    def read_csv_into_db_usgs(self, data_path: str):
        try:
            # Read the data
            data = pd.read_csv(data_path)

            # Convert the time column to datetime
            data['time'] = pd.to_datetime(data['time'])

            # Save the data to the database
            for _, row in data.iterrows():

                if EarthquakeDataUSGS.objects.filter(csv_id=row['id']).exists():
                    continue

                # Create a new record
                EarthquakeDataUSGS.objects.create(
                    time=row['time'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    depth=row['depth'],
                    mag=row['mag'],
                    place=row['place'],
                    csv_id=row['id']
                )

        except Exception as e:
            print(f"Error in read_csv_into_db_usgs: {str(e)}")

    def read_csv_into_db_afad(self, data_path: str):
        try:
            # Read the data
            data = pd.read_csv(data_path)

            # Convert the time column to datetime
            data['eventDate'] = pd.to_datetime(data['eventDate'])

            # Rename date, id columns
            data.rename(columns={'eventId': 'csv_id', 'eventDate': 'time'}, inplace=True)

            # Save the data to the database
            for _, row in data.iterrows():

                if EarthquakeDataAFAD.objects.filter(csv_id=row['csv_id']).exists():
                    continue

                # Create a new record
                EarthquakeDataAFAD.objects.create(
                    time=row['time'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    depth=row['depth'],
                    mag=row['magnitude'],
                    place=row['area'],
                    csv_id=row['csv_id']
                )

        except Exception as e:
            print(f"Error in read_csv_into_db_afad: {str(e)}")

