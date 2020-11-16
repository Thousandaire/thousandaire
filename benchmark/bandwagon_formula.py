"""
Bandwagon alpha formula.

Idea:
    We believe the 'wind' on the market.
    The wind blows when the instrument rises/falls for consecutive x days,
    and accumulated change rate is more than y.
    We follow wind of instruments and positions are proportional to their
    accumulated change rate (in the window).
"""

from thousandaire.alpha import BaseAlphaFormula
from thousandaire.data_classes import Portfolio

def catch_wind(data):
    """
    Do you feel the wind?

    This function is used to check whether the price has rised/fallen
    in consecutive x days.
    """
    return (all([data[x].buy < data[x + 1].buy
                 for x in range(-len(data), -1, 1)]) or
            all([data[x].buy > data[x + 1].buy
                 for x in range(-len(data), -1, 1)]))

class BandWagonFormula(BaseAlphaFormula):
    """
    Formula for bandwagon.
    """
    def __init__(self, _startdate, dataset, parameters):
        BaseAlphaFormula.__init__(self, _startdate, dataset, parameters)
        self.rate = parameters['rate']
        self.window = parameters['window']

    def generate(self, _date, dataset):
        """
        Generate portfolio for the given date.

        When the instrument had rised/fallen in consecutive x days,
        I will put as same position as the rate it had rised/fallen.
        """
        portfolio = Portfolio()
        used_dataset = dataset['currency_price_tw']
        for instrument, price_data in used_dataset.items():
            if all([item.buy for item in price_data[-self.window - 1::]]):
                rate = ((price_data[-1].buy - price_data[-self.window - 1].buy)
                        / price_data[-self.window - 1].buy)
                if (catch_wind(price_data[-self.window - 1: : 1])
                        and abs(rate) >= self.rate):
                    portfolio[instrument] = rate
        return portfolio
