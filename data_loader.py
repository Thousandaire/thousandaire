"""
Implementation of DataLoader module.
"""

import os
import pickle
from thousandaire.constants import DATA_DIR
from thousandaire.dataset import Dataset

class DataLoader:
    """
    This object loads data from archieved files and feeds back data in Dataset
    format defined in dataset.py.
    """
    def __init__(self, data_list):
        self.data = {}
        for data_name in data_list:
            data_path = os.path.join(DATA_DIR, data_name)
            try:
                with open(data_path, "rb") as file:
                    self.data[data_name] = pickle.load(file)
            except FileNotFoundError:
                self.data[data_name] = Dataset(data_name, {})
                print("Warning: %s does not exist." % (data_name))

    def get_all(self):
        """
        Return all available data.
        """
        return self.data

    def get_update(self):
        """
        TO-DO: Update the data and return those new data.
        """
