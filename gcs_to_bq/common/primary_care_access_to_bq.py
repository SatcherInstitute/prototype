import json
import logging
from pandas import DataFrame, read_excel
from .gcs_to_bq_util import load_values_as_dataframe, append_dataframe_to_bq
import os
import time
import xlrd
from google.cloud import bigquery, storage


FILEPATH = '{}-{}.xlsx'

STATE_NAMES = [
"Alabama",
"Alaska",
"Arizona",
"Arkansas",
"California",
"Colorado",
"Connecticut",
"Delaware",
"Florida",
"Georgia",
"Hawaii",
"Idaho",
"Illinois",
"Indiana",
"Iowa",
"Kansas",
"Kentucky",
"Louisiana",
"Maine",
"Maryland",
"Massachusetts",
"Michigan",
"Minnesota",
"Mississippi",
"Missouri",
"Montana",
"Nebraska",
"Nevada",
"New Hampshire",
"New Jersey",
"New Mexico",
"New York",
"North Carolina",
"North Dakota",
"Ohio",
"Oklahoma",
"Oregon",
"Pennsylvania",
"Rhode Island",
"South Carolina",
"South Dakota",
"Tennessee",
"Texas",
"Utah",
"Vermont",
"Virginia",
"Washington",
"West Virginia",
"Wisconsin",
"Wyoming"]

def write_primary_care_access_to_bq(dataset, table_name, gcs_bucket, fileprefix):
  """Writes primary care access stats to BigQuery from bucket

     dataset: The BigQuery dataset to write to
     table_name: The name of the biquery table to write to
     gcs_bucket: The name of the gcs bucket to read the data from
     fileprefix: The prefix of the files in the gcs landing bucket to read from"""

  client = storage.Client()
  bucket = client.get_bucket(gcs_bucket)

  for state_name in STATE_NAMES:
    filename = FILEPATH.format(fileprefix, state_name)
    blob = bucket.blob(filename)
    local_path = '/tmp/{}'.format(filename)
    blob.download_to_filename(local_path)

    try:
      frame = read_excel(io=local_path, sheet_name='Ranked Measure Data')
      data = []
      for row_index, row in frame.iterrows():
        if(row_index < 2):
          # First rows are headers we don't want
          continue
        data.append([row[0], row[1], row[2], row[108], row[109], row[110]]);
      new_dataframe = DataFrame(data=data, columns=('fips', 'state', 'county', 'num_primary_care_physicians', 'primary_care_physicians_rate', 'primary_care_physicians_ratio'))
      column_types = {'fips': 'STRING', 'state': 'STRING', 'county': 'STRING',  'num_primary_care_physicians': 'FLOAT64',  'primary_care_physicians_rate': 'FLOAT64',  'primary_care_physicians_ratio': 'STRING'}
      append_dataframe_to_bq(new_dataframe, column_types, dataset, table_name)
    except json.JSONDecodeError as err:
      msg = 'Unable to write to BigQuery due to improperly formatted data: {}'
      logging.error(msg.format(err))