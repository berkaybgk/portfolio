import pandas as pd
import numpy as np

class Regression:

    def __init__(self, x:np.array, y:np.array):
        self.x = x.values
        self.y = y.values

    def compute_betas_linear(self) -> np.array:
        """
        Returns the beta coefficients for multiple linear regression
        """
        X = self.x
        y = self.y

        X_with_intercept = np.column_stack((np.ones(X.shape[0]), X))

        # Calculate betas: (X^T X)^(-1) X^T y
        betas = np.linalg.inv(X_with_intercept.T.dot(X_with_intercept)).dot(X_with_intercept.T).dot(y)

        return betas


    def compute_betas_polynomial(self, degree: int) -> np.array:
        """
        Computes polynomial coefficients with stronger regularization.
        """
        x = self.x
        y = self.y

        # Create polynomial features
        X_poly = self.create_polynomial_features(degree)

        # Use stronger regularization - Ridge regression essentially
        lambda_reg = 0.1  # Increased from 1e-10
        n_features = X_poly.shape[1]

        # Handle missing values in y
        if isinstance(y, pd.Series):
            y = y.fillna(y.median())
        else:
            y_median = np.nanmedian(y)
            y = np.nan_to_num(y, nan=y_median)

        try:
            # More stable computation
            XTX = X_poly.T.dot(X_poly)
            reg_term = lambda_reg * np.eye(n_features)

            # Check condition number
            if np.linalg.cond(XTX) > 1e15:
                print("Warning: Matrix is ill-conditioned. Increasing regularization.")
                lambda_reg = 1.0  # Much stronger regularization
                reg_term = lambda_reg * np.eye(n_features)

            # Use solve instead of explicit inversion
            beta = np.linalg.solve(XTX + reg_term, X_poly.T.dot(y))

            # Check for NaN values in coefficients
            if np.any(np.isnan(beta)):
                raise ValueError("NaN values in coefficients")

            return beta

        except (np.linalg.LinAlgError, ValueError) as e:
            print(f"Error during coefficient calculation: {e}")
            print("Falling back to simpler model...")
            # Fall back to a simpler model (OLS with just first degree terms)
            X_simple = np.column_stack((np.ones(len(y)), x))
            beta_simple = np.linalg.lstsq(X_simple, y, rcond=1e-3)[0]
            # Pad with zeros to match expected coefficient count
            beta_padded = np.zeros(1 + x.shape[1] * degree)
            beta_padded[:len(beta_simple)] = beta_simple
            return beta_padded



    def predict_linear(self, x_test: np.array) -> np.array:
        """
        Returns the predicted values for multivariate linear regression
        """
        x_test = x_test.values
        betas = self.compute_betas_linear()

        X_test_with_intercept = np.column_stack((np.ones(x_test.shape[0]), x_test))

        y_pred = X_test_with_intercept.dot(betas)

        return y_pred


    def predict_polynomial(self, x_test, beta):
        """
        Makes predictions with more error handling.
        """
        # Handle missing values in test data
        if isinstance(x_test, pd.DataFrame):
            x_test = x_test.fillna(0)
        else:
            x_test = np.nan_to_num(x_test)

        # Store original x
        x_orig = self.x

        # Temporarily replace self.x with x_test for feature generation
        self.x = x_test.values if hasattr(x_test, 'values') else x_test

        # Calculate degree
        n_features = self.x.shape[1]
        degree = max(1, (len(beta) - 1) // n_features)

        # Create polynomial features for test data
        X_test_poly = self.create_polynomial_features(degree)

        # Ensure feature matrix is compatible with beta
        if X_test_poly.shape[1] > len(beta):
            X_test_poly = X_test_poly[:, :len(beta)]
        elif X_test_poly.shape[1] < len(beta):
            # Pad with zeros if necessary
            pad_width = len(beta) - X_test_poly.shape[1]
            X_test_poly = np.pad(X_test_poly, ((0, 0), (0, pad_width)))

        # Predict
        y_pred = X_test_poly.dot(beta)

        # Restore original x
        self.x = x_orig

        # Check for numerical issues in predictions
        if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
            print("Warning: NaN or Inf values in predictions. Using fallback predictions.")
            # Fall back to simple mean prediction
            if isinstance(self.y, pd.Series):
                mean_y = self.y.mean()
            else:
                mean_y = np.mean(self.y)
            y_pred = np.ones_like(y_pred) * mean_y

        return y_pred

    def mean_squared_error(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Returns the MSE for the results of prediction
        """
        y_true = y_true.values
        mse = (1/len(y_true)) * np.sum((y_true - y_pred) ** 2)
        return mse


    def create_polynomial_features(self, degree: int) -> np.array:
        """
        Creates polynomial features with robust normalization.
        """
        x = self.x
        n_samples = x.shape[0]

        # Handle missing values
        if isinstance(x, pd.DataFrame):
            x = x.fillna(0)  # Replace NaN with zeros
        else:
            x = np.nan_to_num(x)  # Replace NaN with zeros for numpy arrays

        # Robust normalization - use median and IQR instead of mean/std
        # to be less affected by outliers
        x_centered = x - np.median(x, axis=0)
        iqr = np.percentile(x, 75, axis=0) - np.percentile(x, 25, axis=0)
        # Avoid division by zero
        iqr = np.where(iqr < 1e-10, 1.0, iqr)
        x_normalized = x_centered / iqr

        # Start with a column of ones for the intercept
        X_poly = np.ones((n_samples, 1))

        # Add the original features
        X_poly = np.column_stack((X_poly, x_normalized))

        # For degree 2 and higher
        for d in range(2, degree + 1):
            for col in range(x_normalized.shape[1]):
                # Clip to prevent extreme values
                col_data = np.clip(x_normalized[:, col], -5, 5)
                col_powered = np.power(col_data, d).reshape(-1, 1)
                X_poly = np.column_stack((X_poly, col_powered))

        # Check for numerical issues
        if np.any(np.isnan(X_poly)) or np.any(np.isinf(X_poly)):
            print("Warning: NaN or Inf values in polynomial features. Using fallback method.")
            # Fallback to a simpler approach
            X_poly = np.ones((n_samples, 1))
            x_safe = np.clip(x, -10, 10)  # Extreme clipping
            X_poly = np.column_stack((X_poly, x_safe))

        return X_poly



def load_and_preprocess(test_size = 0.2):
    """
    Returns
    X_train, X_test, y_train, y_test
    """
    df = pd.read_csv("resources/cancer_reg.csv")

    cutoff = int(test_size * df.shape[0])

    # Shuffle the rows of the DataFrame
    df = df.sample(frac=1, random_state=28).reset_index(drop=True)

    test, train = df[:cutoff], df[cutoff:]

    x_train = train.drop(columns=["target_death_rate"])
    x_test = test.drop(columns=["target_death_rate"])

    y_train = train["target_death_rate"]
    y_test = test["target_death_rate"]

    return x_train, x_test, y_train, y_test


if __name__ == "__main__":

    x_train, x_test, y_train, y_test = load_and_preprocess()




