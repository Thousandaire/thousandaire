"""
Get currency price
"""

import xml.etree.ElementTree as ET
import pickle
import os
from datetime import datetime
import requests
from dataset import Data, Dataset

class Crawler():
    """
    Crawling new data and update.
    """
    def __init__(self, data_name):
        #instrument will read from file in the future
        self.instruments = ['USD', 'JPY', 'AUD', 'SEK', 'NZD', 'EUR', 'ZAR', 'GBP']
        self.data_name = data_name
        self.url = 'https://historical.findrate.tw/his.php?c='
        timestamp_file = data_name + '_timestamp_file.pkl'
        if os.path.isfile(timestamp_file):
            with open(timestamp_file, 'rb') as file:
                renew_date = pickle.load(file)
        else:
            renew_date = {}
        self.renew_date = {
            instrument: renew_date.get(instrument) for instrument in self.instruments}

    def get_table(self, target):
        """
        locate the place of 'table'
        """
        response = requests.get(self.url + target)
        text = response.content.decode('utf-8')
        start = text.find('<table')
        end = text.find('</table>') + len('</table>')
        return text[start : end]

    def crawl_data(self, instrument):
        """
        Crawl target data.
        """
        history = Data(instrument, ['buy', 'sell'])
        counter = 1
        synchronized = False
        while not synchronized:
            table = self.get_table('%s&page=%d' % (instrument, counter))
            tree = ET.fromstring(table)
            rows = list(tree[0][1:])
            if not rows:
                break
            for row in rows:
                grids = list(row) 
                date = datetime.strptime(grids[0][0].text, '%Y-%m-%d')
                if date == self.renew_date[instrument]:
                    synchronized = True
                    break
                buy = float(grids[3].text)
                sell = float(grids[4].text)
                #Data came from BANK OF TAIWAN.
                #It gave some discount for Internet-trading.
                if instrument == 'USD':
                    buy_discount = 0.03
                    sell_discount = -0.03
                else:
                    buy_discount = buy * 0.001
                    sell_discount = -sell * 0.001
                buy += buy_discount
                sell += sell_discount
                history.append((date, buy, sell))
            counter += 1
        if len(history) > 0:
            self.renew_date[instrument] = history[0].date
            history.reverse()
        return history

    def set_renew_date(self):
        """
        To reset the renew_date for all instruments
        """
        data_name = self.data_name + '_timestamp_file.pkl'
        with open(data_name, 'wb') as file:
            pickle.dump(self.renew_date, file)

    def update(self):
        """
        Get the historical instrument data
        """
        return_data = {}
        for instrument in self.instruments:
            return_data[instrument] = self.crawl_data(instrument)
        return Dataset(self.data_name, return_data)
