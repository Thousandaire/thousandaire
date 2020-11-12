"""
Adjust data into the format we want.
"""

import collections
import numpy as np
from thousandaire.constants import TRADING_INSTRUMENTS

def protect(func):
    """
    This is a decorator which checks permission before calling the method.
    To get permission, the caller must pass the correct `auth_key`.
    """
    def wrapper(self, *args, **kargs):
        key = kargs.pop('auth_key', None)
        if not self.authorize(key):
            raise IOError('Permission denied.')
        return func(self, *args, **kargs)
    return wrapper

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

    def __init__(self, *_):
        super().__init__(self)

    def __reduce_ex__(self, proto):
        return (
            self.__new__,
            (Data, self.name, self.fields[1:]),
            None,
            map(tuple, self),
            None
        )

    def append(self, element):
        list.append(self, self.materialize(element))

    def extend(self, iterable):
        list.extend(self, list(map(self.materialize, iterable)))

    def materialize(self, element):
        """
        Convert data (in tuple) into namedtuple.
        """
        return self.data_type(*element)

class DataIterator():
    """
    Iterator of DataController.
    """
    def __init__(self, data_controller):
        self.__data_controller = data_controller
        self.__index = -1

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index + 1 < len(self.__data_controller):
            self.__index += 1
            return self.__data_controller[
                self.__index - len(self.__data_controller)]
        raise StopIteration

