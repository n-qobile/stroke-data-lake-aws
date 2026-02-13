# ============================================================================
# Terraform Outputs - Important Resource Information
# ============================================================================

# ============================================================================
# S3 BUCKET OUTPUTS
# ============================================================================

output "raw_data_bucket_name" {
  description = "Name of the raw data S3 bucket"
  value       = aws_s3_bucket.raw_data.id
}

output "raw_data_bucket_arn" {
  description = "ARN of the raw data S3 bucket"
  value       = aws_s3_bucket.raw_data.arn
}

output "processed_data_bucket_name" {
  description = "Name of the processed data S3 bucket"
  value       = aws_s3_bucket.processed_data.id
}

output "processed_data_bucket_arn" {
  description = "ARN of the processed data S3 bucket"
  value       = aws_s3_bucket.processed_data.arn
}

output "athena_results_bucket_name" {
  description = "Name of the Athena results S3 bucket"
  value       = aws_s3_bucket.athena_results.id
}

output "athena_results_bucket_arn" {
  description = "ARN of the Athena results S3 bucket"
  value       = aws_s3_bucket.athena_results.arn
}

# ============================================================================
# GLUE OUTPUTS
# ============================================================================

output "glue_database_name" {
  description = "Name of the Glue catalog database"
  value       = aws_glue_catalog_database.stroke_analytics.name
}

output "glue_raw_crawler_name" {
  description = "Name of the Glue crawler for raw data"
  value       = aws_glue_crawler.raw_data_crawler.name
}

output "glue_processed_crawler_name" {
  description = "Name of the Glue crawler for processed data"
  value       = aws_glue_crawler.processed_data_crawler.name
}

output "glue_etl_job_name" {
  description = "Name of the Glue ETL job"
  value       = aws_glue_job.stroke_etl.name
}

# ============================================================================
# ATHENA OUTPUTS
# ============================================================================

output "athena_workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.stroke_analytics.name
}

output "athena_workgroup_state" {
  description = "State of the Athena workgroup"
  value       = aws_athena_workgroup.stroke_analytics.state
}

# ============================================================================
# IAM ROLE OUTPUTS
# ============================================================================

output "glue_service_role_arn" {
  description = "ARN of the Glue service role"
  value       = aws_iam_role.glue_service_role.arn
}

output "athena_execution_role_arn" {
  description = "ARN of the Athena execution role"
  value       = aws_iam_role.athena_execution_role.arn
}

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

# ============================================================================
# CONVENIENT QUICK REFERENCE
# ============================================================================

output "quick_reference" {
  description = "Quick reference guide for next steps"
  value = {
    upload_data_command = "aws s3 cp data/raw/healthcare-dataset-stroke-data.csv s3://${aws_s3_bucket.raw_data.id}/"
    run_raw_crawler     = "aws glue start-crawler --name ${aws_glue_crawler.raw_data_crawler.name}"
    run_etl_job         = "aws glue start-job-run --job-name ${aws_glue_job.stroke_etl.name}"
    run_processed_crawler = "aws glue start-crawler --name ${aws_glue_crawler.processed_data_crawler.name}"
    athena_console_url  = "https://${data.aws_region.current.name}.console.aws.amazon.com/athena/home?region=${data.aws_region.current.name}#/query-editor"
    glue_console_url    = "https://${data.aws_region.current.name}.console.aws.amazon.com/glue/home?region=${data.aws_region.current.name}"
  }
}

# ============================================================================
# PROJECT SUMMARY
# ============================================================================

output "project_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    project_name    = var.project_name
    environment     = var.environment
    aws_region      = data.aws_region.current.name
    aws_account_id  = data.aws_caller_identity.current.account_id
    glue_database   = aws_glue_catalog_database.stroke_analytics.name
    athena_workgroup = aws_athena_workgroup.stroke_analytics.name
  }
}
