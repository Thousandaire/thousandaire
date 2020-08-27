"""
A template of alpha settings.
"""

import datetime
from thousandaire.alpha import BaseAlphaSettings
from thousandaire.template.alpha_formula import AlphaFormula

class AlphaSettings(BaseAlphaSettings):
    """
    Inherit BaseAlphaSettings and assign values at least for required fields.
    """
    # author name (str)
    author = 'Bruce'
    # start date of simulation (datetime.date)
    start_date = datetime.datetime(2012, 1, 1)
    # end date of simulation (datetime.date)
    # optional, default value: datetime.date.today()
    end_date = datetime.datetime(2018, 12, 31)
    # alpha function (any classes inheriting BaseAlphaFormula)
    alpha = AlphaFormula
    # trading target, including type and region (tuple(str, str))
    target = ('currency', 'TW')
    # data used in the alpha (list(str))
    data_list = ['currency_price_tw']
    # parameters in alpha (dict)
    # optional, default value: {}
    parameters = {'k': 5}