class DataController():
    """
    Control the data privacy.
    """
    def __init__(self, data, key=None):
        self.name = data.name
        self.__data = data
        self.__end = len(self.__data)
        self.__key = key
        self.__workdays = None
        # empty_row and fields other than `date` are used in many methods,
        # so we cache them to improve performance.
        self.__empty_row = (
            tuple(None for i in range(0, len(data.fields) - 1))
            if data is not None else None
        )
        self.__fields = (
            list(name for name in data.fields if name != 'date')
            if data is not None else None
        )

    def __getitem__(self, index):
        """
        Use self.__end to control the data privacy.

        In the back-test system, we assume that the current simulating day is
        index 0. Since users should get only data before the current day, the
        method should accept only negative numbers.

        If getting non-negative numbers, an IndexError will be raised.
        Otherwise, we have 2 cases:
            (1) We get a negative number:
                We use self.__end and the number we get to produce a new index
                to meet the assumption above. Then, we return
                `self.__data[index]` to the users.
                When users require some data earlier than our raw data,
                    (a) if the data were not earlier than workdays data:
                        return an Data object with "None" data.
                    (b) if the data were earlier than workdays data:
                        raise an IndexError.
            (2) We get a slice:
                We reset the start index and stop index according to our
                assumption, and return a newly generated DataController.
        """
        if isinstance(index, slice):
            if index.step == 0:
                raise IndexError("slice step cannot be zero")
            start = index.start
            stop = index.stop
            step = 1 if index.step is None else index.step
            if start is None:
                start = -self.__end if step > 0 else -1
            if stop is None:
                stop = 0 if step > 0 else -self.__end - 1
            if start >= 0 or stop > 0:
                raise IndexError("list index out of range")
            return_data = Data(self.__data.name, self.__fields)
            return_data.extend([
                self[x] for x in range(start, stop, step)
                if self[x] is not None])
            return DataController(
                return_data,
                self.__key
            )
        if index >= 0:
            raise IndexError("list index out of range")
        if self.__end + index < 0:
            if len(self.__workdays) + index >= 0:
                return_datum = Data(self.__data.name, self.__fields)
                return_datum.append(
                    (self.__workdays[index].date, self.__empty_row))
                return return_datum
            raise IndexError("list index out of range")
        return self.__data[self.__end + index]

    def __iter__(self):
        return DataIterator(self)

    def __len__(self):
        return self.__end

    def __str__(self):
        return str(self.__data[: self.__end])

    def authorize(self, key):
        """
        Check if the key is correct to authorize the key holder to access
        the data.
        """
        return key == self.__key

    @protect
    def extend(self, extend_object):
        """
        Similar to list.extend.
        """
        if (isinstance(extend_object, DataController)
                and self.name == extend_object.name):
            self.__data.extend(extend_object)
            self.__end = len(self.__data)
        else:
            raise TypeError("Data in a dataset must be the same types.")

    def get_today(self):
        """
        Return the date of the current simulating day.

        When self.__end == len(self.__data), it means we are generating the
        portfolio for the next real-life trading day.
        None will be returned as the next workday is still unknown.
        """
        if self.__end == len(self.__data):
            return None
        return self.__data[self.__end].date

    @protect
    def move_forward(self):
        """
        Move to next workday.

        2 thing to be concerned:
            (1) When self.__end == len(self.__data), it means we do not have
                the next date. Thus, we raise a ValueError when users still
                call this method.
            (2) The self.__data may not be as old as workdays data, so we
                should check it to know we should move self.__end.
        """
        if self.__end == len(self.__data):
            raise ValueError("Date not found.")
        if (self.__end == 0
                and self.__data[0].date != self.__workdays.get_today()):
            return
        self.__end += 1

    @protect
    def set_date(self, target_date):
        """
        Set the DataController to the state of target_date.

        2 things to be concerned:
            (1) When the target date is latter than the latest data we have,
                raise a ValueError.
            (2) When the target date is earlier than the earliest data we have,
                just keep the index at the earliest data we have.
        """
        if self.__data[-1].date < target_date:
            raise ValueError("Date not found.")
        left = -len(self.__data)
        right = 0
        while left < right - 1:
            mid = (left + right) // 2
            if self.__data[mid].date > target_date:
                right = mid
            else:
                left = mid
        self.__end = len(self.__data) + left

    def set_key(self, key):
        """
        Set key for permission control.
        """
        if self.__key is not None:
            raise IOError("Permission denied: the key is unchangeable.")
        self.__key = key

    @protect
    def set_workdays(self, workdays):
        """
        Synchronize all data with workdays.
        Will be called by the Dataset.

        We have raw data, workdays data and synchronized data in this method.
        Synchronized data will contain only dates of workdays data.
        However, if the date is earlier than our raw data,
        synchronized data will not keep it.

        For example, among 10/01~10/07:
        If workdays are
            10/01, 10/02, 10/04, 10/05, 10/06.
        The raw data has values on
            10/03, 10/05 and 10/06
            (with data value1003, value1005, value1006 respectively).
        The synchronized data will be
            (10/04, None-vector), (10/05, value1005), (10/06, value1006).
        Synchronized data will not keep any data before 10/03.

        To match the criterion above, 3 things should be concerned:
            (1) The start date of the synchronized data will be
                (a) the first date of raw data, if it is a workday; otherwise,
                (b) the first workday after the first date in raw data,
            (2) If raw data is not available on some date in workdays, data of
                the date will be set to None-vector in synchronized data.
            (3) Dates not in workdays will not be in the synchronized data
                regardless of their existence in raw data.
        """
        self.__workdays = workdays
        data_index = -len(self.__data)
        workdays_index = -len(workdays)
        sync_data = Data(self.__data.name, self.__fields)
        while workdays_index < 0 and data_index < 0:
            if self.__data[data_index].date > workdays[workdays_index].date:
                if data_index != -len(self.__data):
                    sync_data.append(
                        (workdays[workdays_index].date, *self.__empty_row))
                workdays_index += 1
            elif self.__data[data_index].date < workdays[workdays_index].date:
                data_index += 1
            else:
                sync_data.append(self.__data[data_index])
                workdays_index += 1
                data_index += 1
        remaining_data = [
            (workdays[x].date, *self.__empty_row)
            for x in range(workdays_index, 0)]
        sync_data.extend(remaining_data)
        self.__data = sync_data
        self.__end = len(self.__data)

class Dataset(dict):
    """
    Merge all data into one set.
    This will be called in the simulator.
    """
    def __init__(self, data_name, data):
        dict.__init__(self)
        for instrument, values in data.items():
            self[instrument] = DataController(values)
        self.data_name = data_name

    def move_forward(self, key=None):
        """
        Move to next workday.
        """
        for instrument in self:
            self[instrument].move_forward(auth_key=key)

    def set_date(self, target, key=None):
        """
        Set the current date to the given date.
        """
        for instrument in self:
            self[instrument].set_date(target, auth_key=key)

    def set_key(self, key):
        """
        Set key for permission control.
        """
        for instrument in self:
            self[instrument].set_key(key)

    def set_workdays(self, workdays, key=None):
        """
        Synchronize all data with workdays.
        Should be called only by the simulator.
        """
        for instrument in self:
            self[instrument].set_workdays(workdays, auth_key=key)

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
