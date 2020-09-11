# Specify the provider, here
provider "google" {
  project                 = var.project_id
  region                  = var.compute_region
}

# [BEGIN] GCS Resources

# Raw data landing zone for data integration
resource "google_storage_bucket" "gcs_di_landing" {
  name                    = var.gcs_landing_bucket
  location                = var.gcs_region
  force_destroy           = true # This forces deletion of objects created in bucket post provisioning
}

# Create a BigQuery dataset
resource "google_bigquery_dataset" "bq_ingest_dataset" {
  dataset_id              = var.bq_dataset_name
  location                = "US"
}

# Create a BigQuery table
resource "google_bigquery_table" "bq_ingest_table"{
  dataset_id              = google_bigquery_dataset.bq_ingest_dataset.dataset_id
  table_id                = var.bq_table_name

  time_partitioning {
    type = "HOUR"
  }

  schema = <<EOF
    [
      {"name":"date","type":"DATE","mode":"NULLABLE"},
      {"name":"county","type":"STRING","mode":"NULLABLE"},
      {"name":"state","type":"STRING","mode":"NULLABLE"},
      {"name":"fips","type":"INTEGER","mode":"NULLABLE"},
      {"name":"cases","type":"INTEGER","mode":"NULLABLE"},
      {"name":"deaths","type":"INTEGER","mode":"NULLABLE"},
      {"name":"confirmed_cases","type":"INTEGER","mode":"NULLABLE"},
      {"name":"confirmed_deaths","type":"INTEGER","mode":"NULLABLE"},
      {"name":"probable_cases","type":"INTEGER","mode":"NULLABLE"},
      {"name":"probable_deaths","type":"INTEGER","mode":"NULLABLE"}
    ]
  EOF
}

## [BEGIN] GCF CREATION
## To create a GCF, three things need to happen. Zip up the
## code locally, upload it to a bucket, then create the
## function off of that.

# Create a ZIP of gcf_1_di_url_file_to_gcs
data "archive_file" "gcf_1_di_url_file_to_gcs" {
 type                     = "zip"
 source_dir               = "${var.code_path}/gcf_1_di_url_file_to_gcs/"
 output_path              = "${var.code_path}/gcf_1_di_url_file_to_gcs.zip"
}

# Create a ZIP of gcf_2_di_gcs_csv_to_bq
data "archive_file" "gcf_2_di_gcs_csv_to_bq" {
 type                     = "zip"
 source_dir               = "${var.code_path}/gcf_2_di_gcs_csv_to_bq/"
 output_path              = "${var.code_path}/gcf_2_di_gcs_csv_to_bq.zip"
}

# Bucket for storing your GCF code
resource "google_storage_bucket" "gcs_code" {
  name                    = var.gcs_code_bucket
  location                = var.gcs_region
}

# Place the ZIP files into your shiny new bucket
resource "google_storage_bucket_object" "gcf_1_di_url_file_to_gcs" {
 name                     = "gcf_1_di_url_file_to_gcs.zip"
 bucket                   = google_storage_bucket.gcs_code.name
 source                   = "${var.code_path}/gcf_1_di_url_file_to_gcs.zip"
}
resource "google_storage_bucket_object" "gcf_2_di_gcs_csv_to_bq" {
 name   = "gcf_2_di_gcs_csv_to_bq.zip"
 bucket                   = google_storage_bucket.gcs_code.name
 source                   = "${var.code_path}/gcf_2_di_gcs_csv_to_bq.zip"
}

# Create the functions
resource "google_cloudfunctions_function" "gcf_1_di_url_file_to_gcs" {
 name                     = var.gcf_name_1
 description              = "Pull a CSV from a URL to GCF"
 available_memory_mb      = 256
 source_archive_bucket    = google_storage_bucket.gcs_code.name
 source_archive_object    = google_storage_bucket_object.gcf_1_di_url_file_to_gcs.name
 timeout                  = 60
 entry_point              = "gcf_1_di_url_file_to_gcs"
 runtime                  = "python37"
 event_trigger {
    event_type            = "google.pubsub.topic.publish"
    resource              = google_pubsub_topic.pubsub_trigger.name
  }
  # TODO: These are hard coded now, but need to be dynamic from the Pub/sub 
  # message at some point.
  environment_variables = {
    FILE_URL              = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv"
    GCS_UPLOAD_TO_BUCKET  = google_storage_bucket.gcs_di_landing.name
    DESTINATION_FILENAME  = "nyt_us-counties.csv"
  }
}

resource "google_cloudfunctions_function" "gcf_2_di_gcs_csv_to_bq" {
 name                     = var.gcf_name_2
 description              = "Upload the CSV to BQ"
 available_memory_mb      = 256
 source_archive_bucket    = google_storage_bucket.gcs_code.name
 source_archive_object    = google_storage_bucket_object.gcf_2_di_gcs_csv_to_bq.name
 timeout                  = 60
 entry_point              = "gcf_2_di_gcs_csv_to_bq"
 runtime                  = "python37"
 event_trigger {
    event_type            = "google.storage.object.finalize"
    resource              = google_storage_bucket.gcs_di_landing.name
  }
  # TODO: These are hard coded now, but need to be dynamic from the Pub/sub 
  # message at some point.
  environment_variables = {
    DATASET               = "${var.bq_dataset_name}"
    TABLE                 = "${var.bq_table_name}"
  }
}

## [END] GCF CREATION

# Create a Pub/Sub topic to trigger gcf_1_di_url_file_to_gcs
resource "google_pubsub_topic" "pubsub_trigger" {
  name                    = var.pubsub_trigger_topic_name
}

# Create a Cloud Scheduler task to trigger the Pub/Sub event
resource "google_cloud_scheduler_job" "scheduler_job" {
  name                    = var.scheduler_job_name
  description             = "Hello World test job every six hours"
  time_zone               = "America/New_York"
  schedule                = "0 */6 * * *"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name            = "projects/${var.project_id}/topics/${var.pubsub_trigger_topic_name}"
    data                  = base64encode("Hello, World")
  }
}

# [END] GCS RESOURCES