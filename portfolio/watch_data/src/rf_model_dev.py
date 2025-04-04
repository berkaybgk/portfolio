import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from main import get_model_df

# Load dataset
df = get_model_df()

df = df[df["price"] < 2500000]
# Eliminate outliers, there are nearly 1500 outliers in the dataset (0.004% of the data)

high_cardinality_cols = ['model', 'brand']
country_code = ['country_code']
medium_cardinality_cols = ['case_material', 'movement']
numerical_cols = ['year_of_production', 'case_diameter']
rest_cols = ['condition', 'scope_of_delivery', 'year_unknown']

# Define preprocessing steps
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numerical_cols),
    # Use MinMaxScaler for high cardinality columns
    ("cat_high", MinMaxScaler(), high_cardinality_cols),
    # Use OneHotEncoder for medium cardinality columns
    ("cat_med", OneHotEncoder(handle_unknown='ignore'), medium_cardinality_cols),
])

# Use TargetEncoding for high cardinality columns
for col in high_cardinality_cols:
    df[col] = df.groupby(col)['price'].transform('mean')

# Define training data
X = df[numerical_cols + medium_cardinality_cols + rest_cols + country_code + high_cardinality_cols]
y = df['price']

# Set country_code to 1 if country code is US, else 0
X.loc[:, 'country_code'] = np.where(df['country_code'] == 'US', 1, 0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=28)

# Create a pipeline with preprocessing and the Random Forest model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(
        n_estimators=1200,
        max_depth=7,
        min_samples_split=7,
        random_state=28,
        n_jobs=-1,
        verbose=True
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
model_path = os.path.join(save_dir, "random_forest_model.pkl")
joblib.dump(model, model_path)
print(f"Model saved to: {model_path}")
