# This file contains code for downloading a file from a url and uploading
# it to a GCS bucket.

from google.cloud import storage
import google.cloud.exceptions
import io, os
import logging
import requests


def local_file_path(filename):
  return '/tmp/{}'.format(filename)


def url_file_to_gcs(url, url_params, gcs_bucket, dest_filename):
  """Downloads a file from a url and uploads as a blob to the given GCS bucket.

     url: The URL of the file to download.
     url_params: URL parameters to be passed to requests.get().
     gcs_bucket: Name of the GCS bucket to upload to (without gs://).
     dest_filename: What to name the downloaded file in GCS. Include the file extension."""
  try:
    local_path = local_file_path(dest_filename)
    with requests.get(url, params=url_params) as response, open(local_path, 'wb') as f:
      response.raise_for_status()
      f.write(response.content)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(gcs_bucket)
    blob = bucket.blob(dest_filename)
    blob.upload_from_filename(local_path)
    os.remove(local_file_path)
  except requests.HTTPError as e:
    logging.error("HTTP error for url {}: {}".format(url, e))
  except google.cloud.exceptions.NotFound:
    logging.error("GCS Bucket {} not found".format(gcs_bucket))
    