import json
import logging
from pandas import DataFrame
from .gcs_to_bq_util import load_values_as_dataframe, append_dataframe_to_bq


# TODO replace aaron_census_test with the dataset we'll end up actually using
_BQ_DATASET = 'aaron_census_test'


def write_state_names_to_bq(table_name, gcs_bucket, filename):
  """Writes state names to BigQuery from bucket

     table_name: The name of the biquery table to write to
     gcs_bucket: The name of the gcs bucket to read the data from
     filename: The name of the file in the gcs bucket to read from"""
  try:
    frame = load_values_as_dataframe(gcs_bucket, filename)
    frame = frame.rename(columns={'state': 'state_code', 'NAME': 'state_name'})
    column_types = {'state_code': 'STRING', 'state_name': 'STRING'}
    append_dataframe_to_bq(frame, column_types, _BQ_DATASET, table_name)
  except json.JSONDecodeError as err:
    msg = 'Unable to write to BigQuery due to improperly formatted data: {}'
    logging.error(msg.format(err))
