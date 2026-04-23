variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "innerchart"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name for the data lake"
  type        = string
  default     = "innerchart-data-lake"
}
