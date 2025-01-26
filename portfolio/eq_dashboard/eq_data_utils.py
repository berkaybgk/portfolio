import pandas as pd
class EqUtils:
    def __init__(self):
        self.data_path = "resources/eq_data.csv"

    def get_last_weeks_data(self):
        data = pd.read_csv(self.data_path)
        pass
