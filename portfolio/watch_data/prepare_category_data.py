from .src import main
import os
import pandas as pd

def get_brand_models_mapping(df):
    """Extract brand-model mapping from the dataframe."""
    brand_models = {}
    for brand in df['brand'].unique():
        brand_models[brand] = sorted(df[df['brand'] == brand]['model'].unique())
    return brand_models

def get_categorical_data(df):
    """Extract all categorical data from the dataframe."""
    # Convert conditions to strings based on the mapping
    condition_ranking = {
        1: 'Like new & unworn',
        2: 'Very good',
        3: 'New',
        4: 'Good',
        5: 'Fair',
        6: '-',
        7: 'Incomplete',
        8: 'Poor'
    }
    
    # Convert scope of delivery to strings based on the mapping
    scope_ranking = {
        1: 'Original box, original papers',
        2: 'Original box, no original papers',
        3: 'No original box, no original papers',
        4: 'Original papers, no original box'
    }
    
    categorical_data = {
        'movement': sorted(df['movement'].unique()),
        'case_material': sorted(df['case_material'].unique()),
        'case_diameter': sorted(df['case_diameter'].unique()),
        'year_of_production': sorted(df['year_of_production'].unique()),
        'condition': sorted([condition_ranking[cond] for cond in df['condition'].unique()]),
        'scope_of_delivery': sorted([scope_ranking[scope] for scope in df['scope_of_delivery'].unique()]),
        'country_code': ['US', 'NOT US']
    }
    return categorical_data

def save_categorical_data():
    """Save brand-model mapping and other categorical data to CSV files."""
    # Get the data from the CSV file
    path = os.path.join(os.path.dirname(__file__), "resources", "cleaned_watches_data_fixed.csv")
    df = main.get_model_df(path)
    
    # Get brand-model mapping
    brand_models = get_brand_models_mapping(df)
    
    # Save brand-model mapping
    brand_model_rows = []
    for brand, models in brand_models.items():
        for model in models:
            brand_model_rows.append({'brand': brand, 'model': model})
    
    brand_model_df = pd.DataFrame(brand_model_rows)
    brand_model_df.to_csv(os.path.join(os.path.dirname(__file__), "resources", "brand_models.csv"), index=False)
    
    # Get and save other categorical data
    categorical_data = get_categorical_data(df)
    
    # Save each category to a separate CSV file
    for category, values in categorical_data.items():
        df_category = pd.DataFrame(values, columns=[category])
        df_category.to_csv(os.path.join(os.path.dirname(__file__), "resources", f"{category}.csv"), index=False)

def check_category_data():
    # the csv is inside watch_data (app) / resources
    path = os.path.join(os.path.dirname(__file__), "resources", "cleaned_watches_data_fixed.csv")

    df = main.get_model_df(path)

    brands = df["brand"].unique()
    models = df["model"].unique()
    movement = df["movement"].unique()
    case_material = df["case_material"].unique()

    # find and replace the "-" with "Unknown"
    movement = [m if m != "-" else "Unknown" for m in movement]
    case_material = [m if m != "-" else "Unknown" for m in case_material]

    case_diameter = df["case_diameter"].unique()
    year_of_production = df["year_of_production"].unique()
    condition = df["condition"].unique()
    scope_of_delivery = df["scope_of_delivery"].unique()
    country_code = ['US', 'NOT US']

    # Convert conditions to strings based on the mapping
    condition_ranking = {
        1: 'Like new & unworn',
        2: 'Very good',
        3: 'New',
        4: 'Good',
        5: 'Fair',
        6: 'Unknown',
        7: 'Incomplete',
        8: 'Poor'
    }
    condition = [condition_ranking[cond] for cond in condition]

    # Convert scope of delivery to strings based on the mapping
    scope_ranking = {
        1: 'Original box, original papers',
        2: 'Original box, no original papers',
        3: 'No original box, no original papers',
        4: 'Original papers, no original box'
    }
    scope_of_delivery = [scope_ranking[scope] for scope in scope_of_delivery]
    
    print("Brands: ", brands)
    print("Models: ", models)
    print("Movement: ", movement)
    print("Case Material: ", case_material)
    print("Case Diameter: ", case_diameter)
    print("Year of Production: ", year_of_production)
    print("Condition: ", condition)
    print("Scope of Delivery: ", scope_of_delivery)
    print("Country Code: ", country_code)
    

def get_condition_options():
    conditions = [
        'Like new & unworn',
        'Very good',
        'New',
        'Good',
        'Fair',
        'Unknown',
        'Incomplete',
        'Poor'
    ]
    return conditions

def get_scope_of_delivery_options():
    scope_of_delivery = [
        'Original box, original papers',
        'Original box, no original papers',
        'No original box, no original papers',
        'Original papers, no original box'
    ]
    return scope_of_delivery

def get_country_code_options():
    country_code = ['US', 'NOT US']
    return country_code

def get_movement_options():
    movement = [
        'Automatic',
        'Manual winding',
        'Quartz',
        'Unknown',
        'Solar',
        'Smartwatch',
    ]
    return movement

def get_case_material_options():
    case_materials = [
        'Gold/Steel', 'Steel', 'White gold', 'Rose gold', 'Yellow gold', 'Platinum',
    'Titanium', 'Silver', 'Ceramic', 'Bronze', 'Carbon', 'Red gold', 'Unknown', 'Plastic',
    'Sapphire crystal', 'Gold-plated', 'Aluminum', 'Tantalum', 'Brass',
    'Palladium', 'Tungsten', 'Yellow gold and steel', 'White gold and steel',
    'Rose gold and steel']
    return case_materials

def get_brand_model_options():
    path = os.path.join(os.path.dirname(__file__), "resources", "brand_models.csv")
    df = pd.read_csv(path)
    brand_model = {}
    for brand in df["brand"].unique():
        # Clean and sanitize the model names
        models = df[df["brand"] == brand]["model"].unique().tolist()
        cleaned_models = [str(model).strip() for model in models if pd.notna(model)]
        brand_model[str(brand).strip()] = cleaned_models

    # Sort the brand_model dictionary by brand names
    brand_model = dict(sorted(brand_model.items(), key=lambda item: item[0]))

    return brand_model


if __name__ == "__main__":
    # save_categorical_data()
    print(get_case_material_options())


