"""
Prototype of Crawler objects.
"""

import os
import pickle

class BaseCrawler:
    """
    This is prototype for all Crawler objects.
    """
    def __init__(self, dataset_name):
        """
        TO-BE-INCLUDED!
        Please call this before your own initialization.
        Initialize `self.dataset_name` as `dataset_name`.
        """
        self.dataset_name = dataset_name

    def get_last_modified_date(self):
        """
        Return the last modified date of the dataset.
        """
        timestamp_file = self.dataset_name + '_timestamp_file.pkl'
        if os.path.isfile(timestamp_file):
            with open(timestamp_file, 'rb') as file:
                return pickle.load(file)
        return {}

    def set_last_modified_date(self, date_dict):
        """
        Set the last modified date of the dataset to the given dict of dates.
        """
        timestamp_file = self.dataset_name + '_timestamp_file.pkl'
        with open(timestamp_file, 'wb') as file:
            pickle.dump(date_dict, file)

    def update(self):
        """
        TO-BE-OVERLOAD!
        This should return 2 values:
          1. The new last modified date -- usually the last date of new data.
          2. All new data generated after the last modified date.
        """
