"""
NGU alpha formula.

Idea:
    The more the instruments fell, the more we buy.
    This idea came from a gambling strategy:
    I bet ＄1 on the first game, but I lost. Then, I would bet ＄2
    on the second game.
    If I lose again, I would raise to ＄4 on the third game, and so on.
    In this strategy, I could win money when I win only one game.
"""

from thousandaire.alpha import BaseAlphaFormula
from thousandaire.data_classes import Portfolio

def make_list(multi, days):
    """
    Make position list.
    The formula will use this list to keep the last position
    I put in each instruments.
    """
    position = [0, 1]
    count = days
    while count > 0:
        position.append(position[-1] * multi)
        count -= 1
    return_list = list(map(lambda var: -var, position[::-1]))
    return_list.extend(position[1:])
    return return_list

class NGUFormula(BaseAlphaFormula):
    """
    Formula for NGU.
    """
    def __init__(self, _startdate, dataset, parameters):
        BaseAlphaFormula.__init__(self, _startdate, dataset, parameters)
        self.trading_instruments = ['USD', 'EUR', 'JPY', 'GBP', 'CAD']
        self.position = make_list(parameters['multiplier'], parameters['days'])
        self.index = {
            instrument: int(len(self.position) / 2)
            for instrument in self.trading_instruments}

    def generate(self, _date, dataset):
        """
        Generate portfolio for the given date.

        At first, the position will be 0.
        When the price fall, which means I lose money, I would buy more.
        Thus, I should plus 1 to the index, which used in position list,
        to increase the position.
        """
        portfolio = Portfolio()
        used_dataset = dataset['currency_price_tw']
        for instrument in self.trading_instruments:
            today = used_dataset[instrument][-1].buy
            yesterday = used_dataset[instrument][-2].buy
            if today > yesterday:
                self.index[instrument] = max(
                    self.index[instrument] - 1, 0)
            elif today < yesterday:
                self.index[instrument] = min(
                    self.index[instrument] + 1, len(self.position) - 1)
            portfolio[instrument] = self.position[self.index[instrument]]
        return portfolio
