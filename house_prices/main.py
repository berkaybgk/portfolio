import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler


def clean_and_preprocess_data(data):

    def parse_date(df):
        year = df['date'].apply(lambda x: x[:4])
        month = df['date'].apply(lambda x: x[4:6])
        day = df['date'].apply(lambda x: x[6:8])

        df['year'] = year
        df['month'] = month
        df['day'] = day

        df.drop('date', axis=1, inplace=True)

        return df

    def parse_zipcode(df):
        # Take the 3rd digit of the zipcode
        df['zipcode'] = df['zipcode'].apply(lambda x: str(x)[2])

        # Convert to int
        df['zipcode'] = df['zipcode'].astype(int)

        return df

    # Parse date
    data = parse_date(data)

    # Parse zipcode
    # data = parse_zipcode(data)
    data.drop('zipcode', axis=1, inplace=True)

    # Drop the id column
    data.drop('id', axis=1, inplace=True)

    # Drop the outliers
    # sqft_living < 8000
    data = data[data['sqft_living'] < 8000]

    skewed_features = ['sqft_lot', 'waterfront', 'sqft_lot15']

    # data[skewed_features] = np.log1p(data[skewed_features])

    # We know that there is no missing data in the dataset
    return data


class HousePricesModel(nn.Module):
    def __init__(self, input_size):
        super(HousePricesModel, self).__init__()

        self.fc1 = nn.Linear(input_size, 64)
        self.dropout1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(64, 64)
        self.dropout2 = nn.Dropout(0.2)
        self.fc3 = nn.Linear(64, 32)
        self.dropout3 = nn.Dropout(0.2)
        self.fc4 = nn.Linear(32, 1)


    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout2(x)
        x = torch.relu(self.fc3(x))
        x = self.dropout3(x)
        x = self.fc4(x)

        return x


def main():
    # Load data
    df = pd.read_csv('resources/kc_house_data.csv')

    # Clean and preprocess data
    df = clean_and_preprocess_data(df)

    # Split data into features and target
    X = df.drop('price', axis=1)
    y = df['price']

    # Initialize the scaler
    scaler = StandardScaler()

    # Split data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Scale the features
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Scale the target variable (optional but can help with training)
    y_scaler = StandardScaler()
    y_train_scaled = y_scaler.fit_transform(y_train.values.reshape(-1, 1))
    y_test_scaled = y_scaler.transform(y_test.values.reshape(-1, 1))

    # Convert to tensors with explicit casting to float32
    X_train_tensor = torch.FloatTensor(X_train_scaled)
    y_train_tensor = torch.FloatTensor(y_train_scaled)

    X_test_tensor = torch.FloatTensor(X_test_scaled)
    y_test_tensor = torch.FloatTensor(y_test_scaled)

    # Create a DataLoader
    train_dataset = torch.utils.data.TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # Create the model
    model = HousePricesModel(X_train_scaled.shape[1])

    # Define the loss function
    criterion = nn.MSELoss()

    # Define the optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Training loop with improved logging
    num_epochs = 60
    best_loss = float('inf')

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        batch_count = 0

        for X_batch, y_batch in train_loader:
            # Forward pass
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            batch_count += 1

        epoch_loss = running_loss / batch_count
        print(f'Epoch {epoch + 1}/{num_epochs}, Average Loss: {epoch_loss:.6f}')

        # Save best model
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            torch.save(model.state_dict(), 'best_model.pth')

    # Evaluate the model
    model.eval()
    with torch.no_grad():
        y_pred_scaled = model(X_test_tensor)
        test_loss = criterion(y_pred_scaled, y_test_tensor)

        # Convert predictions back to original scale
        y_pred = y_scaler.inverse_transform(y_pred_scaled.numpy())
        y_true = y_scaler.inverse_transform(y_test_tensor.numpy())

        # Calculate metrics in original scale
        mse = np.mean((y_pred - y_true) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_pred - y_true))

    print('\nEvaluation Results:')
    print(f'Test Loss (scaled): {test_loss.item():.6f}')
    print(f'RMSE (original scale): ${rmse:.2f}')
    print(f'MAE (original scale): ${mae:.2f}')

    # Get r^2 score
    from sklearn.metrics import r2_score
    r2 = r2_score(y_true, y_pred)
    print(f'R^2: {r2:.6f}')


if __name__ == '__main__':
    main()
