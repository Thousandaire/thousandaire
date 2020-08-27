"""
Allocation of the asset.
"""

class Portfolio(dict):
    """
    Set the portfolio
    """
    def __init__(self, date):
        dict.__init__(self)
        self.date = date

    def normalize(self):
        """
        Normalize positions to make sure the summation of absolute values is 1.
        The simulator will call this method.
        """
        position_sum = sum(map(abs, self.values()))
        if position_sum == float(0):
            raise ValueError("zero position on %s" % (self.date))
        for instrument in self.keys():
            self[instrument] = self[instrument] / position_sum
