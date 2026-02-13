# ============================================================================
# IAM Roles and Policies - Least Privilege Access Control
# ============================================================================

# ============================================================================
# AWS GLUE SERVICE ROLE
# ============================================================================

# Trust policy for Glue to assume role
data "aws_iam_policy_document" "glue_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Glue service role
resource "aws_iam_role" "glue_service_role" {
  name               = "${var.project_name}-glue-service-role"
  assume_role_policy = data.aws_iam_policy_document.glue_assume_role.json

  tags = {
    Name        = "Glue Service Role"
    Description = "IAM role for Glue crawlers and ETL jobs"
  }
}

# Attach AWS managed policy for Glue
resource "aws_iam_role_policy_attachment" "glue_service_policy" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Custom policy for S3 access
data "aws_iam_policy_document" "glue_s3_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/*",
      "${aws_s3_bucket.processed_data.arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation"
    ]

    resources = [
      aws_s3_bucket.raw_data.arn,
      aws_s3_bucket.processed_data.arn
    ]
  }
}

resource "aws_iam_policy" "glue_s3_policy" {
  name        = "${var.project_name}-glue-s3-policy"
  description = "S3 access policy for Glue crawlers and jobs"
  policy      = data.aws_iam_policy_document.glue_s3_access.json
}

resource "aws_iam_role_policy_attachment" "glue_s3_attachment" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.glue_s3_policy.arn
}

# ============================================================================
# ATHENA WORKGROUP ROLE (for query execution)
# ============================================================================

# Trust policy for Athena
data "aws_iam_policy_document" "athena_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["athena.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Athena execution role
resource "aws_iam_role" "athena_execution_role" {
  name               = "${var.project_name}-athena-execution-role"
  assume_role_policy = data.aws_iam_policy_document.athena_assume_role.json

  tags = {
    Name        = "Athena Execution Role"
    Description = "IAM role for Athena query execution"
  }
}

# Athena S3 access policy
data "aws_iam_policy_document" "athena_s3_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/*",
      "${aws_s3_bucket.processed_data.arn}/*",
      aws_s3_bucket.raw_data.arn,
      aws_s3_bucket.processed_data.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]

    resources = [
      "${aws_s3_bucket.athena_results.arn}/*",
      aws_s3_bucket.athena_results.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "glue:GetDatabase",
      "glue:GetTable",
      "glue:GetPartitions"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "athena_s3_policy" {
  name        = "${var.project_name}-athena-s3-policy"
  description = "S3 and Glue access policy for Athena"
  policy      = data.aws_iam_policy_document.athena_s3_access.json
}

resource "aws_iam_role_policy_attachment" "athena_s3_attachment" {
  role       = aws_iam_role.athena_execution_role.name
  policy_arn = aws_iam_policy.athena_s3_policy.arn
}

# ============================================================================
# LAMBDA EXECUTION ROLE (for ETL transformations)
# ============================================================================

# Trust policy for Lambda
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Lambda execution role
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.project_name}-lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Name        = "Lambda Execution Role"
    Description = "IAM role for Lambda ETL functions"
  }
}

# Attach AWS managed policy for Lambda basic execution
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda S3 access policy
data "aws_iam_policy_document" "lambda_s3_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/*",
      "${aws_s3_bucket.processed_data.arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.raw_data.arn,
      aws_s3_bucket.processed_data.arn
    ]
  }
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "${var.project_name}-lambda-s3-policy"
  description = "S3 access policy for Lambda ETL functions"
  policy      = data.aws_iam_policy_document.lambda_s3_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# ============================================================================
# USER/ANALYST POLICY (for console/CLI access)
# ============================================================================

# Policy for data analysts to query via Athena
data "aws_iam_policy_document" "analyst_access" {
  statement {
    sid    = "AthenaQueryAccess"
    effect = "Allow"

    actions = [
      "athena:StartQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:StopQueryExecution",
      "athena:GetWorkGroup",
      "athena:ListWorkGroups"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "GlueCatalogReadAccess"
    effect = "Allow"

    actions = [
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:GetPartition",
      "glue:GetPartitions"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "S3ReadAccess"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/*",
      "${aws_s3_bucket.processed_data.arn}/*",
      aws_s3_bucket.raw_data.arn,
      aws_s3_bucket.processed_data.arn
    ]
  }

  statement {
    sid    = "S3QueryResultsAccess"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]

    resources = [
      "${aws_s3_bucket.athena_results.arn}/*",
      aws_s3_bucket.athena_results.arn
    ]
  }
}

resource "aws_iam_policy" "analyst_policy" {
  name        = "${var.project_name}-analyst-policy"
  description = "Policy for data analysts to query stroke data via Athena"
  policy      = data.aws_iam_policy_document.analyst_access.json

  tags = {
    Name        = "Analyst Access Policy"
    Description = "Read-only access to query data via Athena"
  }
}
