variable "project_id" {
  description   = "Google Project ID"
  type          = string
}

variable "compute_region" {
  description   = "Region for Compute Resources"
  type          = string
  default       = "us-central1"
}