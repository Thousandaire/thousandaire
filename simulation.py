"""
Fuctions for a process to simulate an alpha.
"""

import argparse
import copy
import importlib
import json
import os
import pickle
from multiprocessing import Process, Queue
from time import sleep
import requests
import pandas
from thousandaire.constants import DATA_LIST_ALL, EVAL_URL
from thousandaire.constants import OFFICIAL_CURRENCY, TRADING_CONFIGS
from thousandaire.constants import TRADING_INSTRUMENTS, TRADING_REGIONS
from thousandaire.data_loader import DataLoader
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

def initialize():
    """
    Load all available dataset and bind them with workdays.

    Return bound data, which is a dict of regions to Dataset.
    """
    raw_data = DataLoader(DATA_LIST_ALL).get_all()
    workdays_all = {
        region : raw_data['workdays'][region]
        for region in TRADING_REGIONS if region in raw_data['workdays']}
    bound_data = {}
    for region, workdays in workdays_all.items():
        bound_data[region] = copy.deepcopy(raw_data)
        for dataset in bound_data[region].values():
            dataset.set_workdays(workdays)
    bound_data['workdays'] = workdays_all
    return bound_data

def extract_data(raw_data, data_list, price_dataset, region):
    """
    Extract data on data_list from raw_data.

    Return data will be a dictionary, including three key-value pairs:
    (1) 'workdays'
        a DataController, the workdays data of the trading region.
    (2) 'price'
        a Dataset, the price dataset of the trading region.
    (3) 'others'
        a dict of Dataset, other data that users specify in data_list.
    """
    return {
        'workdays' : raw_data['workdays'][region],
        'price' : raw_data[region][price_dataset],
        'others' : {
            name : raw_data[region][name]
            for name in data_list if name in raw_data[region]}}

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
    if (settings.end_date is None or
            settings.end_date > data_all['workdays'][region][-1].date):
        settings.end_date = data_all['workdays'][region][-1].date
    data_required = extract_data(
        data_all, settings.data_list,
        TRADING_CONFIGS[settings.target][PRICE_DATASET], region)
    pnl_function = TRADING_CONFIGS[settings.target][PNL_FUNCTION](
        OFFICIAL_CURRENCY[region], TRADING_INSTRUMENTS[settings.target])
    results = Simulator(settings, data_required, pnl_function).run()
    eval_request = {
        'indicator_names': None,
        'instruments': TRADING_INSTRUMENTS[settings.target],
        'data': results}
    connect_attemp = 0
    eval_results = None
    while connect_attemp < 3:
        try:
            eval_results = (
                requests.post(EVAL_URL, data=pickle.dumps(eval_request)).content
                if not skip_evaluation else None)
            break
        except requests.ConnectionError as err:
            print('Connection falied.', err, sep='\n')
            connect_attemp += 1
            sleep(1)
    results_queue.put(
        (alpha_settings_path, TRADING_INSTRUMENTS[settings.target], results,
         pickle.loads(eval_results) if eval_results else None))

def main():
    """
    Run the simulation process.
    """
    args = build_parser()
    data_all = initialize()
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

if __name__ == '__main__':
    main()
