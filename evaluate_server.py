"""
Server to handle processes of evaluating.
"""

import pickle
from flask import Flask
from flask import request
from ratelimit import limits
from thousandaire.evaluator import Evaluator

APP = Flask(__name__)

@APP.route('/', methods=['POST'])
@limits(calls=100, period=1)
def evaluate():
    """
    Connect with evaluator.
    """
    eval_data = pickle.loads(request.get_data())
    indicator_names = eval_data['indicator_names']
    instruments = eval_data['instruments']
    data = eval_data['data']
    return pickle.dumps(Evaluator(indicator_names).run(instruments, data))

if __name__ == '__main__':
    APP.run(debug=False)
