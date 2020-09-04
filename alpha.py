"""
Prototypes of alpha objects.
"""

import datetime

class BaseAlphaFormula:
    """
    Prototype of alpha formulas.

    All alpha formulas should inherit this and implement generate method.
    """
    def __init__(self, _date, _data, _parameters):
        self.__last_success_date = None

    def __call__(self, date, data):
        portfolio = self.generate(date, data)
        self.__last_success_date = date
        return portfolio

    def get_last_success_date(self):
        """
        Return the last success date of simulation.

        This method is for prod since it is possible that an alpha can not
        generate portfolio for several days due to lack of data or whatever.
        """
        return self.__last_success_date

class BaseAlphaSettings:
    """
    Prototype of alpha settings.

    All alpha settings should inherit this and re-define variables.
    """
    # required variables
    author = None
    start_date = None
    alpha = None
    target = None
    data_list = None

    # optional variables
    end_date = datetime.date.today()
    parameters = {}
    submission_id = None
    submission_date = None

    def is_valid(self):
        """
        Currently check only types of required variables.
        It is possible that values are invalid.

        TODO: implement value checks.
        """
        expected = {
            type(self.author): str,
            type(self.start_date): datetime.date,
            type(self.end_date): datetime.date,
            self.alpha: BaseAlphaFormula,
            type(self.target): tuple,
            type(self.data_list): list,
            type(self.parameters): dict
        }
        return all(issubclass(variable, expected_type)
                   for variable, expected_type in expected.items())

    def set_submission_info(self, submission_id, submission_date):
        """
        Set submission information of the alpha.

        This method is for prod since we will register the alpha settings
        in our alpha pool.
        """
        self.submission_id = submission_id
        self.submission_date = submission_date
