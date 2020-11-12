"""
Fuctions for a process to simulate an alpha.
"""

import argparse
import copy
import importlib
import os
import pickle
from thousandaire.constants import DATA_LIST_ALL, OFFICIAL_CURRENCY
from thousandaire.constants import TRADING_CONFIGS
from thousandaire.constants import TRADING_INSTRUMENTS, TRADING_REGIONS
from thousandaire.data_classes import Dataset
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
        'alpha_settings_path', help='Path of the alpha settings file.')
    parser.add_argument(
        '-s', '--skip_evaluation',
        help='Running the simulation without evaluation..',
        action='store_true')
    parser.add_argument(
        '-screen', '--skip_screen_print',
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

def handle_result(output_path, skip_screen_print, results, eval_results):
    """
    Handle results of simulation.
    """
    if output_path:
        output_data = {
            'simulation_results': results,
            'evaluation_results': eval_results}
        with open(os.path.join(output_path, 'results'), 'wb') as file:
            pickle.dump(
                Dataset('results', output_data), file)
    if not skip_screen_print:
        print(results, eval_results, sep='\n')

def simulate(alpha_settings_path, skip_evaluation,
             skip_screen_print, output_path):
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
    data_all = initialize()
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
    eval_results = (
        Evaluator().run(TRADING_INSTRUMENTS[settings.target], results)
        if not skip_evaluation else None)
    handle_result(output_path, skip_screen_print, results, eval_results)

def main():
    """
    Run the simulation process.
    """
    args = build_parser()
    simulate(args.alpha_settings_path, args.skip_evaluation,
             args.skip_screen_print, args.output_path)

if __name__ == '__main__':
    main()
