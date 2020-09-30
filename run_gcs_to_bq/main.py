import logging
import os
from common.census_to_bq import write_state_names_to_bq
from flask import Flask, request
app = Flask(__name__)


_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_STATE_NAMES = 'STATE_NAMES'


@app.route('/', methods=['POST'])
def ingest_bucket_to_bq():
  """Main function for moving data from buckets to bigquery. Triggered by
     notify-data-ingested topic."""
  envelope = request.get_json()
  if not envelope:
    logging.error('No Pub/Sub message received.')
    return ('', 400)

  if not isinstance(envelope, dict) or 'message' not in envelope:
    logging.error('Invalid Pub/Sub message format')
    return ('', 400)

  data = envelope['message']
  logging.info(f"message: {data}")

  if 'attributes' not in data:
    logging.error("PubSub message missing 'attributes' field")
    return ('', 400)

  attributes = data['attributes']
  if ('id' not in attributes
      or 'gcs_bucket' not in attributes
      or 'filename' not in attributes):
    logging.error(
        "Pubsub attributes must contain 'id', 'gcs_bucket', and 'filename'")
    return ('', 400)

  workflow_id = attributes['id']
  gcs_bucket = attributes['gcs_bucket']
  filename = attributes['filename']

  if workflow_id == _STATE_NAMES:
    if 'DATASET_NAME' not in os.environ:
      logging.error("Environment variable DATASET_NAME missing.")
      return ('', 400)
    dataset = os.environ['DATASET_NAME']
    write_state_names_to_bq(dataset, 'state_names', gcs_bucket, filename)
  elif workflow_id == _HOUSEHOLD_INCOME:
    # TODO(jenniebrown): Write household income function
    pass

  return ('', 204)
