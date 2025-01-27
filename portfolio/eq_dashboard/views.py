from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from .eq_data_utils import EqUtils
import traceback
import pandas as pd

eq_utils = EqUtils()

class EarthquakeDashboardView(View):
    template_name = 'eq_dashboard/dashboard.html'

    def get(self, request):
        return render(request, self.template_name)

class EarthquakeDataAPI(View):
    def get(self, request):
        try:
            # Validate input parameters
            try:
                lookback_days = int(request.GET.get('lookback_days', 30))
                min_magnitude = float(request.GET.get('min_magnitude', 4.0))
            except ValueError as e:
                return JsonResponse({
                    'error': f'Invalid parameter value: {str(e)}',
                    'status': 'error'
                }, status=400)

            # Get the earthquake data
            data = eq_utils.get_data(lookback_days, min_magnitude)

            # Validate that data is a pandas DataFrame
            if not isinstance(data, pd.DataFrame):
                return JsonResponse({
                    'error': 'Invalid data format returned',
                    'status': 'error'
                }, status=500)

            # Check if DataFrame is empty
            if data.empty:
                return JsonResponse({
                    'earthquakes': [],
                    'status': 'success'
                })

            # Convert to dict and return
            return JsonResponse({
                'earthquakes': data.to_dict(orient='records'),
                'status': 'success'
            })

        except Exception as e:
            # Log the full error for debugging
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)