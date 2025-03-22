import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from regression import Regression

def load_and_preprocess(test_size=0.2, add_noise=False, noise_scale=1.0):
    """
    Loads and preprocesses data with more robust handling.
    """
    try:
        df = pd.read_csv("resources/cancer_reg.csv")

        # Keep only numeric columns
        numeric_cols = df.select_dtypes(include=np.number).columns
        df = df[numeric_cols]

        # Handle missing values
        df = df.fillna(df.median())

        # Keep only columns with variation
        std_cols = df.columns[df.std() > 0]
        df = df[std_cols]
        print(f"After removing zero-variance columns: {df.shape}")

        # Add noise if requested
        if add_noise:
            np.random.seed(42)
            noise = np.random.normal(0, noise_scale, size=df.shape[0])
            df['Noise'] = noise

        # Make sure target column exists and is numeric
        if "target_deathrate" in df.columns:
            target_column = "target_deathrate"
        else:
            print("Warning: target_deathrate not found. Using first column as target.")
            target_column = df.columns[0]

        # Split train/test
        cutoff = int(test_size * df.shape[0])
        df = df.sample(frac=1, random_state=35).reset_index(drop=True)
        test, train = df[:cutoff], df[cutoff:]

        x_train = train.drop(columns=[target_column])
        x_test = test.drop(columns=[target_column])
        y_train = train[target_column]
        y_test = test[target_column]

        return x_train, x_test, y_train, y_test

    except Exception as e:
        print(f"Error in data preprocessing: {e}")
        return None, None, None, None


def predict_polynomial(x_train, x_test, y_train, y_test):
    try:
        lr = Regression(x_train, y_train)

        # Use degree 3
        degree = 2
        print(f"Training with polynomial degree {degree}")
        betas = lr.compute_betas_polynomial(degree)

        # Use the updated predict method
        y_pred = lr.predict_polynomial(x_test, betas)

        mse = lr.mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error on Test Data: {mse}")

        # Plot results
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title(f'Polynomial Regression (Degree {degree})')

        # Add perfect prediction line
        min_val = min(min(y_test), min(y_pred))
        max_val = max(max(y_test), max(y_pred))
        plt.plot([min_val, max_val], [min_val, max_val], 'r--')

        # Add regression line for actual vs predicted
        z = np.polyfit(y_test, y_pred, 1)
        p = np.poly1d(z)
        plt.plot(y_test, p(y_test), 'b-')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(e)


def predict_multilinear(x_train, x_test, y_train, y_test):

    try:
        lr = Regression(x_train, y_train)

        y_pred = lr.predict_linear(x_test)

        mse = lr.mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error on Test Data: {mse}")

        plt.scatter(y_test, y_pred)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Actual vs Predicted')
        plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')
        plt.show()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    x_train, x_test, y_train, y_test = load_and_preprocess()

    predict_polynomial(x_train, x_test, y_train, y_test)

    # predict_multilinear(x_train, x_test, y_train, y_test)
