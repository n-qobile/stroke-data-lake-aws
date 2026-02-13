# ============================================================================
# S3 Buckets - Data Lake Storage Layer
# ============================================================================

# Generate unique bucket names to avoid global naming conflicts
locals {
  raw_bucket_name       = "${var.project_name}-${var.raw_data_bucket_suffix}-${var.aws_account_id}"
  processed_bucket_name = "${var.project_name}-${var.processed_data_bucket_suffix}-${var.aws_account_id}"
  athena_bucket_name    = "${var.project_name}-${var.athena_results_bucket_suffix}-${var.aws_account_id}"
}

# ============================================================================
# RAW DATA BUCKET - Landing zone for original datasets
# ============================================================================

resource "aws_s3_bucket" "raw_data" {
  bucket = local.raw_bucket_name

  tags = {
    Name        = "Raw Data Bucket"
    Layer       = "Bronze"
    DataType    = "RawHealthcareData"
    Description = "Original stroke prediction dataset from Kaggle"
  }
}

# Enable versioning for raw data (data protection)
resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Encryption for raw data bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access for raw data
resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for raw data
resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    id     = "transition-to-intelligent-tiering"
    status = "Enabled"

    filter {}

    transition {
      days          = var.s3_lifecycle_transition_days
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

# ============================================================================
# PROCESSED DATA BUCKET - Cleaned and transformed data
# ============================================================================

resource "aws_s3_bucket" "processed_data" {
  bucket = local.processed_bucket_name

  tags = {
    Name        = "Processed Data Bucket"
    Layer       = "Silver"
    DataType    = "CleanedHealthcareData"
    Description = "ETL-processed stroke data with enhanced features"
  }
}

# Enable versioning for processed data
resource "aws_s3_bucket_versioning" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Encryption for processed data bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access for processed data
resource "aws_s3_bucket_public_access_block" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for processed data
resource "aws_s3_bucket_lifecycle_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    id     = "transition-to-intelligent-tiering"
    status = "Enabled"

    filter {}

    transition {
      days          = var.s3_lifecycle_transition_days
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

# ============================================================================
# ATHENA RESULTS BUCKET - Query outputs storage
# ============================================================================

resource "aws_s3_bucket" "athena_results" {
  bucket = local.athena_bucket_name

  tags = {
    Name        = "Athena Query Results"
    Layer       = "QueryResults"
    DataType    = "QueryOutputs"
    Description = "Storage for Athena query results and metadata"
  }
}

# Encryption for Athena results
resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access for Athena results
resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for Athena results (expire old queries)
resource "aws_s3_bucket_lifecycle_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    id     = "expire-old-query-results"
    status = "Enabled"

    filter {}

    expiration {
      days = var.s3_lifecycle_expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
