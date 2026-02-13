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

# Read raw data from S3 with SEMICOLON delimiter (THIS IS THE FIX!)
print("Reading raw data with semicolon delimiter...")
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("sep", ";") \
    .csv(f"s3://{source_bucket}/healthcare-dataset-stroke-data.csv")

print(f"Initial record count: {df.count()}")
print("Initial schema:")
df.printSchema()

# Data Quality Checks and Transformations
print("Applying transformations...")

# 1. Remove duplicates
df = df.dropDuplicates(['id'])
print(f"After dedup: {df.count()} records")

# 2. Handle 'N/A' string in BMI - convert to null then fill with median
df = df.withColumn('bmi', when(col('bmi') == 'N/A', None).otherwise(col('bmi').cast('double')))
bmi_median = df.approxQuantile("bmi", [0.5], 0.01)[0]
print(f"BMI median: {bmi_median}")
df = df.fillna({'bmi': bmi_median})

# 3. Create age groups
df = df.withColumn('age_group', 
    when(col('age') < 30, '18-29')
    .when(col('age') < 45, '30-44')
    .when(col('age') < 60, '45-59')
    .when(col('age') < 75, '60-74')
    .otherwise('75+'))

# 4. Create BMI categories
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

# 6. Create risk score
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
df = df.withColumn('processing_method', lit('glue_pyspark_etl'))

print(f"Final record count: {df.count()}")
print("Final schema:")
df.printSchema()

# Show sample
print("Sample processed data:")
df.show(5, truncate=False)

# Write to S3 as Parquet
print("Writing processed data to Parquet...")
output_path = f"s3://{target_bucket}/stroke_data_processed/"
df.write.mode("overwrite").parquet(output_path)

print(f"ETL job completed successfully!")
print(f"Output written to: {output_path}")

job.commit()