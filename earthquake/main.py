import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib


def find_largest_nearby_earthquake(data, row):
    """
    Find the largest earthquake within 0.5 degrees longitude and latitude
    proximity in the last 20 years, excluding the last week, for a given earthquake record.

    Parameters:
    -----------
    data : pandas.DataFrame
        Full earthquake dataset
    row : pandas.Series
        Current earthquake record to find nearby largest earthquake for

    Returns:
    --------
    float
        Magnitude of the largest nearby earthquake (0 if no nearby earthquakes found)
    """
    # Ensure the index is reset
    data = data.reset_index(drop=True)

    # Filter for earthquakes in the last 20 years
    current_date = pd.to_datetime(row['time'])
    recent_data = data[
        (pd.to_datetime(data['time']) >= current_date - pd.Timedelta(days=20 * 365)) &
        (pd.to_datetime(data['time']) < current_date - pd.Timedelta(days=7))
        ]

    # Filter for earthquakes within 0.5 degrees proximity
    nearby_quakes = recent_data[
        (abs(recent_data['latitude'] - row['latitude']) <= 0.5) &
        (abs(recent_data['longitude'] - row['longitude']) <= 0.5)
        ]

    # Return the magnitude of the largest nearby earthquake
    # If no nearby earthquakes, return 0
    return nearby_quakes['mag'].max() if len(nearby_quakes) > 0 else 0


def find_recent_earthquakes(data):
    """
    Find recent earthquakes within 0.4 degrees latitude/longitude and 2 weeks of the current earthquake.

    Parameters:
    -----------
    data : pandas.DataFrame
        Full earthquake dataset

    Returns:
    --------
    pandas.DataFrame
        Earthquake dataset with a new column `close_event` indicating if there was a recent earthquake nearby
    """
    # Parameters
    magnitude_threshold = 4.3  # Minimum magnitude to consider
    proximity_threshold = 0.4  # Proximity in degrees of latitude/longitude
    time_threshold = pd.Timedelta(weeks=2)  # Time window (2 week)

    # Ensure the DataFrame is sorted by time for efficiency
    data = data.sort_values("time").reset_index(drop=True)

    # Initialize a new column
    data["close_event"] = 0

    # Iterate through each row
    for i, row in data.iterrows():
        # Define current earthquake properties
        current_time = row["time"]
        current_lat = row["latitude"]
        current_lon = row["longitude"]

        # Find earthquakes that meet the criteria
        recent_quakes = data[
            (data["time"] < current_time) &
            (data["time"] >= current_time - time_threshold) &
            (np.abs(data["latitude"] - current_lat) <= proximity_threshold) &
            (np.abs(data["longitude"] - current_lon) <= proximity_threshold) &
            (data["mag"] > magnitude_threshold)
            ]

        # Update the `close_event` column
        data.at[i, "close_event"] = 1 if not recent_quakes.empty else 0

    return data


def load_and_preprocess(csv_path):
    """
    Load the earthquake dataset and preprocess it.

    Parameters:
    -----------
    csv_path : str
        Path to the earthquake dataset CSV file

    Returns:
    --------
    pandas.DataFrame
        Processed earthquake dataset
    """
    df = pd.read_csv(csv_path)

    # Drop the imbalanced magnitudes
    df.drop(df[df["mag"] < 4.0].index, inplace=True)

    # Sort the dfFrame by time
    df = df.sort_values('time').reset_index(drop=True)

    df["time"] = pd.to_datetime(df["time"].str[:10])

    # Extract date features
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['day'] = df['time'].dt.day
    df['dayofweek'] = df['time'].dt.dayofweek

    # Drop columns with too many missing values
    df.drop(columns=["dmin", "horizontalError", "depthError", "magError"], inplace=True)

    # Fill missing values
    for col in ["nst", "gap", "magNst", "rms"]:
        df[col] = df[col].fillna(df[col].median())

    # We can drop the id, updated, type, place, magNst, status, net, locationSource,
    # and magSource columns as they are not informative
    df.drop(columns=["id", "updated", "type", "place", "magNst",
                       "status", "locationSource", "magSource", "net"], inplace=True)

    # Find if there was a recent significant earthquake nearby
    df = find_recent_earthquakes(df)

    # Find the largest nearby earthquake for each record
    df['largest_nearby_earthquake'] = df.apply(
        lambda row: find_largest_nearby_earthquake(df, row),
        axis=1
    )

    # Create a target variable
    df['target'] = 0  # Initialize target column

    # Create the target variable
    for i in range(len(df) - 1):
        current_time = df.loc[i, 'time']
        # Filter events within the next two weeks and within 0.5 degrees proximity
        mask = (df['time'] > current_time) & (df['time'] <= current_time + pd.Timedelta(weeks=2)) & (
                    np.abs(df['latitude'] - df.loc[i, 'latitude']) <= 1) & (
                           np.abs(df['longitude'] - df.loc[i, 'longitude']) <= 1)

        # If there is at least one significant earthquake, set the target to 1
        if df[mask]['mag'].max() >= 5.0:
            df.loc[i, 'target'] = 1

    return df


