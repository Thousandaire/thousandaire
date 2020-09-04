"""
Pnl and cost calculators.
"""

from collections import defaultdict

class CurrencyPnl:
    """
    Calculator of pnl and cost of currency trading.
    """
    def __init__(self, base_ins, instruments):
        self.base_ins = base_ins
        self.instruments = instruments
        self.last_quantity = defaultdict(float)
        self.last_price = defaultdict(float)

    def __call__(self, portfolio, price, liquidation):
        if liquidation:
            for instrument in self.instruments:
                portfolio[-1][instrument] = (
                    0 if instrument is not self.base_ins else 1)
        return self.calculate(portfolio[-1], price)

    def calculate(self, today, price):
        """
        Calculate pnl and produce cost.

        We assume that our overall investment size is always 1.
        Thus, performance of alphas is more readable because it stands for
        ratio as well.
        Please check wiki page for more details.
        """
        pnl = {instrument: 0. for instrument in self.instruments}
        cost = {instrument: 0. for instrument in self.instruments}
        for instrument in self.instruments:
            if (price[instrument][-1].buy is not None and
                    price[instrument][-1].sell is not None):
                position = today.get(instrument, 0)
                spread = ((price[instrument][-1].sell -
                           price[instrument][-1].buy) / 2)
                middle_price = price[instrument][-1].buy + spread
                quantity = position / middle_price
                difference = (
                    self.last_quantity[instrument] - quantity)
                pnl[instrument] = ((middle_price - self.last_price[instrument])
                                   * self.last_quantity[instrument])
                cost[instrument] = abs(difference * spread)
                self.last_quantity[instrument] = quantity
                self.last_price[instrument] = middle_price
        return pnl, cost
