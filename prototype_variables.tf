variable "project_id" {
  description = "Google Project ID"
  type        = string
}

variable "compute_region" {
  description = "Region for Compute Resources"
  type        = string
  default     = "us-central1"
}

variable "gcs_landing_bucket" {
  description = "Name of the landing GCS bucket"
  type        = string
}

variable "gcs_region" {
  description = "Region for Google Cloud Storage"
  type        = string
  default     = "US"
}

variable "bq_dataset_name" {
  description = "BigQuery Main Dataset"
  type        = string
}

variable "gcf_code_path" {
  description = "Base path where the Cloud Functions code lives"
  type        = string
}

variable "gcf_code_bucket" {
  description = "Name of the bucket where the GCF code is kept"
  type        = string
}

variable "upload_to_gcs_topic_name" {
  description = "Name of the Pub/Sub topic used to trigger uploading files to GCS"
  type        = string
}

variable "gcf_upload_to_gcs_name" {
  description = "Name of the GCF function which uploads files to GCS"
  type        = string
}

variable "household_income_scheduler_name" {
  description = "Name of the Cloud Scheduler job for downloading household income data"
  type        = string
}

variable "run_ingestion_service_name" {
  description = "Name of the Cloud Run service for data ingestion"
  type        = string
}

variable "run_ingestion_image_path" {
  description = "Path to container image for the Cloud Run ingestion service"
  type        = string
}

variable "ingestion_invoker_identity_id" {
  description = "Account id of the service account used to trigger data ingestion"
  type        = string
}

variable "ingestion_subscription_name" {
  description = "Name of push subscription that invokes the ingestion service"
  type        = string
}

variable "ingestion_runner_identity_id" {
  description = "Account id of the service account used when running the data ingestion service"
  type        = string
}

variable "project_number" {
  description = "Google project number"
  type        = number
}

variable "ingestion_runner_role_id" {
  description = "Id of custom role given to the ingestion runner service account"
  type        = string
}