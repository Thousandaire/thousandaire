"""
Global constants shared by the whole package.
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OFFICIAL_CURRENCY = {
    'TW' : 'TWD', 'US' : 'USD', 'JAP' : 'JPY', 'UK' : 'GBP'}
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DATA_LIST_ALL = ['currency_price_tw', 'workdays']
TIMESTAMP_FILE_SUFFIX = '_timestamp_file.pkl'
