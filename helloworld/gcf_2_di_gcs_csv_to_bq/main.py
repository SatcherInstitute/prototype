# GCF Environment Variables:
# DATASET = Target BQ dataset.
# TABLE = Target BQ table.

from google.cloud import bigquery
import os

def gcf_2_di_gcs_csv_to_bq(event, context):
  # Instantiate the clients.
  client = bigquery.Client()      
  dataset_ref = client.dataset(os.environ['DATASET'])
  job_config = bigquery.LoadJobConfig()
  
  # Always append, so we can keep the history.
  job_config.write_disposition = 'WRITE_APPEND'
  
  # Define the target table schema.
  job_config.schema = [
    bigquery.SchemaField('date', 'DATE'),
    bigquery.SchemaField('county', 'STRING'),
    bigquery.SchemaField('state', 'STRING'),
    bigquery.SchemaField('fips', 'INTEGER'),
    bigquery.SchemaField('cases', 'INTEGER'),
    bigquery.SchemaField('deaths', 'INTEGER'),
    bigquery.SchemaField('confirmed_cases', 'INTEGER'),
    bigquery.SchemaField('confirmed_deaths', 'INTEGER'),
    bigquery.SchemaField('probable_cases', 'INTEGER'),
    bigquery.SchemaField('probable_deaths', 'INTEGER')
  ]
  
  # Ignore the first header row, and set that it's a CSV.
  job_config.skip_leading_rows = 1
  job_config.source_format = bigquery.SourceFormat.CSV

  # I has a bukkit. The parameters are pulled from the Pub/Sub message.
  uri = 'gs://' + event['bucket'] + '/' + event['name']

  # Load it up.
  load_job = client.load_table_from_uri(
    uri,
    dataset_ref.table(os.environ['TABLE']),
    job_config=job_config)

  load_job.result()  # Wait for table load to complete.
  print('Job finished.')