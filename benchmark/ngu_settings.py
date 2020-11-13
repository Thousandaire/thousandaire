"""
Settings for NEVER GIVE UP alpha.

Idea:
    The more the instruments fell, the more we buy.
    This idea came from a gambling strategy:
    I bet ＄1 on the first game, but I lost. Then, I would bet ＄2
    on the second game.
    If I lose again, I would raise to ＄4 on the third game, and so on.
    In this strategy, I could win money when I win only one game.
"""

import datetime
from thousandaire.alpha import BaseAlphaSettings
from thousandaire.benchmark.ngu_formula import NGUFormula

class AlphaSettings(BaseAlphaSettings):
    """
    Settings for NGU.
    """
    author = 'Black'
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 9, 10)
    alpha = NGUFormula
    target = ('currency', 'TW')
    data_list = ['currency_price_tw']
    parameters = {'multiplier': 2, 'days': 10}
