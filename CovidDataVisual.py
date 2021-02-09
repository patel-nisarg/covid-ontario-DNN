# Creates an HTML file consisting of an interactive plot from Ontario Covid-19 database.

import pandas as pd
import numpy as np
import ssl
import bokeh.plotting as plt
from bokeh.models import LinearAxis, Range1d, HoverTool, SingleIntervalTicker
from scipy.signal import savgol_filter as sf

data_url = 'https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv'

school_data_url = 'https://data.ontario.ca/dataset/b1fef838-8784-4338-8ef9-ae7cfd405b41/resource/7fbdbb48-d074-45d9-93cb-f7de58950418/download/schoolcovidsummary.csv'

ssl._create_default_https_context = ssl._create_unverified_context
data = pd.read_csv(data_url)
sch_data = pd.read_csv(school_data_url)

columns = list(data)
sc_columns = list(sch_data)
tot_cases = np.nan_to_num(np.array(data['Total Cases'])).astype(np.int64)
new_cases = [tot_cases[x] - tot_cases[x - 1] for x in range(2, len(tot_cases))]
new_sch_cases = np.array(sch_data[sc_columns[5]])

tot_tests = np.nan_to_num(np.array(data[columns[9]])).astype(np.int64)
dates = pd.to_datetime(data[columns[0]])[2:]
dates_num = np.arange(1, len(dates) - 1)

tot_deaths = np.nan_to_num(np.array(data['Deaths']).astype(np.int64))
new_deaths = [tot_deaths[x] - tot_deaths[x - 1] for x in range(2, len(tot_deaths))]
axis2 = np.nan_to_num(np.array(new_deaths))  # Change column selection here

axis3 = np.nan_to_num(np.array(data[columns[9]][2:]))
smoothened_y1 = sf(new_cases, window_length=31, polyorder=3)

# Creating first figure and setting parameters
fig = plt.figure(x_axis_type="datetime", sizing_mode='stretch_both')
ticker = SingleIntervalTicker(interval=5, num_minor_ticks=10)
fig.xaxis.axis_label = 'Date'
fig.y_range = Range1d(start=0, end=max(new_cases) * 1.1)
fig.yaxis.axis_label = 'New Daily Cases'

# Create second axis and add it to plot
fig.extra_y_ranges = {"axis2": Range1d(start=0, end=max(axis2) * 1.1)}
fig.add_layout(LinearAxis(y_range_name="axis2", axis_label='Total Deaths'), 'right')

source = plt.ColumnDataSource(data={
    'x': dates,
    'y1': new_cases,
    'y2': axis2,
    'y3': smoothened_y1
})

plot1 = fig.line(
    x='x',
    y='y1',
    legend_label='New daily cases',
    color='green',
    source=source
)
fig.add_tools(HoverTool(renderers=[plot1], tooltips=[('Value', '@y1'),
                                                     ('Date', '@x{%F}')], formatters={'@x': 'datetime'}, mode='vline'))

plot1_1 = fig.line(
    x='x',
    y='y3',
    color='green',
    source=source,
    line_width=6,
    line_alpha=0.5,
    legend_label='Savitzky-Golay Filter Smoothened'
)

plot2 = fig.line(
    x='x',
    y='y2',
    legend_label='New Deaths',
    color='purple',
    y_range_name='axis2',
    source=source
)
fig.add_tools(HoverTool(renderers=[plot2], tooltips=[('Value', '@y2'),
                                                     ('Date', '@x{%F}')], formatters={'@x': 'datetime'}, mode='vline'))

fig.toolbar.logo = None
fig.toolbar_location = 'above'
fig.legend.location = 'top_left'
fig.ygrid.minor_grid_line_color = 'grey'
fig.ygrid.minor_grid_line_alpha = 0.1
fig.xgrid.minor_grid_line_color = 'grey'
fig.xgrid.minor_grid_line_alpha = 0.1

plt.output_file('covid_ontario_visual.html')
plt.show(fig)
