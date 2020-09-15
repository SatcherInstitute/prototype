# Specify the provider, here
provider "google" {
  project                 = var.project_id
  region                  = var.compute_region
}

# [BEGIN] GCS Resources

# Raw data landing zone for data ingestion
resource "google_storage_bucket" "gcs_data_ingestion_landing_bucket" {
  name                    = var.gcs_landing_bucket
  location                = var.gcs_region
  force_destroy           = true # This forces deletion of objects created in bucket post provisioning
}

# [END] GCS Resources