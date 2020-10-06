# Note: this file only exists temporarily, as an entry point for running the
# ingestion pipeline as cloud functions.

import logging
import ingestion.util as util

def ingest_data(event, context):
  try:
    util.ingest_data_to_gcs(event)
  except Exception as e:
    logging.error(e)

def ingest_bucket_to_bq(event, context):
  try:
    util.ingest_bucket_to_bq(event)
  except Exception as e:
    logging.error(e)
