import json
import logging
from pandas import DataFrame
from .gcs_to_bq_util import load_values_as_dataframe, append_dataframe_to_bq


def write_state_names_to_bq(dataset, table_name, gcs_bucket, filename):
  """Writes state names to BigQuery from bucket

     dataset: The BigQuery dataset to write to
     table_name: The name of the biquery table to write to
     gcs_bucket: The name of the gcs bucket to read the data from
     filename: The name of the file in the gcs bucket to read from"""
  try:
    frame = load_values_as_dataframe(gcs_bucket, filename)
    frame = frame.rename(columns={'state': 'state_code', 'NAME': 'state_name'})
    column_types = {'state_code': 'STRING', 'state_name': 'STRING'}
    append_dataframe_to_bq(frame, column_types, dataset, table_name)
  except json.JSONDecodeError as err:
    msg = 'Unable to write to BigQuery due to improperly formatted data: {}'
    logging.error(msg.format(err))