def split_with_sequence(df, sequence_length=365*3):
    """
    Split the data into sequences and create the target variable.
    The target variable is defined as whether there is a significant earthquake within the next two weeks.

    Parameters:
    -----------
    df : pandas.DataFrame
        Processed earthquake dataset

    Returns:
    --------
    torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor
        Train and test sequences and targets
    """

    # Copy the dataframe to avoid modifying the original
    data = df.copy()

    # Ensure the data is sorted by time
    data = data.sort_values('time').reset_index(drop=True)

    # Select features
    features = ['latitude', 'longitude', 'depth', 'mag', 'nst', 'gap', 'rms', 'year', 'month', 'day', 'dayofweek', 'close_event', 'largest_nearby_earthquake']
    def create_sequences(df, features, seq_length):
        sequences = []
        targets = []
        for i in range(len(df) - seq_length):
            seq = df[features].iloc[i:i+seq_length].values
            label = df['target'].iloc[i+seq_length]
            sequences.append(seq)
            targets.append(label)
        return np.array(sequences), np.array(targets)

    sequences, targets = create_sequences(data, features, sequence_length)

    split_index = int(len(sequences) * 0.8)

    # Split sequences and targets
    X_train = sequences[:split_index]
    y_train = targets[:split_index]
    X_test = sequences[split_index:]
    y_test = targets[split_index:]

    # Normalize features
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
    X_test = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

    # Save the scaler
    joblib.dump(scaler, "scaler.pkl")

    # Convert to tensors
    X_train = torch.tensor(X_train, dtype=torch.float)
    y_train = torch.tensor(y_train, dtype=torch.float)

    X_test = torch.tensor(X_test, dtype=torch.float)
    y_test = torch.tensor(y_test, dtype=torch.float)

    return X_train, y_train, X_test, y_test


class EarthquakeLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(EarthquakeLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Define LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)

        # Define output layer
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))

        out = out[:, -1, :]
        out = self.fc(out)
        return out

def main(df, sequence_length=365*3, num_epochs=15):
    X_train, y_train, X_test, y_test = split_with_sequence(df, sequence_length)

    batch_size = 64

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    # Do not shuffle to maintain temporal order
    train_loader = DataLoader(train_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Calculate class weights
    class_counts = np.bincount(y_train.numpy().astype(int))

    # Define device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Calculate class weights
    pos_weight = class_counts[0] / class_counts[1]
    pos_weight = torch.tensor([pos_weight], dtype=torch.float).to(device)

    # Define loss function
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    features = ['latitude', 'longitude', 'depth', 'mag', 'nst', 'gap', 'rms', 'year', 'month', 'day', 'dayofweek',
                'close_event', 'largest_nearby_earthquake']

    # Model parameters
    input_size = len(features)
    hidden_size = 64
    num_layers = 2
    output_size = 1  # Binary classification

    # Initialize model
    model = EarthquakeLSTM(input_size, hidden_size, num_layers, output_size)
    model.to(device)

    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0003)

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0
        for sequences_batch, labels_batch in train_loader:
            sequences_batch = sequences_batch.to(device)
            labels_batch = labels_batch.to(device).unsqueeze(1)

            # Forward pass
            outputs = model(sequences_batch)
            loss = criterion(outputs, labels_batch)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        # Print loss per epoch
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss/len(train_loader):.4f}')

    model.eval()
    with torch.no_grad():
        all_outputs = []
        all_labels = []
        for sequences_batch, labels_batch in test_loader:
            sequences_batch = sequences_batch.to(device)
            labels_batch = labels_batch.to(device).unsqueeze(1)
            outputs = model(sequences_batch)
            outputs = torch.sigmoid(outputs)  # Since we didn't apply sigmoid in the model

            all_outputs.extend(outputs.cpu().numpy())
            all_labels.extend(labels_batch.cpu().numpy())

    # Binarize outputs
    threshold = 0.5
    predicted = [1 if x >= threshold else 0 for x in all_outputs]

    # Evaluation metrics
    accuracy = accuracy_score(all_labels, predicted)
    precision = precision_score(all_labels, predicted, zero_division=0)
    recall = recall_score(all_labels, predicted, zero_division=0)
    f1 = f1_score(all_labels, predicted, zero_division=0)
    conf_matrix = confusion_matrix(all_labels, predicted)

    print("Evaluation Metrics:")
    print(f'Accuracy: {accuracy:.4f}')
    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1 Score: {f1:.4f}')
    print()
    print('Confusion Matrix:')
    print(conf_matrix)

    # Extract the last two weeks of data based on the 'time' column
    last_time = df['time'].max()
    two_weeks_ago = last_time - pd.Timedelta(weeks=2)
    last_two_weeks = df[df['time'] >= two_weeks_ago]

    # If no rows found or no test predictions match, return empty or partial results
    if len(last_two_weeks) == 0 or len(all_outputs) == 0:
        print("Warning: No data found for the last two weeks or no test predictions available.")
        return df.iloc[0:0]  # Return empty DataFrame with same columns

    # Create a new DataFrame with predictions
    result_df = last_two_weeks.copy()

    # Select the last few predictions from test data
    num_last_predictions = len(last_two_weeks)
    start_idx = len(all_outputs) - num_last_predictions

    result_df['actual_label'] = y_test[-num_last_predictions:].numpy()
    result_df['predicted_prob'] = all_outputs[start_idx:]
    result_df['predicted_label'] = [1 if x >= 0.5 else 0 for x in result_df['predicted_prob']]

    return result_df


if __name__ == "__main__":

    earthquake_df = load_and_preprocess("resources/90_25_turkey.csv")

    prediction_results = main(earthquake_df, sequence_length=1000, num_epochs=12)

    print()
    for i in range(len(prediction_results)):
        print(f"The earthquake at", prediction_results.iloc[i]['time']
              , f"with coordinates {prediction_results.iloc[i]['latitude']}/{prediction_results.iloc[i]['longitude']}"
              , "is predicted to have a significant earthquake within the next two weeks:"
              , prediction_results.iloc[i]['predicted_label'])


