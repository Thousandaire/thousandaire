"""
Call crawlers to get up-to-date data and save them to files.
"""

import importlib
import pickle
from data_loader import DataLoader

def call_crawler(dataset_list):
    """
    Call crawlers to get latest data.
    """
    for dataset_name in dataset_list:
        crawler_module = importlib.import_module(dataset_name)
        crawler = crawler_module.Crawler(dataset_name)
        cur_data = DataLoader([dataset_name]).get_all()[dataset_name]
        last_date, new_data = crawler.update()
        with open(dataset_name, 'wb') as file:
            for key in new_data:
                if key in cur_data.keys():
                    cur_data[key].extend(new_data[key])
                else:
                    cur_data[key] = new_data[key]
            pickle.dump(cur_data, file)
        crawler.set_last_modified_date(last_date)

if __name__ == '__main__':
    dataset_list_all = ['currency_price_tw', 'workdays']
    call_crawler(dataset_list_all)
