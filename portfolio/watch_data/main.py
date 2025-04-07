import os
import pandas as pd
import numpy as np
import joblib
from .src.utils import get_model_df, get_model_avg_price, get_brand_avg_price
from .src.gradbr_model_dev import pre_process_data, predict_price

def get_predictions(n):
    # Define absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "src", "important_models")
    data_path = os.path.join(base_dir, "resources", "single_instance.csv")

    # Load and preprocess data
    df = get_model_df(data_path)
    sample_df = df.copy()
    
    X, y = pre_process_data(sample_df)

    # Load the trained model
    model_path = os.path.join(model_dir, "gradient_boosting_model.pkl")
    model = joblib.load(model_path)

    # Predict the price for the sample data
    predictions = predict_price(model, X)
    print("Sample Data:")
    print(y.values)
    print("Predicted Prices:")
    print(predictions)

def brand_avg_price(brand):
    return get_brand_avg_price(brand)

def model_avg_price(model, brand):
    return get_model_avg_price(model, brand)

def predict_watch_price(brand, model, movement,
                        case_material, year_of_production, condition,
                        country_code, scope_of_delivery, case_diameter
                        ) -> float:

    # Load the trained model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "src", "important_models")
    model_path = os.path.join(model_dir, "gradient_boosting_model.pkl")
    grad_model = joblib.load(model_path)
    # Create a DataFrame with the input data

    model = model_avg_price(model, brand)
    brand = brand_avg_price(brand)

    input_data = pd.DataFrame({
        'brand': [brand],
        'model': [model],
        'movement': [movement],
        'case_material': [case_material],
        'year_of_production': [year_of_production+0.0],
        'condition': [condition],
        'country_code': [country_code],
        'scope_of_delivery': [scope_of_delivery],
        'case_diameter': [case_diameter],
        'year_unknown': [0],
    })

    condition_ranking = {
        'Like new & unworn': 1,
        'Very good': 2,
        'New': 3,
        'Good': 4,
        'Fair': 5,
        'Unknown': 6,
        'Incomplete': 7,
        'Poor': 8
    }
    input_data['condition'] = (
        input_data['condition']
        .map(condition_ranking)  # Use map instead of replace
        .astype(int)  # Explicitly convert to int (optional but safe)
    )

    scope_ranking = {
        'Original box, original papers': 1,
        'Original box, no original papers': 3,
        'No original box, no original papers': 4,
        'Original papers, no original box': 2
    }
    input_data['scope_of_delivery'] = (
        input_data['scope_of_delivery']
        .map(scope_ranking)  # Use map instead of replace
        .astype(int)  # Explicitly convert to int (optional but safe)
    )

    # Country code is either 1 or 0 based on US or not US
    input_data['country_code'] = input_data['country_code'].apply(lambda x: 1 if x == 'US' else 0)

    # Make predictions using the loaded model
    predicted_price = predict_price(grad_model, input_data)
    return predicted_price


if __name__ == "__main__":
    # result = predict_watch_price(
    #     brand="Rolex",
    #     model="Datejust 36",
    #     movement="Automatic",
    #     case_material="Steel",
    #     year_of_production=2022,
    #     condition="Very good",
    #     country_code="US",
    #     scope_of_delivery="Original papers, no original box",
    #     case_diameter=40.0
    # )
    # print(f"Predicted Price: {result}")

    # brand="Rolex",
    # model="Datejust",
    # movement="Automatic",
    # case_material="Steel",
    # year_of_production=2022,
    # condition="Very good",
    # country_code="US",
    # scope_of_delivery="Watches",
    # case_diameter=40.0

    # print(f"Predicted Price: {result}")
    get_predictions(1)

    # input_data = pd.DataFrame({
    #     'brand': brand,
    #     'model': model,
    #     'movement': movement,
    #     'case_material': case_material,
    #     'year_of_production': year_of_production,
    #     'condition': condition,
    #     'country_code': country_code,
    #     'scope_of_delivery': scope_of_delivery,
    #     'case_diameter': case_diameter,
    #     'year_unknown': 0,
    # })

    # print(input_data)


    