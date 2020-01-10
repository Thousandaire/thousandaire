"""
Set workdays in different regions
Refer to trading day of currency
"""

import os
import pickle
from dataset import Dataset
from data_loader import DataLoader

class Crawler():
    """
    Set the newest workday and update
    """
    def __init__(self, data_name):
        #regions will read from file in the future
        self.regions = ['tw']
        self.data_name = data_name
        timestamp_file = data_name + '_timestamp_file.pkl'
        if os.path.isfile(timestamp_file):
            with open(timestamp_file, 'rb') as file:
                renew_date = pickle.load(file)
        else:
            renew_date = {}
        self.renew_date = {
            region: renew_date.get(region) for region in self.regions}

    def set_renew_date(self):
        """
        Reset the renew_date for all regions
        """
        file_name = self.data_name + '_timestamp_file.pkl'
        with open(file_name, 'wb') as file:
            pickle.dump(self.renew_date, file)

    def set_workdays(self, region):
        """
        Set workdays in the region
        """
        data_name = 'currency_price_' + region
        reference_data = DataLoader([data_name]).get_raw_data()
        #We set workdays from the trading day which the region's currency trade with USD,
        #because USD is the strongest currency.
        #When region is US, we use JPY instead.
        reference_currency = 'USD' if region != 'us' else 'JPY'
        return_data = Dataset('workdays', [])
        for value in reference_data[data_name][reference_currency][::-1]:
            if value.date == self.renew_date[region]:
                break
            return_data.append((value.date))
        self.renew_date[region] = return_data[0].date
        return_data.reverse()
        return return_data

    def update(self):
        """
        Get the workdays in every region
        """
        return_data = {}
        for region in self.regions:
            return_data[region] = self.set_workdays(region)
        return return_data
