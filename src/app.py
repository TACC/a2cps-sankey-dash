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
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq

from flask import request

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
# Sample JSON
# ----------------------------------------------------------------------------
latest_data = [{"source": "Screened Patients", "target": "Declined - Not interested in research", "value": 249, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - COVID-related", "value": 9, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Compensation insufficient", "value": 2, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Specific study procedure", "value": 226, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Time related", "value": 762, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - No reason provided", "value": 662, "mcc": "1"}, {"source": "Screened Patients", "target": "Consented Patients", "value": 476, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject chose to discontinue the study", "value": 14, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Site PI chose to discontinue subject participation", "value": 25, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject is lost to follow-up, unable to locate", "value": 2, "mcc": "1"}, {"source": "Consented Patients", "target": "Patients Reaching Baseline", "value": 409, "mcc": "1"}, {"source": "Patients Reaching Baseline", "target": "Patients With Surgery", "value": 398, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject chose to discontinue the study", "value": 3, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject is lost to follow-up, unable to locate", "value": 2, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Patients Reaching Week 6", "value": 377, "mcc": "1"}, {"source": "Patients Reaching Week 6", "target": "Early Terminations - Subject chose to discontinue the study", "value": 1, "mcc": "1"}, {"source": "Patients Reaching Week 6", "target": "Patients Reaching Month 3", "value": 328, "mcc": "1"}, {"source": "Reaching Month 3", "target": "Early Terminations - Subject is lost to follow-up, unable to locate", "value": 3, "mcc": "1"}, {"source": "Patients Reaching Month 3", "target": "Patients Reaching Month 6", "value": 247, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Not interested in research", "value": 123, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - COVID-related", "value": 2, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Compensation insufficient", "value": 6, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Specific study procedure", "value": 112, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Time related", "value": 176, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - No reason provided", "value": 128, "mcc": "2"}, {"source": "Screened Patients", "target": "Consented Patients", "value": 184, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject chose to discontinue the study", "value": 13, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Site PI chose to discontinue subject participation", "value": 4, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject is lost to follow-up, unable to locate", "value": 1, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Death", "value": 2, "mcc": "2"}, {"source": "Consented Patients", "target": "Patients Reaching Baseline", "value": 152, "mcc": "2"}, {"source": "Patients Reaching Baseline", "target": "Patients With Surgery", "value": 137, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject chose to discontinue the study", "value": 1, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Early Terminations - Death", "value": 1, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Patients Reaching Week 6", "value": 124, "mcc": "2"}, {"source": "Patients Reaching Week 6", "target": "Patients Reaching Month 3", "value": 96, "mcc": "2"}, {"source": "Reaching Month 3", "target": "Early Terminations - Subject chose to discontinue the study", "value": 3, "mcc": "2"}, {"source": "Reaching Month 3", "target": "Early Terminations - Site PI chose to discontinue subject participation", "value": 2, "mcc": "2"}, {"source": "Patients Reaching Month 3", "target": "Patients Reaching Month 6", "value": 56, "mcc": "2"}]
# ----------------------------------------------------------------------------
# Data loading parameters
# ----------------------------------------------------------------------------
file_url_root ='https://api.a2cps.org/files/v2/download/public/system/a2cps.storage.community/reports'
report = 'consort'
report_suffix = report + '-data-[mcc]-latest.csv'
mcc_list=[1,2]

latest_data_dict = {'start':'here'}
global_variable = 'THIS IS GLOBAL'

def load_latest_data(file_url_root, report, report_suffix, mcc_list):
    # Load Data for page
    latest_files = get_latest_files_list(report_suffix, mcc_list)
    latest_data = load_data(file_url_root, report, latest_files) # Load data for latest data from url
    # latest_data = pd.read_csv(os.path.join(ASSETS_PATH, 'latest.csv')) # line to Load from local files for development purposes
    latest_data_dict = latest_data.to_dict('records')
    return latest_data_dict

def load_available_files(file_url_root, report):
    files_df = get_available_files_df(file_url_root, report)

    if not files_df.empty:
        past_dates = list(files_df['date'].unique())
    else:
        past_dates = []
    past_dates_options = [{'label': d, 'value': d} for d in past_dates]

    return past_dates_options
# ----------------------------------------------------------------------------
# DASH APP LAYOUT
# ----------------------------------------------------------------------------
external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=REQUESTS_PATHNAME_PREFIX,
                )

def get_layout():
    if not get_django_user():
        return html.H1("Unauthorized")
    global latest_data_dict
    latest_data_dict = load_latest_data(file_url_root, report, report_suffix, mcc_list)
    date_options = [{'label': 'latest', 'value': 'latest'}]
    past_dates_options = load_available_files(file_url_root, report)
    if len(past_dates_options) > 0:
        date_options = date_options + past_dates_options
    layout =  html.Div([
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div([
                    dcc.Store(id='latest_data', data = latest_data_dict),
                    dcc.Store(id='store_data'),
                    dcc.Store(id='date_data'),
                    html.Div(id='div_store_data'),
                    html.Div(id='div_test'),
                    dbc.Row([
                        dbc.Col([
                            html.H1('CONSORT REPORT (new)'),
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
    return layout

app.layout = get_layout

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------
# load selected data into data store
@app.callback(
    Output('store_data', 'data'),
    Output('date_data', 'data'),
    # Output('dash_content','children'),
    Input('dropdown-date', 'value'),
    State('store_data', 'data'),
    )
def set_dropdown_dates_value(selected_date, store_data):
    if not get_django_user():
        raise PreventUpdate
    if not selected_date:
        raise PreventUpdate
    else:
        global latest_data_dict
        global global_variable

        if selected_date == 'latest':
            sankey_data = latest_data_dict
        elif selected_date in store_data.keys():
            sankey_data = store_data[selected_date]
        else:
            selected_date_files = get_data_files_list(selected_date, files_df)
            selected_date_data = load_data(file_url_root, report, selected_date_files)
            if len(selected_date_data) > 0:
                store_data[str(selected_date)] = selected_date_data.to_dict('records')
                sankey_data = store_data[str(selected_date)]
            else:
                store_data = store_data
                sankey_data = {}

        return store_data, sankey_data

# Load content of page
@app.callback(
    Output('dash_content','children'),
    Input('dropdown-mcc', 'value'),
    State('date_data', 'data'),
    State('dropdown-date', 'value'))
def show_store_data(mcc, date_data, selected_date):
    if not get_django_user():
        raise PreventUpdate
    print(selected_date)
    df_json = date_data
    error_div = html.Div('There is no data available for this selection')
    if not mcc:
        return html.Div('Please select an mcc to view data')
    if not df_json:
        print('no df')
        return error_div
    else:
        df = pd.DataFrame.from_dict(df_json)
        print(len(df))
        if len(df) == 0:
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
    app.run_server(debug=True, port = 8040)
else:
    server = app.server
