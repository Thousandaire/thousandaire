"""
Call crawlers to get up-to-date data and save them to files.
"""

import importlib
import os
import pickle
from thousandaire.constants import DATA_DIR, DATA_LIST_ALL
from thousandaire.data_loader import DataLoader

def call_crawlers(dataset_list):
    """
    Call crawlers to get latest data.
    """
    for dataset_name in dataset_list:
        crawler_module = importlib.import_module(
            'thousandaire.crawlers.%s' % dataset_name)
        crawler = crawler_module.Crawler(dataset_name)
        cur_data = DataLoader([dataset_name]).get_all()[dataset_name]
        last_date, new_data = crawler.update()
        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)
        data_path = os.path.join(DATA_DIR, dataset_name)
        with open(data_path, 'wb') as file:
            for key in new_data:
                if key in cur_data.keys():
                    cur_data[key].extend(new_data[key])
                else:
                    cur_data[key] = new_data[key]
            pickle.dump(cur_data, file)
        crawler.set_last_modified_date(last_date)

if __name__ == '__main__':
    call_crawlers(DATA_LIST_ALL)
