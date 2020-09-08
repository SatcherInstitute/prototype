# This file contains code for downloading a file from a url and uploading
# it to a GCS bucket.

# GCF Environment Variables:
# FILE_URL = URL of CSV to download.
# GCS_UPLOAD_TO_BUCKET = Bucket to upload to (without gs://).
# DESTINATION_FILENAME = What to name the downloaded file in GCS.
#                        Include the file extension.

from google.cloud import storage
import google.cloud.exceptions
import io, os
import logging
import requests

file_url = os.environ['FILE_URL']
upload_bucket_name = os.environ['GCS_UPLOAD_TO_BUCKET']
destination_blob_name = os.environ['DESTINATION_FILENAME']
storage_client = storage.Client()

local_file_path = '/tmp/{}'.format(destination_blob_name)

def gcf_di_url_file_to_gcs(event, context):
  try:
    with requests.get(file_url) as response, open(local_file_path, 'wb') as f:
      response.raise_for_status()
      f.write(response.content)
    bucket = storage_client.get_bucket(upload_bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    os.remove(local_file_path)
  except requests.HTTPError as e:
    logging.error("HTTP error for url {}: {}".format(file_url, e))
  except google.cloud.exceptions.NotFound:
    logging.error("GCS Bucket {} not found".format(upload_bucket_name))
    