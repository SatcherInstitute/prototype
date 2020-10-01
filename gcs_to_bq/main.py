import base64
import json
import logging
import os
import common.census_to_bq as census_to_bq
from common.county_adjacency import write_adjacencies_to_bq
from common.primary_care_access_to_bq import write_primary_care_access_to_bq


_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_STATE_NAMES = 'STATE_NAMES'
_COUNTY_NAMES = 'COUNTY_NAMES'
_COUNTY_ADJACENCY = 'COUNTY_ADJACENCY'
_POPULATION_BY_RACE = 'POPULATION_BY_RACE'
_PRIMARY_CARE_ACCESS = 'PRIMARY_CARE_ACCESS'


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
      or 'gcs_bucket' not in attributes):
    logging.error(
        "Pubsub attributes must contain 'id' and 'gcs_bucket'")
    return
  id = attributes['id']
  gcs_bucket = attributes['gcs_bucket']

  if 'DATASET_NAME' not in os.environ:
    logging.error("Environment variable DATASET_NAME missing.")
    return

  dataset = os.environ['DATASET_NAME']

  if id == _HOUSEHOLD_INCOME:
    # TODO implement
    pass
  elif id == _STATE_NAMES:
    census_to_bq.write_state_names_to_bq(
        dataset, 'state_names', gcs_bucket, attributes['filename'])
  elif id == _COUNTY_NAMES:
    census_to_bq.write_county_names_to_bq(
        dataset, 'county_names', gcs_bucket, attributes['filename'])
  elif id == _COUNTY_ADJACENCY:
    write_adjacencies_to_bq(
        dataset, 'county_adjacency', gcs_bucket, attributes['filename'])
  elif id == _POPULATION_BY_RACE:
    census_to_bq.write_population_by_race_to_bq(
        dataset, 'population_by_race', gcs_bucket, attributes['filename'])
  elif id == _PRIMARY_CARE_ACCESS:
    write_primary_care_access_to_bq(dataset, 'primary_care_access', gcs_bucket, attributes['fileprefix'])
  else: 
    logging.warning("ID: %s, is not a valid id", id)
