import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from regression import Regression

def load_and_preprocess(test_size=0.2, add_noise=False, noise_scale=1.0):
    """
    Returns X_train, X_test, y_train, y_test

    Parameters:
    - test_size: proportion of data to use for testing
    - add_noise: whether to add a noise column
    - noise_scale: standard deviation of the noise
    """
    df = pd.read_csv("resources/linear_trial.csv")

    # Add a column with random noise if requested
    if add_noise:
        np.random.seed(42)
        noise = np.random.normal(0, noise_scale, size=df.shape[0])
        df['Noise'] = noise

    cutoff = int(test_size * df.shape[0])

    # Shuffle the rows of the DataFrame
    df = df.sample(frac=1, random_state=35).reset_index(drop=True)

    test, train = df[:cutoff], df[cutoff:]

    x_train = train.drop(columns=["Y"])
    x_test = test.drop(columns=["Y"])

    y_train = train["Y"]
    y_test = test["Y"]

    return x_train, x_test, y_train, y_test


if __name__ == "__main__":
    x_train, x_test, y_train, y_test = load_and_preprocess()

    lr = Regression(x_train, y_train)

    betas = lr.compute_betas_linear()
    print(f"Beta coefficients: {betas}")

    y_pred = lr.predict_linear(x_test)

    mse = lr.mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error on Test Data: {mse}")

    # For multivariate data, plotting becomes more complex
    # You might want to plot predicted vs. actual values instead
    import matplotlib.pyplot as plt
    plt.scatter(y_test, y_pred)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title('Actual vs Predicted')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')
    plt.show()

