variable "project_id" {
  description   = "Google Project ID"
  type          = string
}

variable "compute_region" {
  description   = "Region for Compute Resources"
  type          = string
  default       = "us-central1"
}

variable "gcs_landing_bucket" {
  description   = "Name of the landing GCS bucket"
  type          = string
}

variable "gcs_region" {
  description   = "Region for Google Cloud Storage"
  type          = string
  default       = "US"
}

variable "bq_dataset_name" {
  description   = "BigQuery Main Dataset"
  type          = string
}

