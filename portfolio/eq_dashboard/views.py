from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from .eq_data_utils import EqUtils

eq_utils = EqUtils()

class EarthquakeDashboardView(View):
    template_name = 'eq_dashboard/dashboard.html'

    def get(self, request):
        # This will be our main dashboard view
        return render(request, self.template_name)


class EarthquakeDataAPI(View):
    def get(self, request):
        # Get lookback days from request, default to 30
        lookback_days = int(request.GET.get('lookback_days', 30))
        min_magnitude = float(request.GET.get('min_magnitude', 4.0))

        # Get the earthquake data
        data = eq_utils.get_data(lookback_days, min_magnitude)

        return JsonResponse({
            'earthquakes': data.to_dict(orient='records')
        })

