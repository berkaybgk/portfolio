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
                lookback_days = int(request.GET.get('lookback_days', 30))
                min_magnitude = float(request.GET.get('min_magnitude', 4.0))
            except ValueError as e:
                logger.error(f"Parameter validation error: {str(e)}")
                return JsonResponse({
                    'error': f'Invalid parameter value: {str(e)}'
                }, status=400)

            # Log the request parameters
            logger.info(f"Fetching earthquake data with lookback_days={lookback_days}, min_magnitude={min_magnitude}")

            # Get the earthquake data
            data = eq_utils.get_data(lookback_days, min_magnitude)

            # Validate data
            if not isinstance(data, pd.DataFrame):
                logger.error(f"Invalid data type returned: {type(data)}")
                return JsonResponse({
                    'error': 'Invalid data format returned'
                }, status=500)

            # Convert to records and return
            earthquakes = data.to_dict(orient='records')
            logger.info(f"Successfully fetched {len(earthquakes)} earthquakes")

            return JsonResponse({
                'earthquakes': earthquakes
            })

        except Exception as e:
            logger.error(f"Error in EarthquakeDataAPI: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'error': str(e)
            }, status=500)
