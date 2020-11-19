"""
Evaluator calculates indicators for an alpha to evaluate alpha performance.
"""

from multiprocessing import Array, Process, Queue
import ctypes
import pickle
import numpy as np

COSTS = 'costs'
DATES = 'dates'
PNLS = 'pnls'
POSITIONS_RAW = 'positions_raw'
POSITIONS_NP = 'positions_np'
INDICATORS_ALL = {}
INDICATORS_DEFAULT = []

def encode_data(instruments, data):
    """
    Encode data into numpy type.

    instruments: all instruments we need here to construct 2D np.array.
        data: a Data with following fields:
            dates: a list-like objects which stores dates.
            pnls: a np.array which stores each instrument's pnl.
            costs: a np.array which stores each instrument's trading cost.
            positions_raw: a list-like of dict-like objects which map
                instruments (str) to their positions (float).
            positions_np: the np-version of positions_raw.
    """
    dates = [item.date for item in data]
    pnls = {instrument: np.array([item.pnl[instrument] for item in data])
            for instrument in instruments}
    costs = {instrument: np.array([item.cost[instrument] for item in data])
             for instrument in instruments}
    positions_raw = [item.position_raw for item in data]
    positions_np = np.array([item.position_np for item in data])
    serialized = lambda var: Array(ctypes.c_char, pickle.dumps(var), lock=False)
    return {
        COSTS: serialized(costs),
        DATES: serialized(dates),
        PNLS: serialized(pnls),
        POSITIONS_RAW: serialized(positions_raw),
        POSITIONS_NP: serialized(positions_np)}


class Evaluator:
    """
    Evaluator to run alpha evaluation indicators.
    """
    def __init__(self, indicator_names=None):
        """
        indicators: indicators to calculate.
            If indicators=None, default indicators will be calculated.
        """
        if indicator_names is None:
            self.indicators = INDICATORS_DEFAULT
        else:
            self.set_indicators(indicator_names)

    def get_indicators(self):
        """
        Return a list of current assigned indicator names.
        """
        return [indicator.__name__ for indicator in self.indicators]

    def set_indicators(self, indicator_names):
        """
        Set to-run indicators to be the given indicators.
        """
        self.indicators = []
        for indicator_name in indicator_names:
            indicator = INDICATORS_ALL.get(indicator_name)
            if indicator is None:
                raise AttributeError(
                    'Indicator not found: %s' % indicator_name)
            self.indicators.append(indicator)

    def run(self, instruments, data):
        """
        Run all specified evaluation functions and return their results.
        """
        processes = []
        results_queue = Queue()
        for indicator in self.indicators:
            process = Process(
                target=evaluate,
                args=(results_queue, indicator),
                kwargs=encode_data(instruments, data))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        results = {}
        while not results_queue.empty():
            indicator_name, result = results_queue.get()
            results[indicator_name] = result
        return results

def evaluate(results, indicator, **serialized):
    """
    Decode all shared variables into evalution function inputs, and return
    their results by results (a multiprocess.Queue).
    """
    results.put((indicator.__name__, indicator(**serialized)))

def get_all_indicators():
    """
    Return a list of all available built-in indicators.
    """
    return list(INDICATORS_ALL.keys())

def default(func):
    """
    Set func to be a default indicators.
    """
    INDICATORS_DEFAULT.append(func)
    return func

def inputs(*needed_fields):
    """
    Decorator for eval_functions to extract their inputs from encoded data.
    Only fields in needed_fields will be decoded to improve the performance.

    All and only functions decorated by this will be considered as indicators.
    They will be registered into indicator_list for lookup.
    """
    def middle(func):
        def final(**available_fileds):
            return func(*(
                pickle.loads(available_fileds[field])
                for field in needed_fields))
        final.__name__ = func.__name__
        # register the function into INDICATORS_ALL
        INDICATORS_ALL[final.__name__] = final
        return final
    return middle

@default
@inputs(PNLS)
def max_drawdown(pnls):
    """
    Maximal accumulated loss in any consecutive interval
    within the simulation period.
    If there is no drawdown at all, it will return 0.
    """
    aggregated_pnls = sum(np.array(list(pnls.values())))
    accumulated_pnls = np.add.accumulate(aggregated_pnls)
    cur_max_pnl = 0.
    drawdown = 0.
    for item in accumulated_pnls:
        drawdown = min(drawdown, item - cur_max_pnl)
        cur_max_pnl = max(item, cur_max_pnl)
    return drawdown

@default
@inputs(PNLS)
def returns(pnls):
    """
    Average annual returns
    """
    aggregated_pnls = sum(np.array(list(pnls.values())))
    return np.mean(aggregated_pnls) * 252

@default
@inputs(PNLS)
def sharpe(pnls):
    """
    Sharpe ratio
    """
    aggregated_pnls = sum(np.array(list(pnls.values())))
    return np.mean(aggregated_pnls) / np.std(aggregated_pnls)

@default
@inputs(COSTS)
def trading_costs(costs):
    """
    Average annual costs of trading
    """
    aggregated_costs = sum(np.array(list(costs.values())))
    return np.mean(aggregated_costs) * 252

@default
@inputs(POSITIONS_NP)
def turnover(positions_np):
    """
    Turnover rate
    """
    daily_tvr = abs(positions_np[1:] - positions_np[:-1]).sum(axis=1) / 2
    return {'Mean': daily_tvr.mean(), 'Std': daily_tvr.std()}
