"""
Settings for draw lots alpha.

Idea:
    All we believe is God.
    Let God determine our position.
"""

import datetime
from thousandaire.alpha import BaseAlphaSettings
from thousandaire.benchmark.draw_lots_formula import DrawLotsFormula

class AlphaSettings(BaseAlphaSettings):
    """
    Settings for draw lots.
    """
    author = 'Black'
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 9, 10)
    alpha = DrawLotsFormula
    target = ('currency', 'TW')
    data_list = ['currency_price_tw']
