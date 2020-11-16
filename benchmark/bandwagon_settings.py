"""
Settings for bandwagon alpha.

Idea:
    We believe the 'wind' on the market.
    The wind blows when the instrument rises/falls for consecutive x days,
    and accumulated change rate is more than y.
    We follow wind of instruments and positions are proportional to their
    accumulated change rate (in the window).
"""

import datetime
from thousandaire.alpha import BaseAlphaSettings
from thousandaire.benchmark.bandwagon_formula import BandWagonFormula

class AlphaSettings(BaseAlphaSettings):
    """
    Settings for bandwagon.
    """
    author = 'Black'
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 9, 10)
    alpha = BandWagonFormula
    target = ('currency', 'TW')
    data_list = ['currency_price_tw']
    parameters = {'window': 2, 'rate': 0.03}
