"""
Draw lots alpha formula.

Idea:
    All we believe is God.
    Let God determine our position.
"""

from random import randint
from thousandaire.alpha import BaseAlphaFormula
from thousandaire.data_classes import Portfolio

class DrawLotsFormula(BaseAlphaFormula):
    """
    Formula for draw lots.
    """
    def __init__(self, _startdate, dataset, parameters):
        BaseAlphaFormula.__init__(self, _startdate, dataset, parameters)
        self.trading_instruments = ['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'SEK']

    def generate(self, _date, _dataset):
        """
        Generate portfolio for the given date.
        """
        portfolio = Portfolio()
        for instrument in self.trading_instruments:
            portfolio[instrument] = randint(-100, 100)
        return portfolio
