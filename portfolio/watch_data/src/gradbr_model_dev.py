import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from main import get_model_df

def pre_process_data(df_original):
    df = df_original.copy()

    df = df[df["price"] < 200000]
    # Eliminate outliers, there are nearly 3000 outliers in the dataset (0.7% of the data)

    high_cardinality_cols = ['model', 'brand']
    country_code = ['country_code']
    medium_cardinality_cols = ['case_material', 'movement']
    numerical_cols = ['year_of_production', 'case_diameter']
    rest_cols = ['condition', 'scope_of_delivery', 'year_unknown']

    # Target Encoding for high cardinality columns
    for col in high_cardinality_cols:
        df[col] = df.groupby(col)['price'].transform('mean')

    # Define training data
    X = df[numerical_cols + medium_cardinality_cols + rest_cols + country_code + high_cardinality_cols]
    y = df['price']

    # Set country_code to 1 if country code is US, else 0
    X.loc[:, 'country_code'] = np.where(df['country_code'] == 'US', 1, 0)

    return X, y


def train_model():
    # Load dataset
    df = get_model_df()

    df = df[df["price"] < 200000]
    # Eliminate outliers, there are nearly 3000 outliers in the dataset (0.7% of the data)

    high_cardinality_cols = ['model', 'brand']
    country_code = ['country_code']
    medium_cardinality_cols = ['case_material', 'movement']
    numerical_cols = ['year_of_production', 'case_diameter']
    rest_cols = ['condition', 'scope_of_delivery', 'year_unknown']

    # Define preprocessing steps
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numerical_cols),
        ("cat_high", MinMaxScaler(), high_cardinality_cols),
        ("cat_med", OneHotEncoder(handle_unknown='ignore'), medium_cardinality_cols),
    ])

    # Target Encoding for high cardinality columns
    for col in high_cardinality_cols:
        df[col] = df.groupby(col)['price'].transform('mean')

    # Define training data
    X = df[numerical_cols + medium_cardinality_cols + rest_cols + country_code + high_cardinality_cols]
    y = df['price']

    # Set country_code to 1 if country code is US, else 0
    X.loc[:, 'country_code'] = np.where(df['country_code'] == 'US', 1, 0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline with preprocessing and the Gradient Boosting model
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", GradientBoostingRegressor(
            n_estimators=180,
            learning_rate=0.2,
            max_depth=11,
            min_samples_split=2,
            random_state=42,
            verbose=1
        ))
    ])

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Squared Error: {mse:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"R² Score: {r2:.4f}")
    print("There are large outliers in the dataset, considering MAE will be more appropriate than RMSE.")

    # Save the trained model
    save_dir = "saved_models"
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "gradient_boosting_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")


def predict_price(model, input_data):
    """
    Predict the price of a watch using the trained model.

    Parameters:
    - model: The trained model.
    - input_data: A DataFrame containing the input data for prediction.

    Returns:
    - predictions: The predicted prices.
    """
    # Preprocess the input data
    preprocessed_data = model.named_steps['preprocessor'].transform(input_data)

    # Make predictions
    predictions = model.named_steps['regressor'].predict(preprocessed_data)

    return predictions


def get_predictions(n):
    save_dir = "important_models"

    df = get_model_df("../resources/single_instance.csv")

    # Get a random sample of 5 rows from the DataFrame
    sample_df = df.copy()

    # Preprocess the data
    X, y = pre_process_data(sample_df)

    # Load the trained model
    model_path = os.path.join(save_dir, "gradient_boosting_model.pkl")
    model = joblib.load(model_path)
    print(f"Model loaded from: {model_path}")

    # Predict the price for the sample data
    predictions = predict_price(model, X)
    print("Sample Data:")
    print(y.values)
    print("Predicted Prices:")
    print(predictions)


if __name__ == '__main__':

    # Train the model
    # train_model()

    get_predictions(1)
