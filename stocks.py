__author__ = 'rebecca'

from bokeh.plotting import *

import datetime
import pandas
import pandas.io.data as web
import numpy as np


# Declare functions.


def sma(prices, n_periods):
    """
    Returns the rolling mean of a given list of stock prices "prices"
    over a period of time "n_periods". This is commonly known as the "Simple
    Moving Average" in stock charts. Used in building Bollinger Bands.

    Interfaces with Pandas, so the details are sort of unknown to me.
    Return type: Array.
    """
    sma = pandas.rolling_mean(prices, n_periods, min_periods=n_periods)
    return sma  # Returns a Numpy array in this case


def bollinger_upper(prices, sma, n_periods):
    """
    Returns the upper Bollinger band line, for implementing a Bollinger
    band into the plot. The upper and lower lines use a rolling standard deviation
    to define the boundaries of a Bollinger band. Uses the list of stock prices "prices",
    the rolling mean returned by sma() "sma", to calculate over a number of periods "n_periods".

    You must use the same number of time periods as in the associated sma() function.
    Return type: Array.
    """
    stdev = pandas.rolling_std(prices, n_periods, min_periods=n_periods)
    return sma + (2 * stdev)  # Returns a Numpy Array in this case


def bollinger_lower(prices, sma, n_periods):
    """
    Returns the lower Bollinger band line, for implementing a Bollinger
    band into the plot. The upper and lower lines use a rolling standard deviation
    to define the boundaries of a Bollinger band. Uses the list of stock prices "prices",
    the rolling mean returned by sma() "sma", to calculate over a number of periods "n_periods".

    You must use the same number of time periods as in the associated sma() function.
    Return type: Array.
    """
    stdev = pandas.rolling_std(prices, n_periods, min_periods=n_periods)
    return sma - (2 * stdev)  # Returns a Numpy Array in this case


def stackify(x, y):  # TODO: What are some more descriptive labels for the parameters?
    """
    Stacks a set of data into a format appropriate for use with a Patch glyph.

    For example, in the Bollinger bands, x would be the upper band data (which gets reversed)
    and y would be the lower band data (which has the reversed upper data appended).
    This would supply the y coordinates for the Patch glyph.

    The function still needs a little more work, since it's not very generalized.
    (Especially since it assumes the input is an array.)
    Maybe a good explanation as to how Patch works would help?
    Return type: Array.
    """

    stack = np.append(y, x[::-1])
    return stack


def rsi(prices, timeframe=14):
    """
    Returns the Relative Strength Index for a list of stock prices "prices"
    over a period of time "timeframe".
    Return type: Array.
    """

    delta = np.diff(prices)
    seed = delta[:timeframe + 1]

    up = seed[seed >= 0].sum() / timeframe
    down = -seed[seed < 0].sum() / timeframe

    rs = up / down

    rsi = np.zeros_like(prices)
    rsi[:timeframe] = 100. - (100. / (1. + rs))

    for i in range(timeframe, len(prices)):

        i_delta = delta[i - 1]

        if i_delta > 0:
            upval = i_delta
            downval = 0.
        else:
            upval = 0.
            downval = -i_delta

        up = (up * (timeframe - 1) + upval) / timeframe
        down = (down * (timeframe - 1) + downval) / timeframe

        rs = up / down
        rsi[i] = 100. - (100. / (1. + rs))

    return rsi  # Returns a Numpy Array.

# Declare output file.

output_file('stocks.html', title='How are my stocks doing today?', js='relative', css='relative')

# Define timespan.

start = datetime.date(2012, 1, 1)

end = datetime.date.today()

# Define time periods (for SMA and Bollinger).

periods = 50

# List of symbols to look up.

symbols = ['AAPL', 'GOOG', 'MSFT', 'NTDOY']


# Create a plot for each symbol.

for s in symbols:
    # Obtain the data.

    data = web.DataReader(s, 'google', start, end)

    close = data['Close'].values  # Returns Numpy array.

    dates = data.index.values  # Returns Numpy array.


    # Plot raw stock data.

    x = data.index

    y = close

    line(x[50:], y[50:], color='#1B9E77', x_axis_type='datetime', tools='pan,zoom,resize,embed')
    hold()


    # Perform TA on stock data.


    # Define SMA 50.

    sma50 = sma(close, periods)

    # Define Bollinger Bands.

    upperband = bollinger_upper(close, sma50, periods)

    lowerband = bollinger_lower(close, sma50, periods)


    # Plot analyses.


    # SMA 50:

    line(x, sma50, color='#D95F02', x_axis_type='datetime')

    # Bollinger shading glyph:

    bandprice = stackify(upperband, lowerband)  # Reverse the upper band data and append it to the lower band data.

    banddates = stackify(dates, dates)  # Do the same for the dates.

    patch(pandas.to_datetime(banddates), bandprice, color='#7570B3', fill_alpha=0.2, x_axis_type='datetime')

    # TODO: Plot RSI, create a subplot

    # Remove hold, allow for more plots to be added.

    curplot().title = s
    curplot().height = 600
    curplot().width = 800

    yaxis().axis_label = 'Price (USD)'

    grid().grid_line_alpha = 0.4

    hold()


# Finally, display all plots.

show()