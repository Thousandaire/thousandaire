"""
Use to give data to alpha
"""

import pickle
from dataset import Dataset

class DataLoader():
    """
    load the data which users' need
    """
    def __init__(self, data_list):
        self.data = {}
        for data_name in data_list:
            try:
                with open(data_name, "rb") as file:
                    self.data[data_name] = pickle.load(file)
            except FileNotFoundError:
                self.data[data_name] = Dataset(data_name, {})
                print("Warning: %s didn't existence" % (data_name))

    def get_raw_data(self):
        """
        return all information
        """
        return self.data
