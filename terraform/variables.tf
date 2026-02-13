# ============================================================================
# Terraform Variables - Stroke Data Lake Project
# ============================================================================

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "stroke-data-lake"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "056563840644"
}

# S3 Configuration
variable "raw_data_bucket_suffix" {
  description = "Suffix for raw data bucket name"
  type        = string
  default     = "raw-data"
}

variable "processed_data_bucket_suffix" {
  description = "Suffix for processed data bucket name"
  type        = string
  default     = "processed-data"
}

variable "athena_results_bucket_suffix" {
  description = "Suffix for Athena query results bucket"
  type        = string
  default     = "athena-results"
}

# Glue Configuration
variable "glue_database_name" {
  description = "Name of the Glue database"
  type        = string
  default     = "stroke_analytics_db"
}

variable "glue_crawler_schedule" {
  description = "Cron schedule for Glue crawler (leave empty for on-demand only)"
  type        = string
  default     = "" # Run manually for free tier optimization
}

# Data Classification
variable "data_classification" {
  description = "Data classification level"
  type        = string
  default     = "Confidential"
}

# Cost Optimization
variable "s3_lifecycle_transition_days" {
  description = "Days before transitioning to Intelligent-Tiering"
  type        = number
  default     = 90
}

variable "s3_lifecycle_expiration_days" {
  description = "Days before expiring old query results"
  type        = number
  default     = 365
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default = {
    CostCenter = "DataEngineering"
    Compliance = "HealthcareData"
  }
}
