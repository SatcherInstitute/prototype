variable "project_id" {
  description   = "Google Project ID"
  type          = string
}

variable "code_path" {
  description   = "Absolute path to where the code lives"
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

variable "gcs_code_bucket" {
  description   = "Name of the GCS bucket housing your code"
  type          = string
}

variable "bq_dataset_name" {
  description   = "Name of the landing BigQuery Dataset"
  type          = string
}

variable "bq_table_name" {
  description   = "Name of the landing BigQuery Table"
  type          = string
}

variable "gcf_name_1" {
  description   = "Name of GCF 1"
  type          = string
}

variable "gcf_name_2" {
  description   = "Name of GCF 2"
  type          = string
}

variable "pubsub_trigger_topic_name" {
  description   = "Pub/Sub topic to trigger the first GCF"
  type          = string
}

variable "scheduler_job_name" {
  description   = "The Cloud Scheduler Job that kicks off a Pub/Sub message"
  type          = string
}