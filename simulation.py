"""
Fuctions for a process to simulate an alpha.
"""

import argparse
import copy
import ctypes
import importlib
import json
import os
import pickle
from multiprocessing import Array, Process, Queue
import pandas
from thousandaire.constants import DATA_LIST_ALL, OFFICIAL_CURRENCY
from thousandaire.constants import TRADING_CONFIGS
from thousandaire.constants import TRADING_INSTRUMENTS, TRADING_REGIONS
from thousandaire.data_loader import DataLoader
from thousandaire.evaluator import Evaluator
from thousandaire.simulator import Simulator

PRICE_DATASET = 'price_dataset'
PNL_FUNCTION = 'pnl_function'

def build_parser():
    """
    Get the alpha path and handling information.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--alpha_settings_paths',
        help='Paths of alpha settings files, separated by spaces.',
        nargs='*')
    parser.add_argument(
        '-s', '--skip_evaluation',
        help='Running the simulation without evaluation..',
        action='store_true')
    parser.add_argument(
        '-q', '--quiet_mode',
        help='Running the simulation without output to screen.',
        action='store_true')
    parser.add_argument(
        '-o', '--output_path',
        help='Path to dump simulation results.',
        action='store')
    return parser.parse_args()

def encode_data(data):
    """
    Encode data to build shared memory.
    """
    return Array(ctypes.c_char, pickle.dumps(data), lock=False)

def initialize():
    """
    Load all available dataset and bind them with workdays.

    Return bound data, which is a dict of regions to Dataset.
    """
    raw_dataset = DataLoader(DATA_LIST_ALL).get_all()
    workdays_all = {
        region : raw_dataset['workdays'][region]
        for region in TRADING_REGIONS if region in raw_dataset['workdays']}
    bound_dataset = {}
    bound_dataset['workdays'] = {}
    for region, workdays in workdays_all.items():
        bound_dataset[region] = copy.deepcopy(raw_dataset)
        for name, dataset in bound_dataset[region].items():
            dataset.set_workdays(workdays)
            bound_dataset[region][name] = encode_data(dataset)
        bound_dataset['workdays'][region] = encode_data(workdays)
    return bound_dataset

def extract_data(raw_dataset, dataset_list, price_dataset, region):
    """
    Extract data on data_list from raw_data.
    This function will decode the data from shared memory.

    Return data will be a dictionary, including three key-value pairs:
    (1) 'workdays'
        a DataController, the workdays data of the trading region.
    (2) 'price'
        a Dataset, the price dataset of the trading region.
    (3) 'others'
        a dict of Dataset, other data that users specify in data_list.
    """
    return {
        'workdays' : pickle.loads(raw_dataset['workdays'][region]),
        'price' : pickle.loads(raw_dataset[region][price_dataset]),
        'others' : {name : pickle.loads(raw_dataset[region][name])
                    for name in dataset_list if name in raw_dataset[region]}}

def convert_to_dataframe(results, instruments):
    """
    Change results format into pandas DataFrame.
    """
    form = {
        'instrument': [],
        'date': [],
        'pnl': [],
        'cost': [],
        'position': []
    }
    for today in results:
        date = today.date
        for instrument in instruments:
            form['date'].append(date)
            form['instrument'].append(instrument)
            form['pnl'].append(today.pnl[instrument])
            form['cost'].append(today.cost[instrument])
            form['position'].append(
                today.position_raw.get(instrument, 0.))
    return pandas.DataFrame(data=form)

def handle_result(alpha_path, results_set, quiet_mode, output_path):
    """
    Handle results of simulation.
    """
    results, eval_results, instruments = results_set
    if output_path:
        output_data = {
            'simulation_results': results,
            'evaluation_results': eval_results}
        with open(os.path.join(output_path, 'results'), 'wb') as file:
            pickle.dump(output_data, file)
    if not quiet_mode:
        with pandas.option_context(
                'display.max_rows', None, 'display.max_columns', None):
            print(alpha_path,
                  convert_to_dataframe(results, instruments),
                  json.dumps(eval_results, indent=1), sep='\n')

def simulate(results_queue, data_all, alpha_settings_path, skip_evaluation):
    """
    Act the process of simulating.
    """
    try:
        settings = importlib.import_module(alpha_settings_path).AlphaSettings()
    except FileNotFoundError as error:
        raise FileNotFoundError("Alpha does not exist.") from error
    except ImportError as error:
        raise ImportError("No available AlphaSettings in %s"
                          % alpha_settings_path) from error
    if not settings.is_valid():
        raise TypeError("Incorrect type in %s settings" % alpha_settings_path)
    _, region = settings.target
    data_required = extract_data(
        data_all, settings.data_list,
        TRADING_CONFIGS[settings.target][PRICE_DATASET], region)
    if (settings.end_date is None or
            settings.end_date > data_required['workdays'][-1].date):
        settings.end_date = data_all['workdays'][region][-1].date
    pnl_function = TRADING_CONFIGS[settings.target][PNL_FUNCTION](
        OFFICIAL_CURRENCY[region], TRADING_INSTRUMENTS[settings.target])
    results = Simulator(settings, data_required, pnl_function).run()
    eval_results = (
        Evaluator().run(TRADING_INSTRUMENTS[settings.target], results)
        if not skip_evaluation else None)
    results_queue.put(
        (alpha_settings_path, TRADING_INSTRUMENTS[settings.target],
         results, eval_results))

def dispatcher(args, data_all):
    """
    Dispatch simulation process for each alpha.
    """
    processes = []
    results_queue = Queue()
    for path in args.alpha_settings_paths:
        process = Process(
            target=simulate,
            args=(
                results_queue, data_all,
                path, args.skip_evaluation))
        process.start()
        processes.append(process)
    unordered_results = {}
    while any(process.is_alive() for process in processes):
        if not results_queue.empty():
            path, instruments, results, eval_results = results_queue.get()
            unordered_results[path] = (results, eval_results, instruments)
    for process in processes:
        process.join()
    for path in args.alpha_settings_paths:
        handle_result(
            path, unordered_results[path], args.quiet_mode, args.output_path)

def main():
    """
    Run the simulation process.
    """
    args = build_parser()
    data_all = initialize()
    dispatcher(args, data_all)

if __name__ == '__main__':
    main()
