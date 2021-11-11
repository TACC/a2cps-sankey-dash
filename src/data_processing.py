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


# ----------------------------------------------------------------------------
# API DATA FUNCTIONS
# ----------------------------------------------------------------------------

## FUNCTIONS FOR LOADING DATA: MOVE TO MODULE
def load_api_data(api_url):
    '''Get dictionary of sankey data if provided a valid API url'''
    try:
        response = requests.get(api_url)
        api_data = response.json()
    except:
        return False
    return api_data

def get_api_df(api_data):
    ''' Take a dictionary of data balues and return a dataframe with source, target and value columns to build sankey '''
    if load_api_data(api_url):
        api_data = load_api_data(api_url)
        df = pd.DataFrame.from_dict(api_data)
    else:
        cosort_columns = ['source','target','value']
        df = pd.DataFrame(columns = cosort_columns)
    return df

# ----------------------------------------------------------------------------
# Load data from TACC files
# ----------------------------------------------------------------------------
def get_latest_files_list(report_suffix, mcc_list):
    data_files = []
    for mcc in mcc_list:
        filename = report_suffix.replace('[mcc]',str(mcc))
        data_files.append({str(mcc) : filename})

    return data_files

def get_available_files_df(file_url_root, report):
    index_url = '/'.join([file_url_root, report,'index.json'])
    i = requests.get(index_url).json()
    df = pd.DataFrame.from_dict({(a,b): i[a][0][b]
                           for a in i.keys()
                           for b in i[a][0].keys()}
                             ,orient='index'
                           )
    df[['date', 'time']] = pd.DataFrame(df.index.to_list(), index=df.index)
    df['mcc'] = df.apply(lambda x: x[0]['mcc'], axis=1)
    df['file'] = df.apply(lambda x: x[0]['file'], axis=1)
    df.rename(columns={0:'files_dict'}, inplace=True)
    return df


def get_data_files_list(selected_date, mcc_list, available_files_df):
    data_files = []
    for mcc in mcc_list:
        mcc= str(mcc)
        selected_df = available_files_df[(available_files_df['date']==selected_date) & (available_files_df['mcc']==mcc)]
        selected_df = selected_df.sort_values(by=['time'], ascending=False)
        data_files.append({mcc: selected_df.iloc[0]['file']})
    return data_files
    
# ----------------------------------------------------------------------------
# Format data for Sankey
# ----------------------------------------------------------------------------

def get_sankey_nodes(dataframe,source_col = 'source', target_col = 'target'):
    ''' Extract node infomration from sankey dataframe in case this is not provided '''
    nodes = pd.DataFrame(list(dataframe[source_col].unique()) + list(dataframe[target_col].unique())).drop_duplicates().reset_index(drop=True)
    nodes.reset_index(inplace=True)
    nodes.columns = ['NodeID','Node']
    return nodes

def get_sankey_dataframe (data_dataframe,
                          node_id_col = 'NodeID', node_name_col = 'Node',
                          source_col = 'source', target_col = 'target', value_col = 'value'):
    ''' Merge Node dataframes with data dataframe to create dataframe properly formatted for Sankey diagram.
        This means each source and target gets assigned the Index value from the nodes dataframe for the diagram.
    '''
    # get nodes from data
    nodes = get_sankey_nodes(data_dataframe)

    # Copy of Node data to merge on source
    sources = nodes.copy()
    sources.columns = ['sourceID','source']

    # Copy of Node data to merge on target
    targets = nodes.copy()
    targets.columns = ['targetID','target']

    # Merge the data dataframe with node information
    sankey_dataframe = data_dataframe.merge(sources, on='source')
    sankey_dataframe = sankey_dataframe.merge(targets, on='target')

    return nodes, sankey_dataframe

def load_historical_data(csv_url):
    '''Load csv of historical dates and extract unique dates for dropdown options'''
    try :
        # Data Frame
        historical_data = pd.read_csv(csv_url, header = None)
        historical_data.columns=['source','target','value','date']
        historical_data['date_time'] = historical_data['date'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d (%H:%M)'))

    except :
        historical_data = 'Could not access data'

    return historical_data
