"""
A template of alpha formula.
"""

from collections import deque
from thousandaire.alpha import BaseAlphaFormula
from thousandaire.portfolio import Portfolio

class AlphaFormula(BaseAlphaFormula):
    """
    Inherit BaseAlphaFormula to implement your own alpha formula class.

    DO NOT overload the following methods, or simulation may fail in prod:
            __call__, get_last_success_date
    """
    def __init__(self, _date, data, parameters):
        """
        Set up the alpha before generating any portfolios.
        If the alpha needs to warm-up before returning its first portfolio.
        """
        BaseAlphaFormula.__init__(self, _date, data, parameters)
        self.k_days = parameters['k']
        self.mid_last_k_days = {
                instrument: deque(
                        (datum.buy + datum.sell) / 2
                        for datum in price_data[-self.k_days:])
                for instrument, price_data in data['currency_price_tw'].items()
        }
        self.sum_last_k_days = {
                instrument: sum(self.mid_last_k_days[instrument])
                for instrument in data['currency_price_tw']
        }

    def generate(self, date, data):
        """
        Generate portfolio for the given date.
        The simulator guarantees to call this method in date order, and the
        first date will be "startdate" specified in AlphaSettings.
        """
        portfolio = Portfolio(date)
        for instrument, price_data in data['currency_price_tw'].items():
            # maintain mid_last_k_days and sum_last_k_days for optimization.
            new = (price_data[-1].buy + price_data[-1].sell) / 2
            old = self.mid_last_k_days[instrument].pop()
            self.mid_last_k_days[instrument].append(new)
            self.sum_last_k_days[instrument] += new - old
            portfolio[instrument] = (
                    self.sum_last_k_days[instrument] / self.k_days - new)
        return portfolio
