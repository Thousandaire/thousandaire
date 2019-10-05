"""
Get the latest data and save them to file.
"""

import pickle
import importlib
from data_loader import DataLoader

def call_crawler(data_list):
    """
    Call the crawlers we need to get new data
    """
    for data_name in data_list:
        crawler_module = importlib.import_module(data_name)
        crawler = crawler_module.Crawler(data_name)
        old_data = DataLoader([data_name]).get_raw_data()
        new_data = crawler.update()
        with open(data_name, 'wb') as file:
            for key in new_data:
                if key in old_data[data_name].keys():
                    new_data[key] = old_data[data_name][key] + new_data[key]
            pickle.dump(new_data, file)
        crawler.set_renew_date()
