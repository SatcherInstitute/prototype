import os
import json
import time
from google.cloud import bigquery, storage
from pandas import DataFrame


def append_dataframe_to_bq(frame, column_types, dataset, table_name):
  """Appends the provided DataFrame to the table specified by
     `dataset.table_name`. Automatically adds an ingestion time column.

     frame: pandas.DataFrame representing the data to append.
     column_types: A dict of column name to BigQuery data type. The column
                   names must match the columns in the DataFrame
     dataset: The BigQuery dataset to write to
     table_name: The BigQuery table to write to"""
  input_cols = column_types.keys()
  if (len(input_cols) != len(frame.columns)
          or set(input_cols) != set(frame.columns)):
    raise Exception('Column types did not match frame columns')

  columns = column_types.copy()
  columns['ingestion_time'] = 'TIMESTAMP'
  ingestion_time = time.time()
  frame['ingestion_time'] = ingestion_time

  client = bigquery.Client()
  dataset_ref = client.dataset(dataset)
  job_config = bigquery.LoadJobConfig()

  # Always append, so we can keep the history.
  job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

  schema = list(
      map(lambda col: bigquery.SchemaField(col, columns[col]), columns.keys()))
  job_config.schema = schema

  # Note: BQ tables can be loaded directly from DataFrames but there's an
  # implicit dependency on pyarrow which has some issues with python 3.8
  result = frame.to_json(orient='records')
  json_data = json.loads(result)
  load_job = client.load_table_from_json(
      json_data,
      dataset_ref.table(table_name),
      job_config=job_config)

  load_job.result()  # Wait for table load to complete.


def load_values_as_dataframe(gcs_bucket, filename):
  """Loads data from the provided gcs_bucket and filename to a DataFrame.
     Expects the data to be in the pandas 'values' format: a list of rows,
     where each row is a list of values.

     gcs_bucket: The name of the gcs bucket to read the data from
     filename: The name of the file in the gcs bucket to read from"""
  client = storage.Client()
  bucket = client.get_bucket(gcs_bucket)
  blob = bucket.blob(filename)
  local_path = local_file_path(filename)
  blob.download_to_filename(local_path)

  with open(local_path) as json_file:
    data = json.load(json_file)

    col_names = data[0].copy()
    records = data[1:].copy()
    frame = DataFrame.from_records(records, columns=col_names)

    os.remove(local_path)
    return frame


def local_file_path(filename):
  return '/tmp/{}'.format(filename)
