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
        cur_data = DataLoader([data_name]).get_raw_data()[data_name]
        new_data = crawler.update()
        with open(data_name, 'wb') as file:
            for key in new_data:
                if key in cur_data.keys():
                    cur_data[key].extend(new_data[key])
                else:
                    cur_data[key] = new_data[key]
            pickle.dump(cur_data, file)
        crawler.set_renew_date()
