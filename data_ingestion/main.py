import base64
import json
import logging
from common.gcf_household_income import upload_household_income


# Data source name literals. These correspond to a specific data ingestion workflow.
_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'


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
  if event_dict['id'] == _HOUSEHOLD_INCOME:
    upload_household_income(event_dict['url'], event_dict['gcs_bucket'], event_dict['filename'])
