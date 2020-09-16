# Specify the provider, here
provider "google" {
  project                 = var.project_id
  region                  = var.compute_region
}

/* 
 * [BEGIN] GCS Resources
 */

# Raw data landing zone for data ingestion
resource "google_storage_bucket" "gcs_data_ingestion_landing_bucket" {
  name                    = var.gcs_landing_bucket
  location                = var.gcs_region
  force_destroy           = true # This forces deletion of objects created in bucket post provisioning
    # https://www.terraform.io/docs/providers/google/r/storage_bucket.html#force_destroy
}

/*
 * [END] GCS Resources
 */

/* 
 * [BEGIN] Test File Upload
 * This is just adding temporary files for testing the SQL queries.
 * These should be removed when the pipelines for adding these files are copmleted,
 * and the SQL queries should point to those.
 */

resource "google_storage_bucket_object" "file_pdccr" {
 name                     = "covid_19_pdccr.csv"
 bucket                   = google_storage_bucket.gcs_data_ingestion_landing_bucket.name
 source                   = "./testing_data_files/Provisional_COVID-19_Death_Counts_by_County_and_Race.csv"
}

resource "google_storage_bucket_object" "file_ucf" {
 name                     = "Urgent_Care_Facilities.csv"
 bucket                   = google_storage_bucket.gcs_data_ingestion_landing_bucket.name
 source                   = "./testing_data_files/Urgent_Care_Facilities.csv"
}

/*
 * [END] Test File Upload
 */

 /*
  * [BEGIN] BigQuery Setup
  */

# Create a BigQuery dataset
resource "google_bigquery_dataset" "bq_dataset" {
  dataset_id              = var.bq_dataset_name
  location                = "US"
}

/*
 * [BEGIN] Table Creation
 * Manually create tables for pdccr and ucf for testing. Much like the CSV files, these
 * are just temporary loads until they are dynamically loaded in by the ingest pipelines.
 */

# PDCCR table
resource "google_bigquery_table" "bq_table_pdccr" {
  dataset_id = google_bigquery_dataset.bq_dataset.dataset_id
  table_id   = "cdc_pdccr"
}

# PDCCR load
resource "google_bigquery_job" "bq_job_load_pdccr" {
  job_id     = "pdccr_load${formatdate("YYYYMMDDhhmmss",timestamp())}"

  load {
    source_uris = [
      "gs://${var.gcs_landing_bucket}/covid_19_pdccr.csv",
    ]

    destination_table {
      project_id = google_bigquery_table.bq_table_pdccr.project
      dataset_id = google_bigquery_table.bq_table_pdccr.dataset_id
      table_id   = google_bigquery_table.bq_table_pdccr.table_id
    }

    skip_leading_rows = 1

    write_disposition = "WRITE_TRUNCATE"
    autodetect = true
  }
}

# UCF table
resource "google_bigquery_table" "bq_table_ucf" {
  dataset_id = google_bigquery_dataset.bq_dataset.dataset_id
  table_id   = "ucf"
}

# UCF load
resource "google_bigquery_job" "bq_job_load_ucf" {
  job_id     = "ucf_load${formatdate("YYYYMMDDhhmmss",timestamp())}"

  load {
    source_uris = [
      "gs://${var.gcs_landing_bucket}/Urgent_Care_Facilities.csv",
    ]

    destination_table {
      project_id = google_bigquery_table.bq_table_ucf.project
      dataset_id = google_bigquery_table.bq_table_ucf.dataset_id
      table_id   = google_bigquery_table.bq_table_ucf.table_id
    }

    skip_leading_rows = 1

    write_disposition = "WRITE_TRUNCATE"
    autodetect = true
  }
}

/*
 * [END] Table Creation
 */

resource "google_bigquery_table" "bqt_pdccr_ucf_joined" {
  dataset_id = google_bigquery_dataset.bq_dataset.dataset_id
  table_id   = "pdccr_ucf_joined"

  labels = {
    "derived-table" = "yes"
  }
}
# Use the ./sql/pdccr.sql file
resource "google_bigquery_job" "bq_job_pdccr_ucf_joined" {
  depends_on = [google_bigquery_job.bq_job_load_pdccr, google_bigquery_job.bq_job_load_ucf]
  job_id     = "pdccrucfjoin${formatdate("YYYYMMDDhhmmss",timestamp())}"

  query {
    query = file("./sql/pdccr.sql")

    destination_table {
      table_id = google_bigquery_table.bqt_pdccr_ucf_joined.id
    }

    allow_large_results = true
  }
}

/*
 * [END] BigQuery Setup
 */