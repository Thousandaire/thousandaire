"""
Global constants shared by the whole package.
"""

import os
import thousandaire.pnl_calculation

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, 'data')
DATA_LIST_ALL = ['currency_price_tw', 'workdays']
EVAL_URL = 'http://127.0.0.1:5000/'
TRADING_INSTRUMENTS = {
    ('currency', 'TW'):
        ('USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF',
         'CNY', 'HKD', 'NZD', 'SEK', 'SGD', 'MXN', 'ZAR', 'THB', 'TWD')
}
OFFICIAL_CURRENCY = {
    'TW' : 'TWD', 'US' : 'USD', 'JAP' : 'JPY', 'UK' : 'GBP'}
TRADING_CONFIGS = {
    ('currency', 'TW'): {
        'price_dataset': 'currency_price_tw',
        'pnl_function': thousandaire.pnl_calculation.CurrencyPnl}
}
TRADING_REGIONS = ['TW']
TIMESTAMP_FILE_SUFFIX = '_timestamp_file.pkl'
