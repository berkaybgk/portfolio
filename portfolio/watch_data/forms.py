from django import forms
from .prepare_category_data import (
    get_brand_model_options,
    get_movement_options,
    get_case_material_options,
    get_condition_options,
    get_scope_of_delivery_options,
    get_country_code_options
)

class WatchFeatureForm(forms.Form):
    # Get all the options from helper functions
    brand_model_choices = get_brand_model_options()
    brand_choices = [(brand, brand) for brand in get_brand_model_options().keys()]
    movement_choices = [(m, m) for m in get_movement_options()]
    case_material_choices = [(m, m) for m in get_case_material_options()]
    condition_choices = [(c, c) for c in get_condition_options()]
    scope_choices = [(s, s) for s in get_scope_of_delivery_options()]
    country_choices = [(c, c) for c in get_country_code_options()]
    
    # Form fields
    brand = forms.ChoiceField(
        choices=brand_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'brand'})
    )
    
    model = forms.ChoiceField(
        choices=[('', 'Select a model')],  # Default empty choice
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'model', 'disabled': 'disabled'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If form is bound and has brand value, populate model choices
        if self.is_bound and self.data.get('brand'):
            brand = self.data['brand']
            models = self.brand_model_choices.get(brand, [])
            self.fields['model'].choices = [('', 'Select a model')] + [(m, m) for m in models]
            self.fields['model'].widget.attrs.pop('disabled', None)
    
    movement = forms.ChoiceField(
        choices=movement_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    case_material = forms.ChoiceField(
        choices=case_material_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    case_diameter = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        min_value=20,  # Assuming minimum reasonable watch diameter
        max_value=60   # Assuming maximum reasonable watch diameter
    )
    
    year_of_production = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1900,  # Assuming minimum reasonable year
        max_value=2025   # Current year
    )
    
    condition = forms.ChoiceField(
        choices=condition_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    scope_of_delivery = forms.ChoiceField(
        choices=scope_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    country_code = forms.ChoiceField(
        choices=country_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )