import base64
import json
import logging
import os
import common.census as census
from common.primary_care_access import upload_primary_care_access
from common.pubsub_publisher import notify_topic
from common.di_url_file_to_gcs import url_file_to_gcs

# Data source name literals. These correspond to a specific data ingestion workflow.
_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_URGENT_CARE_FACILITIES = 'URGENT_CARE_FACILITIES'
_STATE_NAMES = 'STATE_NAMES'
_COUNTY_NAMES = 'COUNTY_NAMES'
_COUNTY_ADJACENCY = 'COUNTY_ADJACENCY'
_POPULATION_BY_RACE = 'POPULATION_BY_RACE'
_PRIMARY_CARE_ACCESS = 'PRIMARY_CARE_ACCESS'


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
    return

  if 'id' not in event_dict or 'gcs_bucket' not in event_dict:
    logging.error("PubSub data missing 'id' or 'gcs_bucket' field")
    return
  workflow_id = event_dict['id']
  gcs_bucket = event_dict['gcs_bucket']
  logging.info("Data ingestion recieved message: %s", workflow_id)

  if 'PROJECT_ID' not in os.environ:
    logging.error("Environment variable PROJECT_ID missing.")
    return
  if 'NOTIFY_DATA_INGESTED_TOPIC' not in os.environ:
    logging.error("Environment variable NOTIFY_DATA_INGESTED_TOPIC missing.")
    return

  project_id = os.environ['PROJECT_ID']
  notify_data_ingested_topic = os.environ['NOTIFY_DATA_INGESTED_TOPIC']

  if workflow_id == _HOUSEHOLD_INCOME:
    if 'url' not in event_dict or 'filename' not in event_dict:
      logging.error("Pubsub data must contain fields 'url' and 'filename'")
      return
    census.upload_household_income(event_dict['url'], gcs_bucket, event_dict['filename'])
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, filename=event_dict['filename'])
  elif workflow_id == _COUNTY_NAMES:
    if 'url' not in event_dict or 'filename' not in event_dict:
      logging.error("Pubsub data must contain fields 'url' and 'filename'")
      return
    census.upload_county_names(event_dict['url'], gcs_bucket, event_dict['filename'])
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, filename=event_dict['filename'])
  elif workflow_id == _STATE_NAMES:
    if 'url' not in event_dict or 'filename' not in event_dict:
      logging.error("Pubsub data must contain fields 'url' and 'filename'")
      return
    census.upload_state_names(event_dict['url'], gcs_bucket, event_dict['filename'])
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, filename=event_dict['filename'])
  elif workflow_id == _POPULATION_BY_RACE:
    if 'url' not in event_dict or 'filename' not in event_dict:
      logging.error("Pubsub data must contain fields 'url' and 'filename'")
      return
    census.upload_population_by_race(event_dict['url'], gcs_bucket, event_dict['filename'])
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, filename=event_dict['filename'])
  elif workflow_id == _URGENT_CARE_FACILITIES or id == _COUNTY_ADJACENCY:
    if 'url' not in event_dict or 'filename' not in event_dict:
      logging.error("Pubsub data must contain fields 'url' and 'filename'")
      return
    url_file_to_gcs(event_dict['url'], None, gcs_bucket, event_dict['filename'])
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, filename=event_dict['filename'])
  elif workflow_id == _PRIMARY_CARE_ACCESS:
    if 'fileprefix' not in event_dict:
      logging.error("Pubsub data must contain field 'fileprefix'")
      return
    upload_primary_care_access(gcs_bucket, event_dict['fileprefix']);
    notify_topic(project_id, notify_data_ingested_topic, id=workflow_id, gcs_bucket=gcs_bucket, fileprefix=event_dict['fileprefix'])
  else: 
    logging.warning("ID: %s, is not a valid id", workflow_id)
