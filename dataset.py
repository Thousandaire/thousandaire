"""
Adjust data into the format we want.
"""

import collections

class Dataset(list):
    """
    Change the data into the reservation mode.
    """
    def __new__(cls, name, fields):
        self = super(Dataset, Dataset).__new__(Dataset)
        self.name = name
        self.fields = ['date'] + fields
        self.data_type = collections.namedtuple(name, self.fields)
        return self

    def __init__(self, name, fields):
        pass

    def __reduce_ex__(self, proto):
        return (
            self.__new__,
            (Dataset, self.name, self.fields[1:]),
            None,
            map(tuple, self),
            None
        )

    def materialize(self, x):
        """
        Build data into namedtuple
        """
        return self.data_type(*x)

    def append(self, x):
        list.append(self, self.materialize(x))

    def extend(self, iterable):
        list.extend(self, list(map(self.materialize, iterable)))
