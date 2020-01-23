"""
Adjust data into the format we want.
"""

import collections

class Data(list):
    """
    Change the data into the reservation mode.
    """
    def __new__(cls, name, fields):
        self = super(Data, Data).__new__(Data)
        self.name = name
        self.fields = ['date'] + fields
        self.data_type = collections.namedtuple(name, self.fields)
        return self

    def __init__(self, name, fields):
        pass

    def __reduce_ex__(self, proto):
        return (
            self.__new__,
            (Data, self.name, self.fields[1:]),
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

class Dataset(dict):
    """
    Merge all data into one set.
    This will be called in the simulator.
    """
    def __init__(self, data_name, data):
        dict.__init__(self, data)
        self.data_name = data_name
