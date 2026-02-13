# ============================================================================
# AWS Glue - Data Catalog and ETL
# ============================================================================

# ============================================================================
# GLUE DATABASE
# ============================================================================

resource "aws_glue_catalog_database" "stroke_analytics" {
  name        = var.glue_database_name
  description = "Database for stroke risk analysis and healthcare data"

  tags = {
    Name        = "Stroke Analytics Database"
    Description = "Glue catalog database for stroke prediction datasets"
  }
}

# ============================================================================
# GLUE CRAWLER - Raw Data Discovery
# ============================================================================

resource "aws_glue_crawler" "raw_data_crawler" {
  name          = "${var.project_name}-raw-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.stroke_analytics.name
  description   = "Crawler to discover schema of raw stroke data"

  s3_target {
    path = "s3://${aws_s3_bucket.raw_data.bucket}/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = {
    Name        = "Raw Data Crawler"
    Description = "Discovers and catalogs raw CSV files from S3"
    Layer       = "Bronze"
  }
}

# ============================================================================
# GLUE CRAWLER - Processed Data Discovery
# ============================================================================

resource "aws_glue_crawler" "processed_data_crawler" {
  name          = "${var.project_name}-processed-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.stroke_analytics.name
  description   = "Crawler to discover schema of processed stroke data"

  s3_target {
    path = "s3://${aws_s3_bucket.processed_data.bucket}/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = {
    Name        = "Processed Data Crawler"
    Description = "Discovers and catalogs cleaned/transformed data"
    Layer       = "Silver"
  }
}

# ============================================================================
# GLUE ETL JOB - Data Transformation (Python Shell)
# ============================================================================

# Store the ETL script in S3
resource "aws_s3_object" "glue_etl_script" {
  bucket = aws_s3_bucket.processed_data.bucket
  key    = "scripts/stroke_data_transform.py"
  
  content = <<-EOT
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_BUCKET', 'TARGET_BUCKET'])
job.init(args['JOB_NAME'], args)

source_bucket = args['SOURCE_BUCKET']
target_bucket = args['TARGET_BUCKET']

print(f"Starting ETL job: {args['JOB_NAME']}")
print(f"Source: s3://{source_bucket}/")
print(f"Target: s3://{target_bucket}/")

# Read raw data from S3
print("Reading raw data...")
df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"s3://{source_bucket}/healthcare-dataset-stroke-data.csv")

print(f"Initial record count: {df.count()}")
print("Initial schema:")
df.printSchema()

# Data Quality Checks and Transformations
print("Applying transformations...")

# 1. Remove duplicates
df = df.dropDuplicates(['id'])

# 2. Handle missing values in BMI (replace with median)
bmi_median = df.approxQuantile("bmi", [0.5], 0.01)[0]
df = df.fillna({'bmi': bmi_median})

# 3. Create age groups for analysis
df = df.withColumn('age_group', 
    when(col('age') < 30, '18-29')
    .when(col('age') < 45, '30-44')
    .when(col('age') < 60, '45-59')
    .when(col('age') < 75, '60-74')
    .otherwise('75+'))

# 4. Create BMI categories (WHO classification)
df = df.withColumn('bmi_category',
    when(col('bmi') < 18.5, 'Underweight')
    .when(col('bmi') < 25, 'Normal')
    .when(col('bmi') < 30, 'Overweight')
    .otherwise('Obese'))

# 5. Create glucose categories
df = df.withColumn('glucose_category',
    when(col('avg_glucose_level') < 100, 'Normal')
    .when(col('avg_glucose_level') < 126, 'Prediabetic')
    .otherwise('Diabetic'))

# 6. Create risk score (simple weighted score)
df = df.withColumn('risk_score',
    (col('age') / 10).cast('int') +
    (col('hypertension') * 2) +
    (col('heart_disease') * 3) +
    when(col('smoking_status') == 'smokes', 2)
    .when(col('smoking_status') == 'formerly smoked', 1)
    .otherwise(0) +
    when(col('bmi') > 30, 2)
    .when(col('bmi') > 25, 1)
    .otherwise(0)
)

# 7. Standardize text fields
df = df.withColumn('gender', upper(col('gender')))
df = df.withColumn('ever_married', upper(col('ever_married')))
df = df.withColumn('work_type', initcap(col('work_type')))
df = df.withColumn('Residence_type', initcap(col('Residence_type')))

# 8. Add processing metadata
df = df.withColumn('processed_date', current_timestamp())
df = df.withColumn('data_source', lit('kaggle_stroke_prediction'))

print(f"Final record count: {df.count()}")
print("Final schema:")
df.printSchema()

# Write transformed data to processed bucket (Parquet format for efficiency)
print("Writing processed data...")
df.write.mode("overwrite").parquet(f"s3://{target_bucket}/stroke_data_processed/")

print("ETL job completed successfully!")

job.commit()
EOT

  tags = {
    Name        = "Glue ETL Script"
    Description = "Python script for stroke data transformation"
  }
}

resource "aws_glue_job" "stroke_etl" {
  name              = "${var.project_name}-etl-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.processed_data.bucket}/${aws_s3_object.glue_etl_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--SOURCE_BUCKET"                    = aws_s3_bucket.raw_data.bucket
    "--TARGET_BUCKET"                    = aws_s3_bucket.processed_data.bucket
  }

  execution_property {
    max_concurrent_runs = 1
  }

  tags = {
    Name        = "Stroke ETL Job"
    Description = "Glue job to clean and transform stroke data"
    Type        = "ETL"
  }
}

# ============================================================================
# CLOUDWATCH LOG GROUP for Glue Job Logs
# ============================================================================

resource "aws_cloudwatch_log_group" "glue_job_logs" {
  name              = "/aws-glue/jobs/${var.project_name}-etl-job"
  retention_in_days = 7

  tags = {
    Name        = "Glue Job Logs"
    Description = "CloudWatch logs for Glue ETL job execution"
  }
}
