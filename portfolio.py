"""
Allocation of the asset.
"""

import numpy as np
from thousandaire.constants import TRADING_INSTRUMENTS

class Portfolio(dict):
    """
    Set the portfolio
    """
    def __init__(self, np_array=None, encoding=None):
        dict.__init__(self)
        if np_array is not None:
            if isinstance(np_array, np.ndarray):
                self.decode_from_nparray(np_array, encoding)
            else:
                raise TypeError(
                    'The input is %s, not a numpy array.' % type(np_array))

    def decode_from_nparray(self, np_array, encoding):
        """
        Decode numpy array into portfolio.
        """
        if encoding is None:
            raise KeyError('Invalid encoding method: %r' % encoding)
        if len(np_array) != len(TRADING_INSTRUMENTS[encoding]):
            raise ValueError(
                'Input dimension does not match number of instruments.')
        for index, instrument in TRADING_INSTRUMENTS[encoding]:
            self[instrument] = np_array[index]

    def encode_to_nparray(self, encoding):
        """
        Encode the positions into numpy type.
        """
        return np.array([
            self.get(instrument, 0)
            for instrument in TRADING_INSTRUMENTS[encoding]])

    def is_tradable(self, tradable_list):
        """
        Check if all instruments of the portfolio are tradable.
        """
        return all(instrument in tradable_list for instrument in self)

    def normalize(self):
        """
        Normalize positions to make sure the summation of absolute values is 1.
        The simulator will call this method.
        """
        position_sum = sum(map(abs, self.values()))
        for instrument in self:
            self[instrument] = self[instrument] / position_sum
