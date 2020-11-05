"""
Unit tests for data classes

Implemented:
    Data

TODO:
    DataController
    Dataset
    Portfolio
"""

import unittest
from datetime import datetime
from thousandaire.data_classes import Data

class TestData(unittest.TestCase):
    """
    Unit test object for Data.
    """
    def setUp(self):
        self.data = Data('test', ['buy', 'sell'])
        self.data_list = [
            [(datetime(2020, 1, 27), 27, 27), (datetime(2020, 1, 28), 28, 28)],
            [(datetime(2020, 1, 29), 29, 29), (datetime(2020, 1, 30), 30, 30)]]

    def assert_eqaul_content(self, response, answer):
        """
        Check whether the response from object is equal to the answer.
        """
        self.assertEqual(
            [item.date for item in response], [item[0] for item in answer])
        self.assertEqual(
            [item.buy for item in response], [item[1] for item in answer])
        self.assertEqual(
            [item.sell for item in response], [item[2] for item in answer])

    def test_fields(self):
        """
        Test fields in Data.
        """
        self.assertEqual(self.data.fields, ['date', 'buy', 'sell'])

    def test_append(self):
        """
        Test append method in Data.
        """
        # Normal append to a empty Data.
        self.data.append(self.data_list[0][0])
        self.assert_eqaul_content([self.data[0]], [self.data_list[0][0]])
        # Normal append to a not empty Data.
        self.data.append(self.data_list[0][1])
        self.assert_eqaul_content([self.data[1]], [self.data_list[0][1]])
        # Invalid append.
        self.assertRaises(TypeError, self.data.append, 1)
        self.assertRaises(TypeError, self.data.append, (3, 5))
        self.assertRaises(TypeError, self.data.append, (3, 5, 7, 9))
        self.assertRaises(TypeError, self.data.append, *self.data_list[0][0])

    def test_extend(self):
        """
        Test extend method in Data.
        """
        # Normal extend to a empty Data.
        self.data.extend(self.data_list[0])
        self.assert_eqaul_content(self.data, self.data_list[0])
        # Extend to a not empty Data.
        self.data.extend(self.data_list[1])
        self.assert_eqaul_content(
            self.data, self.data_list[0] + self.data_list[1])
        # Invalid extend
        self.assertRaises(TypeError, self.data.extend, 1)
        self.assertRaises(TypeError, self.data.extend, [(3, 5), (2, 4)])
        self.assertRaises(
            TypeError, self.data.extend, [(3, 5, 7, 9), (2, 4, 6, 8)])
        self.assertRaises(TypeError, self.data.extend, *self.data_list[0])

if __name__ == '__main__':
    unittest.main()
