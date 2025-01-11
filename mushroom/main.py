import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class MushroomUtils:
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)

    def get_labeled_data(self):
        """
        Labels the data using LabelEncoder, useful for tree-based models
        """
        label_encoder = LabelEncoder()
        labeled_data = self.data.copy()
        for column in labeled_data.columns:
            labeled_data[column] = label_encoder.fit_transform(labeled_data[column])
        return labeled_data



if __name__ == "__main__":
    processor = MushroomUtils('./resources/mushrooms.csv')
    processed_data = processor.get_labeled_data()
    print(processed_data.head())
