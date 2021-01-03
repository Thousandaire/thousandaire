"""
Simulator that simulates trading process and estimates profits and losses.
"""

import uuid
from thousandaire.data_classes import Data
from thousandaire.constants import TRADING_INSTRUMENTS

class Simulator:
    """
    Handler to simulate a single alpha.
    """
    def __init__(self, settings, data, pnl_function):
        self.pnl_function = pnl_function
        self.data = data
        self.settings = settings
        self.__result = Data(
            'result', ['pnl', 'cost', 'position_raw', 'position_np'])
        self.__portfolio = list()
        self.__key = uuid.uuid4()
        self.initialize_data()

    def generate_pnl(self, date, end_date):
        """
        Calculate pnl for alphas.
        This method will be called day by day while inputting new portfolios.

        pnl and cost will return by user-specified pnl_function.
        """
        liquidation = False
        if date == end_date:
            liquidation = True
        pnl, cost = self.pnl_function(
            self.__portfolio, self.data['price'], liquidation)
        self.__result.append(
            (date, pnl, cost, self.__portfolio[-1],
             self.__portfolio[-1].encode_to_nparray(self.settings.target)))

    def move_forward(self):
        """
        Move the simulating date.
        """
        for dataset in self.data['others'].values():
            dataset.move_forward(self.__key)
        self.data['price'].move_forward(self.__key)
        self.data['workdays'].move_forward(auth_key=self.__key)

    def run(self):
        """
        Start the simulation.
        """
        alpha_formula = self.settings.alpha(
            self.settings.start_date, self.data['others'],
            self.settings.parameters)
        while self.data['workdays'].get_today() < self.settings.end_date:
            portfolio = alpha_formula(
                self.data['workdays'].get_today(), self.data['others'])
            try:
                portfolio.normalize()
            except ZeroDivisionError as error:
                raise ("Zero position on %s"
                       % self.data['workdays'].get_today()) from error
            if not portfolio.is_tradable(
                    TRADING_INSTRUMENTS[self.settings.target]):
                raise KeyError("Some instruments on %s are not tradable."
                               % self.data['workdays'].get_today())
            self.__portfolio.append(portfolio)
            self.move_forward()
            self.generate_pnl(
                self.data['workdays'].get_today(), self.settings.end_date)
        return self.__result

    def initialize_data(self):
        """
        Initialize the data before the simulation, including:

        (1) Set keys for all datasets.
        (2) Set states of all datasets to be on start_date.
        """
        self.data['workdays'].set_key(self.__key)
        self.data['workdays'].set_date(
            self.settings.start_date, auth_key=self.__key)
        self.data['price'].set_key(self.__key)
        self.data['price'].set_date(self.settings.start_date, self.__key)
        for dataset in self.data['others'].values():
            dataset.set_key(self.__key)
            dataset.set_date(self.settings.start_date, self.__key)
