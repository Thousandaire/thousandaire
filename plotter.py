"""
Plotter functions.
"""

import pandas
import plotly.express
import plotly.io

def line(data, title='2D-line', x_axial='X', y_axial='Y'):
    '''
    Function for 2D-line.

    Parameters:
        data: required type is dict of tuple list. Each keys means names of
            data preparing to draw, and each tuple means a coordinate point.
        title: required type is str. The name of the picture.
        x_axial: required type is str. The name of x axial.
        y_axial: required type is str. The name of y axial.

    Returns: representation of figure as an HTML div string
    '''
    plot_data = {
        'instruments' : [],
        x_axial : [],
        y_axial : []
    }
    for instrument, values in data.items():
        for value in values:
            plot_data[x_axial].append(value[0])
            plot_data[y_axial].append(value[1])
            plot_data['instruments'].append(instrument)
    data = pandas.DataFrame(data=plot_data)
    fig = plotly.express.line(
        data, x=x_axial, y=y_axial, color='instruments', title=title)
    return plotly.io.to_html(fig)
