import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import pandas as pd
from main import get_model_df
import os

# Set random seeds for reproducibility
torch.manual_seed(28)
np.random.seed(28)

# Load dataset
df = get_model_df()

df = df[df["price"] < 200000]

# Define column types
high_cardinality_cols = ['model', 'brand']
country_code = ['country_code']
medium_cardinality_cols = ['case_material', 'movement']
numerical_cols = ['year_of_production', 'case_diameter']
rest_cols = ['condition', 'scope_of_delivery', 'year_unknown']

# Apply target encoding for high cardinality columns
for col in high_cardinality_cols:
    df[col] = df.groupby(col)['price'].transform('mean')

# Prepare features and target
X = df[numerical_cols + medium_cardinality_cols + rest_cols + country_code + high_cardinality_cols]
y = df['price'].values

# Set country_code to binary (US=1, others=0)
X.loc[:, 'country_code'] = np.where(df['country_code'] == 'US', 1, 0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=28)

# Define preprocessing
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numerical_cols),
    ("cat_high", MinMaxScaler(), high_cardinality_cols),
    ("cat_med", OneHotEncoder(handle_unknown='ignore'), medium_cardinality_cols),
])

# Fit preprocessor on training data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Convert to numpy arrays if they're sparse matrices
if hasattr(X_train_processed, 'toarray'):
    X_train_processed = X_train_processed.toarray()
    X_test_processed = X_test_processed.toarray()

# Get the number of features after preprocessing
n_features = X_train_processed.shape[1]

# Custom Dataset class
class WatchPriceDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Create datasets and dataloaders
train_dataset = WatchPriceDataset(X_train_processed, y_train)
test_dataset = WatchPriceDataset(X_test_processed, y_test)

batch_size = 512
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Define the neural network
class WatchPricePredictor(nn.Module):
    def __init__(self, input_size):
        super(WatchPricePredictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),

            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),

            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),

            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.network(x)

# Initialize model, loss function, and optimizer
model = WatchPricePredictor(n_features)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.1)

# Training function
def train_model(model, train_loader, test_loader, epochs=100, patience=10):
    best_loss = float('inf')
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0

        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)

        train_loss /= len(train_loader.dataset)

        # Validation
        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                test_loss += loss.item() * X_batch.size(0)

        test_loss /= len(test_loader.dataset)
        scheduler.step(test_loss)

        print(f'Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}')

        # Early stopping
        if test_loss < best_loss:
            best_loss = test_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), 'saved_models/best_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f'Early stopping at epoch {epoch+1}')
                break

# Train the model
train_model(model, train_loader, test_loader, epochs=100)

# Load best model
model.load_state_dict(torch.load('saved_models/best_model.pth'))

# Evaluation function
def evaluate_model(model, test_loader):
    model.eval()
    y_true = []
    y_pred = []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)
            y_true.extend(y_batch.numpy())
            y_pred.extend(outputs.numpy())

    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"Mean Squared Error: {mse:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"R² Score: {r2:.4f}")

    return y_true, y_pred

# Evaluate the model
y_true, y_pred = evaluate_model(model, test_loader)

# Save the entire model
os.makedirs("saved_models", exist_ok=True)
torch.save({
    'model_state_dict': model.state_dict(),
    'preprocessor': preprocessor,
    'input_size': n_features
}, 'saved_models/watch_price_predictor.pth')

print("Model saved to saved_models/watch_price_predictor.pth")

