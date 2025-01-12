"""
After conducting the exploratory data analysis, we can now proceed
to the next step which is to build a machine learning model.
"""

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier


mushroom_data = pd.read_csv('./resources/mushrooms.csv')

# Add the gill-color + gill-size feature, reached from the EDA
mushroom_data["gill_combined"] = mushroom_data["gill-color"] + "_" + mushroom_data["gill-size"]

# Split the data into features and target
X = mushroom_data.drop(columns=["class"], axis=1)
y = mushroom_data["class"]

encoders = {}
# Encode the train and test data
y_encoder = LabelEncoder()

y = y_encoder.fit_transform(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.35, random_state=28)

# Encode the features
for col in X.columns:
    # Save the encoder, so we can use it later in the cross-validation
    encoders[col] = LabelEncoder()
    # Fit and transform the training data
    X_train[col] = encoders[col].fit_transform(X_train[col])
    # Transform the testing data
    X_test[col] = encoders[col].transform(X_test[col])

# Train the model
model = RandomForestClassifier(n_estimators=10, random_state=28, max_depth=6)
model.fit(X_train, y_train)

# Predict the target
y_pred = model.predict(X_test)

if __name__ == '__main__':
    # Evaluate the model
    score = model.score(X_test, y_test)
    print(f"Model Accuracy: {score}")
