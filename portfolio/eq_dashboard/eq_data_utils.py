from django.utils import timezone
from datetime import timedelta
from .models import EarthquakeDataUSGS
from typing import Tuple
import pandas as pd
from django.db.models import QuerySet


class EqUtils:
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
                time__lt=lookback_cutoff,
                mag__gte=min_magnitude
            )
            .values('time', 'latitude', 'longitude', 'depth', 'mag', 'place')
        )

        def queryset_to_dataframe(queryset: QuerySet) -> pd.DataFrame:
            # Convert QuerySet to DataFrame
            df = pd.DataFrame(list(queryset))
            if not df.empty:
                # Rename mag to magnitude
                df.rename(columns={'mag': 'magnitude', 'time': 'date'}, inplace=True)
                # Format date
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%d-%m-%Y')
            return df

        return queryset_to_dataframe(current_data), queryset_to_dataframe(trend_data)

    def read_csv_into_db(self, data_path: str):
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
            print(f"Error in read_csv_into_db: {str(e)}")

