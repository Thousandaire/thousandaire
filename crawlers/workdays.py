"""
Set workdays in different regions
Refer to trading day of currency
"""

from thousandaire.constants import OFFICIAL_CURRENCY
from thousandaire.crawler import BaseCrawler
from thousandaire.data_classes import Data, Dataset
from thousandaire.data_loader import DataLoader

class Crawler(BaseCrawler):
    """
    Set the newest workday and update
    """
    def __init__(self, dataset_name):
        BaseCrawler.__init__(self, dataset_name)
        # regions will be read from file in the future
        self.regions = ['TW']
        last_modified_date = self.get_last_modified_date()
        self.last_modified_date = {
            region: last_modified_date.get(region) for region in self.regions}

    def set_workdays(self, region):
        """
        Set workdays in the region
        """
        dataset_name = 'currency_price_' + region.lower()
        reference_data = DataLoader([dataset_name]).get_all()
        # We set workdays as dates in USD/TWD because this is the pair with
        # the longest trade history. If region is US, we use JPY instead.
        reference_currency = OFFICIAL_CURRENCY[region]
        return_data = Data('workdays', [])
        for value in reference_data[dataset_name][reference_currency][::-1]:
            if value.date == self.last_modified_date[region]:
                break
            return_data.append((value.date,))
        if len(return_data) > 0:
            self.last_modified_date[region] = return_data[0].date
            return_data.reverse()
        return return_data

    def update(self):
        """
        Get the workdays in every region
        """
        return_data = {}
        for region in self.regions:
            return_data[region] = self.set_workdays(region)
        return self.last_modified_date, Dataset(self.dataset_name, return_data)
