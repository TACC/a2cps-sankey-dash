# Data Loading
import json
import pandas as pd
import os
import io
import numpy as np
import datetime

# Data reqeuests
import requests

# ----------------------------------------------------------------------------
# Load Data from TACC
# ----------------------------------------------------------------------------

def get_latest_files_list(report_suffix, mcc_list):
    ''' Generate a list of the available latest files using the logic by which they should be made available'''
    data_files = []
    for mcc in mcc_list:
        filename = report_suffix.replace('[mcc]',str(mcc))
        data_files.append({str(mcc) : filename})
    return data_files

def get_available_files_df(file_url_root, report):
    ''' If reoirt index is available, generate list of historical records that are available.
    If there is an error on the request, simply return None.
    '''
    index_url = '/'.join([file_url_root, report,'index.json'])
    i_request = requests.get(index_url)
    if i_request != 200:
        # print(i_request.status_code)
        return pd.DataFrame()
    else:
        i = i_request.json()
        df = pd.DataFrame.from_dict({(a,b): i[a][0][b]
                               for a in i.keys()
                               for b in i[a][0].keys()}
                                 ,orient='index'
                               )
        df[['date', 'time']] = pd.DataFrame(df.index.to_list(), index=df.index)
        df['mcc'] = df.apply(lambda x: x[0]['mcc'], axis=1)
        df['file'] = df.apply(lambda x: x[0]['file'], axis=1)
        df.rename(columns={0:'files_dict'}, inplace=True)
        df = df.sort_values(['date','time'], ascending=False).drop_duplicates(['date','mcc'])
        return df


def get_data_files_list(selected_date, available_files_df):
    '''For a selected date, use the available files dataframe to generate a list of available files for that date '''
    if available_files_df:
        data_files = []
        mcc_list = available_files_df[(available_files_df['date']==selected_date)]['mcc'].unique()
        for mcc in mcc_list:
            mcc= str(mcc)
            data_files.append({mcc: available_files_df.iloc[0]['file']})
        return data_files
    else:
        return None

def load_data(file_url_root, report, files_list):
    '''Load data for a specified file. Handle 500 server errors'''
    cosort_columns = ['source','target','value', 'mcc']
    df = pd.DataFrame(columns=cosort_columns)
    for f in files_list:
        for mcc in f.keys():
            file = f[mcc]
            csv_url = '/'.join([file_url_root, report, file])
            csv_request = requests.get(csv_url)
            # print(csv_request.status_code)
            csv_content = csv_request.content
            try:
                csv_df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')), usecols=[0,1,2], header=None)
                csv_df['mcc'] = mcc
                csv_df.columns = cosort_columns
            except:
                csv_df = pd.DataFrame(columns=cosort_columns)
            df = pd.concat([df,csv_df])
    return df


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
