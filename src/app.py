# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------

# File Management
import os # Operating system library
import pathlib # file paths

# Data Cleaning and transformations
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Get data from url, with ability to retry


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
# Data loading parameters
# ----------------------------------------------------------------------------
file_url_root ='https://api.a2cps.org/files/v2/download/public/system/a2cps.storage.community/reports'
report = 'consort'
report_suffix = report + '-data-[mcc]-latest.csv'
mcc_list=[1,2]

# Load Data for page
latest_files = get_latest_files_list(report_suffix, mcc_list)
latest_data = load_data(file_url_root, report, latest_files) # Load data for latest data from url
# latest_data = pd.read_csv(os.path.join(ASSETS_PATH, 'latest.csv')) # line to Load from local files for development purposes
latest_data_dict = latest_data.to_dict('records')

files_df = get_available_files_df(file_url_root, report)

if not files_df.empty:
    past_dates = list(files_df['date'].unique())
else:
    past_dates = []

date_options = [{'label': 'latest', 'value': 'latest'}] + [{'label': d, 'value': d} for d in past_dates]
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
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div([
                    dcc.Store(id='store_data'),
                    html.Div(id='div_store_data'),
                    html.Div(id='div_test'),
                    dbc.Row([
                        dbc.Col([
                            html.H1('CONSORT Report'),
                        ],md = 8),
                        dbc.Col([
                            dcc.Dropdown(
                                id='dropdown-date',
                                options=date_options,
                                value=date_options[0]['value'],
                            ),
                        ],id='dd_date',md=2),
                        dbc.Col([
                            # TO DO: Convert this dropdown to use a list generated from the date selected in the dates dropdown.
                            dcc.Dropdown(
                                id='dropdown-mcc',
                                options=[
                                    {'label': 'MCC1', 'value': '1'},
                                    {'label': 'MCC2', 'value': '2'}
                                ],
                                value='1',
                            ),
                        ],id='dd_mcc',md=2),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div(id="report_msg"),
                        ],md = 9),
                        dbc.Col([

                        ],md = 3),
                    ]),
                    html.Div(id = 'dash_content'),
                ],id="loading-output-1")
            ),

        ], style =CONTENT_STYLE)
    ],style=TACC_IFRAME_SIZE)

app.layout = get_layout

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------
# load selected data into data store
@app.callback(
    Output('store_data', 'data'),
    Output('dropdown-mcc', 'value'),
    Input('dropdown-date', 'value'),
    State('store_data', 'data'))
def set_dropdown_dates_value(selected_date, store_data):
    if not get_django_user():
        raise PreventUpdate
    if not selected_date:
        raise PreventUpdate
    else:
        if store_data is None:
            store_data = {}
            store_data['latest'] = latest_data.to_dict('records')
        else:
            store_data = store_data
            if selected_date in store_data.keys():
                store_data = store_data
            else:
                selected_date_files = get_data_files_list(selected_date, files_df)
                selected_date_data = load_data(file_url_root, report, selected_date_files)
                if len(selected_date_data) > 0:
                    store_data[str(selected_date)] = selected_date_data.to_dict('records')
                else:
                    store_data = store_data

        return store_data, '1'

# Load content of page
@app.callback(
    Output('dash_content','children'),
    Input('dropdown-mcc', 'value'),
    State('store_data', 'data'),
    State('dropdown-date', 'value'))
def show_store_data(mcc, store_data, selected_date):
    if not get_django_user():
        raise PreventUpdate
    df_json = store_data[str(selected_date)]
    error_div = html.Div('There is no data available for this selection')
    if not df_json:
        return error_div
    else:
        df = pd.DataFrame.from_dict(df_json)
        if len(df) == 0:
            kids = [html.P('len 0')]
            return error_div
        else:
            if str(selected_date) == 'latest':
                chart_title = 'CONSORT Report from latest data'

            else: # historical data from csv loaded to data store
                chart_title = 'CONSORT Report from str(selected_date)'

            # selected_df = df[df['mcc'] == str(mcc)]
            selected_df = df[df['mcc']==str(mcc)] #[df['mcc']==int(mcc)]

            if len(selected_df) > 0:
                data_table = build_datatable(selected_df,'table_selected')
                nodes, sankey_df = get_sankey_dataframe(selected_df) # transform data into sankey data format
                sankey_fig = build_sankey(nodes, sankey_df) # turn sankey data into sankey figure
                sankey_fig.update_layout(title = chart_title)
                chart = dcc.Graph(id="sankey_chart",figure=sankey_fig) # create dash component chart from figure
                dash_content = build_dash_content(chart, data_table) # create page content from variables
                # dash_content = [data_table]
                content = html.Div([
                    html.Div([html.P(str(len(nodes)))]),
                    data_table,
                ])
                return dash_content  #dash_content
            else:
                return error_div





# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
