# GCF Environment Variables:
# FILE_URL = URL of CSV to download.
# GCS_UPLOAD_TO_BUCKET = Bucket to upload to (without gs://).
# DESTINATION_FILENAME = What to name the downloaded file in GCS.
#                        Include the file extension.

from google.cloud import storage
import io, os
import wget

file_url = os.environ['FILE_URL']
upload_bucket_name = os.environ['GCS_UPLOAD_TO_BUCKET']
destination_blob_name = os.environ['DESTINATION_FILENAME']
storage_client = storage.Client()

local_file_path = '/tmp/{}'.format(destination_blob_name)

def gcf_1_di_url_file_to_gcs(event, context):
  wget.download(file_url, local_file_path)
  bucket = storage_client.get_bucket(upload_bucket_name)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_filename(local_file_path)
  os.remove(local_file_path)