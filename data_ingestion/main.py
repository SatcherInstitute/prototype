import base64
import json
import logging
from common.census import upload_household_income, upload_state_names
from common.pubsub_publisher import notify_data_ingested


# Data source name literals. These correspond to a specific data ingestion workflow.
_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_STATE_NAMES = 'STATE_NAMES'


def ingest_data(event, context):
  """Main GCF function for data ingestion. Receives Pub/Sub trigger and triages to the
     appropriate data ingestion workflow.

     event: Dict containing the Pub/Sub method. The Cloud Scheduler payload will be a base-64
            encoded string in the 'data' field.
     context: Metadata about this function invocation."""
  try:
    if 'data' not in event:
      logging.warning("PubSub message missing 'data' field")
      return
    data = base64.b64decode(event['data']).decode('utf-8')
    event_dict = json.loads(data)
  except json.JSONDecodeError as err:
    logging.error("Could not load json object: %s", err)

  if 'id' not in event_dict:
    logging.error("PubSub data missing 'id' field")
    return
  if 'url' not in event_dict or 'gcs_bucket' not in event_dict or 'filename' not in event_dict:
    logging.error("Pubsub data must contain fields 'url', 'gcs_bucket', and 'filename'")
    return
  
  id = event_dict['id']
  url = event_dict['url']
  gcs_bucket = event_dict['gcs_bucket']
  filename = event_dict['filename']

  if id == _HOUSEHOLD_INCOME:
    upload_household_income(url, gcs_bucket, filename)
  elif id == _STATE_NAMES:
    upload_state_names(url, gcs_bucket, filename)

  notify_data_ingested(id, gcs_bucket, filename)
