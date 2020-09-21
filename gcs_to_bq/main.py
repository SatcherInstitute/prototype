import base64
import json
import logging
from common.census_to_bq import write_state_names_to_bq


_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_STATE_NAMES = 'STATE_NAMES'


def ingest_bucket_to_bq(event, context):
  """Main GCF function for moving data from buckets to bigquery. Triggered by
     notify-data-ingested topic.

     event: Dict containing the Pub/Sub method. The Cloud Scheduler payload
            will be a base-64 encoded string in the 'data' field.
     context: Metadata about this function invocation."""
  # TODO: how to share code between functions? Would be nice to share some of
  # this message processing boilerplate between functions.
  try:
    if 'data' not in event:
      logging.warning("PubSub message missing 'data' field")
      return
    data = base64.b64decode(event['data']).decode('utf-8')
    logging.info('Message received: {}'.format(data))
  except json.JSONDecodeError as err:
    logging.error("Could not load json object: %s", err)

  if 'attributes' not in event:
    logging.error("PubSub message missing 'attributes' field")
    return
  attributes = event['attributes']
  if ('id' not in attributes
      or 'gcs_bucket' not in attributes
      or 'filename' not in attributes):
    logging.error(
        "Pubsub attributes must contain 'id', 'gcs_bucket', and 'filename'")
    return

  id = attributes['id']
  gcs_bucket = attributes['gcs_bucket']
  filename = attributes['filename']

  if id == _STATE_NAMES:
    write_state_names_to_bq('state_names', gcs_bucket, filename)
