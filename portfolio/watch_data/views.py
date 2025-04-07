from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import json
from .forms import WatchFeatureForm
from .prepare_category_data import get_brand_model_options
from .main import predict_watch_price
# from .src.main import predict_watch_price

def watch_feature_form(request):
    if request.method == 'POST':
        form = WatchFeatureForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            brand = form.cleaned_data['brand']
            model = form.cleaned_data['model']
            movement = form.cleaned_data['movement']
            case_material = form.cleaned_data['case_material']
            case_diameter = form.cleaned_data['case_diameter']
            year_of_production = form.cleaned_data['year_of_production']
            condition = form.cleaned_data['condition']
            scope_of_delivery = form.cleaned_data['scope_of_delivery']
            country_code = form.cleaned_data['country_code']

            try:
                predicted_price = predict_watch_price(
                    brand, model, movement,
                    case_material, year_of_production, condition,
                    country_code, scope_of_delivery, case_diameter
                )
            except Exception as e:
                # Handle prediction error
                predicted_price = "Error in prediction: " + str(e)

            # Render form with prediction
            return render(request, 'watch_data/watch_feature_form.html', {
                'form': form,
                'predicted_price': predicted_price,
                'brand_models': json.dumps(get_brand_model_options(), cls=DjangoJSONEncoder, ensure_ascii=False)
            })
    else:
        form = WatchFeatureForm()
    
    return render(request, 'watch_data/watch_feature_form.html', {
        'form': form,
        'brand_models': json.dumps(get_brand_model_options(), cls=DjangoJSONEncoder, ensure_ascii=False)
    })
