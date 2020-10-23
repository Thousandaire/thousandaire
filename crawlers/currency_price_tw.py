"""
Get currency price
"""

from datetime import datetime
import xml.etree.ElementTree as ET
import requests
from thousandaire.crawler import BaseCrawler
from thousandaire.dataset import Data, Dataset

class Crawler(BaseCrawler):
    """
    Crawling new data and update.
    """
    def __init__(self, dataset_name):
        BaseCrawler.__init__(self, dataset_name)
        #instrument will read from file in the future
        self.base = 'TWD'
        self.instruments = [
            'USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY',
            'HKD', 'NZD', 'SEK', 'SGD', 'MXN', 'ZAR', 'THB', 'TWD']
        self.url = 'https://historical.findrate.tw/his.php?c='
        last_modified_date = self.get_last_modified_date()
        self.last_modified_date = {
            instrument: last_modified_date.get(instrument)
            for instrument in self.instruments}

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
                if date == self.last_modified_date[instrument]:
                    synchronized = True
                    break
                buy = float(grids[3].text)
                sell = float(grids[4].text)
                # Data come from BANK OF TAIWAN, which offers discount for
                # online trading.
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
            self.last_modified_date[instrument] = history[0].date
            history.reverse()
        return history

    def fill_data(self, instrument, data):
        """
        Manually fill data of base instrument.
        """
        reference_currency = 'USD'
        history = Data(instrument, ['buy', 'sell'])
        for datum in data[reference_currency]:
            history.append((datum.date, float(1), float(1)))
        if len(history) > 0:
            self.last_modified_date[instrument] = history[-1].date
        return history

    def update(self):
        """
        Get the historical instrument data
        """
        return_data = {}
        for instrument in self.instruments:
            return_data[instrument] = (
                self.crawl_data(instrument)
                if instrument != self.base
                else self.fill_data(instrument, return_data))
        return self.last_modified_date, Dataset(self.dataset_name, return_data)
