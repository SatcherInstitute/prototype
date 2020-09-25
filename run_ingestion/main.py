import base64
import json
import logging
import os
from common.census import upload_household_income, upload_state_names
from common.pubsub_publisher import notify_data_ingested
from common.di_url_file_to_gcs import url_file_to_gcs
from flask import Flask, request
app = Flask(__name__)

# Data source name literals. These correspond to a specific data ingestion workflow.
_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_URGENT_CARE_FACILITIES = 'URGENT_CARE_FACILITIES'
_STATE_NAMES = 'STATE_NAMES'
_CDC_COVID_DEATHS = 'CDC_COVID_DEATHS'

@app.route('/', methods=['POST'])
def ingest_data():
  """Main function for data ingestion. Receives Pub/Sub trigger and triages to the
     appropriate data ingestion workflow.
     
     Returns 400 for a bad request or 204 for success."""

  envelope = request.get_json()
  if not envelope:
    logging.error('No Pub/Sub message received.')
    return ('', 400)

  if not isinstance(envelope, dict) or 'message' not in envelope:
    logging.error('Invalid Pub/Sub message format')
    return ('', 400)

  data = envelope['message']
  logging.info(f"message: {data}")

  try:
    if 'data' not in data:
      logging.warning("PubSub message missing 'data' field")
      return ('', 400)
    data = base64.b64decode(data['data']).decode('utf-8')
    event_dict = json.loads(data)
  except json.JSONDecodeError as err:
    logging.error("Could not load json object: %s", err)
    return ('', 400)

  if 'id' not in event_dict:
    logging.error(f"PubSub data missing 'id' field: {event_dict}")
    return ('', 400)
  if 'url' not in event_dict or 'gcs_bucket' not in event_dict or 'filename' not in event_dict:
    logging.error("Pubsub data must contain fields 'url', 'gcs_bucket', and 'filename'")
    return ('', 400)
    
  id = event_dict['id']
  url = event_dict['url']
  gcs_bucket = event_dict['gcs_bucket']
  filename = event_dict['filename']

  if 'PROJECT_ID' not in os.environ:
    logging.error("Environment variable PROJECT_ID missing.")
    return ('', 400)
  if 'NOTIFY_DATA_INGESTED_TOPIC' not in os.environ:
    logging.error("Environment variable NOTIFY_DATA_INGESTED_TOPIC missing.")
    return ('', 400)

  project_id = os.environ['PROJECT_ID']
  notify_data_ingested_topic = os.environ['NOTIFY_DATA_INGESTED_TOPIC']

  logging.info(f'Ingesting {id} data')
  if id == _HOUSEHOLD_INCOME:
    upload_household_income(url, gcs_bucket, filename)
  elif id == _STATE_NAMES:
    upload_state_names(url, gcs_bucket, filename)
  elif id == _URGENT_CARE_FACILITIES or id == _CDC_COVID_DEATHS:
    url_file_to_gcs(url, None, gcs_bucket, filename)
  else: 
    logging.warning("ID: %s, is not a valid id", id)
    return ('', 400)

  notify_data_ingested(
      project_id, notify_data_ingested_topic, id, gcs_bucket, filename)  
  return ('', 204)

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
