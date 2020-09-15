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
}

/*
 * [END] GCS Resources
 */

/* [BEGIN] Test File Upload
 * This is just adding temporary files for testing the SQL queries.
 * These should be removed when the pipelines for adding these files are copmleted,
 * and the SQL queries should point to those.
 */

resource "google_storage_bucket_object" "file_pdccr" {
 name                     = "Provisional_COVID-19_Death_Counts_by_County_and_Race.csv"
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