import pandas as pd
import numpy as np

class EarthquakeAnalysisUtils():

    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("A dataframe must be provided")
        self.df = df

    def shape_raw_data(self) -> pd.DataFrame:    
        df = self.df.copy()
        
        # Convert date column to pandas datetime
        df['date'] = pd.to_datetime(df['date'])
        
        end_date = df["date"].max()
        start_date = df["date"].min()
        
        # Create weekly date ranges from end_date to start_date
        date_ranges = pd.date_range(end=end_date, start=start_date, freq='W')
        
        # Initialize the result dataframe
        result_df = pd.DataFrame(index=date_ranges)
        
        # Define time periods to analyze (in days)
        time_periods = {
            'week_before': 7,
            'two_weeks_before': 14,
            'month_before': 30,
            'year_before': 365,
            'three_years_before': 1095
        }
        
        for period_name, days in time_periods.items():
            # For each date in our weekly ranges
            for current_date in date_ranges:
                period_start = current_date - pd.Timedelta(days=days)
                period_end = current_date - pd.Timedelta(days=days-7 if period_name == 'week_before' else 0)
                
                # Filter earthquakes for the current period
                mask = (df['date'] >= period_start) & (df['date'] < period_end)
                period_data = df[mask]
                
                if len(period_data) > 0:
                    # Calculate statistics
                    result_df.at[current_date, f'{period_name}_count'] = len(period_data)
                    result_df.at[current_date, f'{period_name}_avg_magnitude'] = period_data['magnitude'].mean()
                    result_df.at[current_date, f'{period_name}_max_magnitude'] = period_data['magnitude'].max()
                    result_df.at[current_date, f'{period_name}_count_lt_5'] = len(period_data[period_data['magnitude'] < 5.0])
                    result_df.at[current_date, f'{period_name}_count_gt_5'] = len(period_data[period_data['magnitude'] >= 5.0])
                    result_df.at[current_date, f'{period_name}_avg_depth'] = period_data['depth'].mean()
                    
                    # Get depth of largest earthquake
                    max_mag_eq = period_data.loc[period_data['magnitude'].idxmax()]
                    result_df.at[current_date, f'{period_name}_max_eq_depth'] = max_mag_eq['depth']
                    
                    # Calculate days since largest earthquake
                    days_since = (current_date - max_mag_eq['date']).days
                    result_df.at[current_date, f'{period_name}_days_since_max'] = days_since
                else:
                    # Fill with zeros if no earthquakes in the period
                    result_df.at[current_date, f'{period_name}_count'] = 0
                    result_df.at[current_date, f'{period_name}_avg_magnitude'] = 0
                    result_df.at[current_date, f'{period_name}_max_magnitude'] = 0
                    result_df.at[current_date, f'{period_name}_count_lt_5'] = 0
                    result_df.at[current_date, f'{period_name}_count_gt_5'] = 0
                    result_df.at[current_date, f'{period_name}_avg_depth'] = 0
                    result_df.at[current_date, f'{period_name}_max_eq_depth'] = 0
                    result_df.at[current_date, f'{period_name}_days_since_max'] = days
        
        # Forward fill any remaining NaN values
        result_df = result_df.fillna(method='ffill')
        
        # Drop first 3 years of data
        cutoff_date = start_date + pd.DateOffset(years=3)
        result_df = result_df[result_df.index >= cutoff_date]
        
        return result_df

