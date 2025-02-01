from datetime import datetime

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from .eq_data_utils import EqUtils
import logging
import traceback
import pandas as pd

logger = logging.getLogger(__name__)
eq_utils = EqUtils()

class EarthquakeDashboardView(View):
    template_name = 'eq_dashboard/dashboard.html'

    def get(self, request):
        return render(request, self.template_name)



class EarthquakeDataAPI(View):
    def get(self, request):
        try:
            # Get and validate parameters
            try:
                start_date = request.GET.get('start_date')
                end_date = request.GET.get('end_date')
                min_magnitude = float(request.GET.get('min_magnitude', 4.0))

                # Validate date format
                if not start_date or not end_date:
                    raise ValueError("Both start_date and end_date are required")

                # Convert to datetime and set time components
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

                # Set start_date to beginning of day (00:00:00)
                start_date = start_date.replace(hour=0, minute=0, second=0)

                # Set end_date to end of day (23:59:59)
                end_date = end_date.replace(hour=23, minute=59, second=59)

                # Ensure end_date is not before start_date
                if end_date < start_date:
                    raise ValueError("end_date cannot be before start_date")

                # Convert to string format for database query
                start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
                end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

            except ValueError as e:
                logger.error(f"Parameter validation error: {str(e)}")
                return JsonResponse({
                    'error': f'Invalid parameter value: {str(e)}'
                }, status=400)

            # Get the earthquake data
            data, trend_data = eq_utils.get_interval_data(start_date, end_date, min_magnitude)

            # Validate data
            if not isinstance(data, pd.DataFrame):
                logger.error(f"Invalid data type returned: {type(data)}")
                return JsonResponse({
                    'error': 'Invalid data format returned'
                }, status=500)

            if not isinstance(trend_data, pd.DataFrame):
                logger.error(f"Invalid trend data type returned: {type(trend_data)}")
                return JsonResponse({
                    'error': 'Invalid trend data format returned'
                }, status=500)

            # Convert to records and return
            earthquakes = data.to_dict(orient='records')
            trend_earthquakes = trend_data.to_dict(orient='records')

            return JsonResponse({
                'earthquakes': earthquakes,
                'trend_earthquakes': trend_earthquakes,
                'period': {
                    'start': start_date,
                    'end': end_date
                }
            })

        except Exception as e:
            logger.error(f"Error in EarthquakeDataAPI: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'error': str(e)
            }, status=500)