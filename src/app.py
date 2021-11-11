# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------

# File Management
import os # Operating system library
import pathlib # file paths

# Data Cleaning and transformations
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json

# Data visualization
import plotly.express as px
import plotly.graph_objects as go

from flask import Flask

# Dash Framework
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import dash_daq as daq
from flask import request
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL, MATCH

# import local modules
from config_settings import *
from data_processing import *


# ----------------------------------------------------------------------------
# DATA urls
# ----------------------------------------------------------------------------
# URL of live API data
api_url = 'https://redcap.tacc.utexas.edu/api/vbr_api.php?op=consort'

# URL of csv of historical dataframe
csv_url = 'https://portals-api.tacc.utexas.edu/files/v2/download/wma_prtl/system/a2cps.storage.public/reports/consort/consort-data-all.csv'

# ----------------------------------------------------------------------------
# DATA VISUALIZATION
# ----------------------------------------------------------------------------

def build_sankey(nodes_dataframe, data_dataframe):
    sankey_fig = go.Figure(data=[go.Sankey(
        # Define nodes
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = .5),
          label =  nodes_dataframe['Node'],
           # color =  "red"
        ),
        # Add links
        link = dict(
          source =  data_dataframe['sourceID'],
          target =  data_dataframe['targetID'],
          value =  data_dataframe['value'],
          ),
        # orientation = 'v'
    )])
    return sankey_fig


# ----------------------------------------------------------------------------
# DATA FOR DASH UI COMPONENTS
# ----------------------------------------------------------------------------

# Data table of API data
def build_datatable(data_source, table_id):
    new_datatable =  dt.DataTable(
            id = table_id,
            data=data_source.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_source.columns],
            css=[{'selector': '.row', 'rule': 'margin: 0; flex-wrap: nowrap'},
                {'selector':'.export','rule':export_style }
                # {'selector':'.export','rule':'position:absolute;right:25px;bottom:-35px;font-family:Arial, Helvetica, sans-serif,border-radius: .25re'}
                ],
            style_cell= {
                'text-align':'left',
                'padding': '5px'
                },
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'grey',
                'fontWeight': 'bold',
                'color': 'white'
            },

            export_format="csv",
        )
    return new_datatable

def build_dates_dropdown(type, options):
    if type == 'api':
        dates_dropdown = 'api'
    else:
        dates_dropdown = 'other'
    return dates_dropdown

def build_dash_content(chart, data_table): # build_sankey(nodes, sankey_df) build_datatable(redcap_df,'table_csv') redcap_df
    dash_content = [
        dbc.Row([
            dbc.Col([
                html.Div(chart, id='div_sankey'),
            ],width=12),
            dbc.Col([
                html.Div(data_table, id='div_table'),
            ], width=12)
        ])
    ]
    return dash_content
# ----------------------------------------------------------------------------
# DASH APP LAYOUT
# ----------------------------------------------------------------------------
external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=REQUESTS_PATHNAME_PREFIX,
                )

def get_layout():
    if not get_django_user():
        return html.H1("Unauthorized")
    return html.Div([
        html.Div([
            dcc.Store(id='store_historical'),
            html.Div(['version: 040721 17:15'],id="version",style={'display':'none'}),
            html.Div(id='div_test'),
            dbc.Row([
                dbc.Col([
                    html.H1('CONSORT Report'),
                ],md = 9),
                dbc.Col([
                    daq.ToggleSwitch(
                        id='toggle-datasource',
                        label=['Live','Historical'],
                        value=False
                    ),
                ],id='dd_datasource',md=3)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(id="report_msg"),
                ],md = 9),
                dbc.Col([
                    html.Div([dcc.Dropdown(id="dropdown_dates")],id="div_dropdown_dates"),
                ],md = 3),
            ]),
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div(id="loading-output-1")
            ),
            dcc.Loading(
                id="loading-2",
                type="default",
                children=html.Div(id="loading-output-2")
            ),
            html.Div(id = 'dash_content'),

        ], style =CONTENT_STYLE)
    ],style=TACC_IFRAME_SIZE)

app.layout = get_layout

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

# return data on toggle
@app.callback(
    Output("loading-output-1", "children"),
    Output('store_historical','data'),
    Output('report_msg','children'),
    Output('dropdown_dates','options'),
    Output('div_dropdown_dates','style'),
    # Output('dash_content','children'),
    Input('toggle-datasource', 'value'),
    State('store_historical','data')
)
def dd_values(data_source, data_state):
    if not get_django_user():
        raise PreventUpdate
    # time of date loading
    now = datetime.now().astimezone()
    date_string = now.strftime("%m/%d/%Y %H:%M %z")
    msg_string = "Data last loaded at " + str(date_string) + "UTC"

    hist_dict = data_state
    dropdown_style = {}

    if(data_source): # Load historical data if not yet loaded
        if not data_state:
            hist_dict = {}
            hd = load_historical_data(csv_url) # load data from csv
            dates = list(hd['date_time'].unique()) # list of unique dates in dataframe to supply dropdown options
            dates.sort(reverse=True)
            hist_dict['data'] = hd.to_dict('records') #store data in local data store
            hist_dict['dates']  = dates

        # set dropdown dropdown_options from dates
        dropdown_options = [{'label': i, 'value': i} for i in hist_dict['dates']]

    else: # load API Json and convert --> pandas DataFrame. Always do this live.
        # Set date dropdown to API values
        dropdown_options = [{'label': 'api', 'value': 'api'}]
        dropdown_style = {'display':'none'}

    return data_source, hist_dict, msg_string, dropdown_options, dropdown_style

@app.callback(
    Output('dropdown_dates', 'value'),
    [Input('dropdown_dates', 'options')])
def set_dropdown_dates_value(available_options):
    if not get_django_user():
        raise PreventUpdate
    return available_options[0]['value']

@app.callback(
    Output("loading-output-2", "children"),
    Output('dash_content','children'),
    Input('dropdown_dates','value'),
    State('toggle-datasource', 'value'),
    State('store_historical','data')
)
def dd_values(dropdown, toggle, historical_data):
    if not get_django_user():
        raise PreventUpdate
    df = pd.DataFrame()

    if not toggle: # live data from api
        df = get_api_df(api_url) # Get data from API
        chart_title = 'CONSORT Report from live API data'

    else: # historical data from csv loaded to data store
        df = pd.DataFrame(historical_data['data'])
        df = df[df['date_time'] == dropdown]
        chart_title = 'CONSORT Report from historical archive on ' + dropdown

    if not df.empty:
        data_table = [build_datatable(df,'table_csv')] # Build data_table from api data
        nodes, sankey_df = get_sankey_dataframe(df) # transform API data into sankey data
        sankey_fig = build_sankey(nodes, sankey_df) # turn sankey data into sankey figure
        sankey_fig.update_layout(title = chart_title)
        chart = dcc.Graph(id="sankey_chart",figure=sankey_fig) # create dash component chart from figure
        dash_content = build_dash_content(chart, data_table) # create page content from variables

    else:
        dash_content = html.Div('There has been an issue in loading data')

    return toggle, dash_content

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
