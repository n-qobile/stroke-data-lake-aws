# Stroke Data Lake - Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Terraform Deployment](#terraform-deployment)
4. [Data Upload](#data-upload)
5. [Running Glue Crawlers](#running-glue-crawlers)
6. [Running ETL Job](#running-etl-job)
7. [Querying with Athena](#querying-with-athena)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)
10. [Cleanup](#cleanup)

---

## Prerequisites

### ✅ Installed Software
- [x] Terraform (verify: `terraform version`)
- [x] AWS CLI (verify: `aws --version`)
- [x] AWS credentials configured (verify: `aws sts get-caller-identity`)

### ✅ AWS Account Requirements
- Active AWS Account (ID: 056563840644)
- Region: eu-north-1 (Stockholm)
- IAM permissions to create:
  - S3 buckets
  - IAM roles and policies
  - Glue databases, crawlers, and jobs
  - Athena workgroups
  - CloudWatch log groups

### ✅ Dataset
- [x] healthcare-dataset-stroke-data.csv downloaded from Kaggle
- [x] Located in: `data/raw/` folder

---

## Initial Setup

### Step 1: Navigate to Project Directory

```powershell
cd ~\Documents\stroke-data-lake
```

### Step 2: Verify Project Structure

```powershell
tree /F
```

You should see:
```
stroke-data-lake/
├── data/
│   ├── raw/
│   │   └── healthcare-dataset-stroke-data.csv
│   └── processed/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── s3.tf
│   ├── iam.tf
│   ├── glue.tf
│   ├── athena.tf
│   └── outputs.tf
├── lambda/
│   └── transform_data.py
├── sql-queries/
│   └── analysis_queries.sql
└── docs/
    └── deployment-guide.md
```

---

## Terraform Deployment

### Step 3: Initialize Terraform

Navigate to the Terraform directory:

```powershell
cd terraform
terraform init
```

**Expected output:**
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.x.x...

Terraform has been successfully initialized!
```

### Step 4: Validate Configuration

```powershell
terraform validate
```

**Expected output:**
```
Success! The configuration is valid.
```

### Step 5: Review Terraform Plan

```powershell
terraform plan
```

Review the output carefully. You should see Terraform planning to create:
- 3 S3 buckets (raw, processed, athena-results)
- 3 IAM roles (Glue, Athena, Lambda)
- 6 IAM policies
- 1 Glue database
- 2 Glue crawlers
- 1 Glue ETL job
- 1 Athena workgroup
- 7 Athena named queries
- 2 CloudWatch log groups
- Various bucket configurations (versioning, encryption, lifecycle)

**Total resources:** ~30-35 resources

### Step 6: Deploy Infrastructure

```powershell
terraform apply
```

Type `yes` when prompted.

**Deployment time:** 2-5 minutes

**Expected final output:**
```
Apply complete! Resources: 35 added, 0 changed, 0 destroyed.

Outputs:

athena_workgroup_name = "stroke-data-lake-workgroup"
glue_database_name = "stroke_analytics_db"
raw_data_bucket_name = "stroke-data-lake-raw-data-056563840644"
processed_data_bucket_name = "stroke-data-lake-processed-data-056563840644"
...
```

**Save these output values** - you'll need them!

---

## Data Upload

### Step 7: Upload Dataset to S3

Navigate back to project root:

```powershell
cd ..
```

Upload your dataset:

```powershell
aws s3 cp data/raw/healthcare-dataset-stroke-data.csv s3://stroke-data-lake-raw-data-056563840644/
```

**Expected output:**
```
upload: data\raw\healthcare-dataset-stroke-data.csv to s3://stroke-data-lake-raw-data-056563840644/healthcare-dataset-stroke-data.csv
```

### Step 8: Verify Upload

```powershell
aws s3 ls s3://stroke-data-lake-raw-data-056563840644/
```

You should see your CSV file listed with date and size.

---

## Running Glue Crawlers

### Step 9: Run Raw Data Crawler

```powershell
aws glue start-crawler --name stroke-data-lake-raw-crawler
```

**Expected output:**
```
(No output means success)
```

### Step 10: Monitor Crawler Progress

```powershell
aws glue get-crawler --name stroke-data-lake-raw-crawler --query 'Crawler.State' --output text
```

**Possible states:**
- `RUNNING` - Still crawling
- `READY` - Completed successfully

Wait until status is `READY` (usually 1-2 minutes).

### Step 11: Verify Table Creation

```powershell
aws glue get-tables --database-name stroke_analytics_db --query 'TableList[*].Name' --output table
```

You should see a table listed (something like `healthcare_dataset_stroke_data_csv`).

---

## Running ETL Job

### Step 12: Start Glue ETL Job

```powershell
aws glue start-job-run --job-name stroke-data-lake-etl-job
```

**Expected output:**
```json
{
    "JobRunId": "jr_abc123..."
}
```

**Save the JobRunId!**

### Step 13: Monitor ETL Job Progress

```powershell
aws glue get-job-run --job-name stroke-data-lake-etl-job --run-id <YOUR_JOB_RUN_ID> --query 'JobRun.JobRunState' --output text
```

**Possible states:**
- `RUNNING` - Job is processing
- `SUCCEEDED` - Completed successfully
- `FAILED` - Something went wrong

**ETL job duration:** 3-5 minutes (first run may take longer)

### Step 14: Run Processed Data Crawler

Once ETL job succeeds:

```powershell
aws glue start-crawler --name stroke-data-lake-processed-crawler
```

Wait for it to complete (check status same as Step 10).

### Step 15: Verify Processed Table

```powershell
aws glue get-tables --database-name stroke_analytics_db --query 'TableList[*].Name' --output table
```

You should now see TWO tables:
1. Raw data table (CSV)
2. Processed data table (Parquet)

---

## Querying with Athena

### Step 16: Access Athena Console

Open your browser and go to:
```
https://eu-north-1.console.aws.amazon.com/athena/home?region=eu-north-1
```

Or run:
```powershell
start https://eu-north-1.console.aws.amazon.com/athena/home?region=eu-north-1
```

### Step 17: Configure Athena Workgroup

1. In Athena console, click **Workgroups** in left menu
2. Select `stroke-data-lake-workgroup`
3. Click **Switch workgroup**

### Step 18: Run Your First Query

In the Query Editor:

1. Select database: `stroke_analytics_db`
2. You should see your table(s) in the left panel
3. Run this query:

```sql
SELECT 
    COUNT(*) as total_patients,
    SUM(stroke) as total_strokes,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate_percent
FROM stroke_data_processed;
```

**Expected result:**
```
total_patients | total_strokes | stroke_rate_percent
5110          | 249          | 4.87
```

### Step 19: Use Pre-built Queries

In Athena console:
1. Click **Saved queries** tab
2. You'll see 7 pre-built queries:
   - `stroke_prevalence_by_age_group`
   - `stroke_risk_factors_analysis`
   - `demographic_stroke_patterns`
   - `health_metrics_comparison`
   - `urban_vs_rural_stroke_patterns`
   - `identify_high_risk_patients`
   - `bmi_glucose_stroke_correlation`

3. Click any query name → **Run query**

### Step 20: Explore with Custom Queries

Copy queries from `sql-queries/analysis_queries.sql` and run them in Athena.

Try this one to identify high-risk patients:

```sql
SELECT 
    id,
    gender,
    age,
    age_group,
    risk_score,
    stroke,
    CASE 
        WHEN risk_score >= 12 THEN 'Critical Risk'
        WHEN risk_score >= 9 THEN 'High Risk'
        WHEN risk_score >= 6 THEN 'Moderate Risk'
        ELSE 'Low Risk'
    END as risk_category
FROM stroke_data_processed
WHERE risk_score >= 8
ORDER BY risk_score DESC
LIMIT 20;
```

---

## Troubleshooting

### Issue: Terraform apply fails

**Solution:**
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Check region
aws configure get region

# If region is wrong, set it:
aws configure set region eu-north-1
```

### Issue: S3 upload fails - "bucket does not exist"

**Solution:**
```powershell
# Verify bucket was created
aws s3 ls | findstr stroke-data-lake

# If missing, check Terraform output
cd terraform
terraform output raw_data_bucket_name
```

### Issue: Glue crawler fails

**Solution:**
```powershell
# Check crawler status
aws glue get-crawler --name stroke-data-lake-raw-crawler

# View crawler logs in CloudWatch
start https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#logsV2:log-groups
```

### Issue: Athena query fails - "table not found"

**Solution:**
1. Verify crawler ran successfully
2. Check tables exist:
   ```powershell
   aws glue get-tables --database-name stroke_analytics_db
   ```
3. Make sure you selected correct database in Athena UI
4. Try refreshing the table list in Athena console

### Issue: ETL job fails

**Solution:**
```powershell
# Get job run details
aws glue get-job-run --job-name stroke-data-lake-etl-job --run-id <JOB_RUN_ID>

# Check CloudWatch logs
start https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#logsV2:log-groups/log-group/$252Faws-glue$252Fjobs$252Fstroke-data-lake-etl-job
```

### Issue: "Access Denied" errors

**Solution:**
```powershell
# Verify IAM roles were created
aws iam list-roles | findstr stroke-data-lake

# Check your user has necessary permissions
# You may need AmazonS3FullAccess, AWSGlueConsoleFullAccess, AmazonAthenaFullAccess
```

---

## Cost Optimization

### Current Configuration (Already Optimized for Free Tier)

✅ **S3 Storage:**
- Versioning enabled (data protection)
- Lifecycle policies set to transition to Intelligent-Tiering after 90 days
- Old Athena results expire after 365 days

✅ **Glue:**
- Crawlers set to manual run (no scheduled runs = no unnecessary costs)
- ETL job uses smallest worker type (G.1X with 2 workers)

✅ **Athena:**
- Pay per query (you only pay for scanned data)
- Results stored in separate bucket with lifecycle management

### Free Tier Limits (First 12 Months)

- **S3:** 5 GB storage, 20,000 GET requests, 2,000 PUT requests
- **Glue:** 1 million objects stored in Data Catalog
- **Athena:** First 10 GB of data scanned per month free (permanent, not just 12 months)

### Your Estimated Monthly Cost (After Free Tier)

With this dataset (~300 KB):
- **S3 Storage:** $0.00 (well under limits)
- **Glue:** $0.00 (manual runs only)
- **Athena:** $0.00 - $0.01 (queries scan ~0.3 MB)
- **CloudWatch Logs:** $0.00 - $0.01

**Total:** < $0.05/month

### Cost Reduction Tips

1. **Delete old query results:**
   ```powershell
   aws s3 rm s3://stroke-data-lake-athena-results-056563840644/ --recursive
   ```

2. **Stop crawlers when not needed** (already manual)

3. **Use column selection in Athena:**
   ```sql
   SELECT age, stroke FROM stroke_data_processed  -- Cheaper
   -- vs
   SELECT * FROM stroke_data_processed  -- More expensive
   ```

4. **Partition data for large datasets** (not needed for this small dataset)

---

## Cleanup

### To Destroy All Resources

**WARNING:** This will delete ALL data and infrastructure!

```powershell
cd terraform

# Empty S3 buckets first (required before deletion)
aws s3 rm s3://stroke-data-lake-raw-data-056563840644 --recursive
aws s3 rm s3://stroke-data-lake-processed-data-056563840644 --recursive
aws s3 rm s3://stroke-data-lake-athena-results-056563840644 --recursive

# Destroy Terraform resources
terraform destroy
```

Type `yes` when prompted.

**Destruction time:** 2-3 minutes

### To Preserve Data but Stop Costs

If you want to keep data but minimize costs:

1. **Stop scheduled crawlers** (already done - manual only)
2. **Delete CloudWatch logs:**
   ```powershell
   aws logs delete-log-group --log-group-name /aws-glue/jobs/stroke-data-lake-etl-job
   aws logs delete-log-group --log-group-name /aws/athena/stroke-data-lake
   ```
3. **Archive data to Glacier** (for long-term storage):
   ```powershell
   aws s3api put-bucket-lifecycle-configuration --bucket stroke-data-lake-raw-data-056563840644 --lifecycle-configuration file://glacier-lifecycle.json
   ```

---

## Next Steps

### For Your Technical Report

1. **Take screenshots of:**
   - S3 bucket structure
   - Glue Data Catalog showing tables
   - Athena query results
   - CloudWatch logs showing job execution

2. **Document:**
   - Architecture decisions (why Parquet? why manual crawlers?)
   - Cost optimization strategies
   - Data governance approach
   - Challenges faced and solutions

3. **Create architecture diagram** showing data flow:
   ```
   Raw CSV → S3 Raw → Glue Crawler → Data Catalog
                ↓
   Glue ETL Job → S3 Processed → Glue Crawler → Data Catalog
                                       ↓
                                  Athena Queries → S3 Results
   ```

### Optional Enhancements

1. **Add QuickSight dashboard** (covered in project brief)
2. **Implement AWS Lake Formation** for fine-grained access control
3. **Add Lambda for automated pipeline** (trigger ETL on file upload)
4. **Set up CloudWatch alarms** for failed jobs
5. **Create Step Functions** for orchestration

---

## Support Resources

- **AWS Documentation:**
  - [Athena User Guide](https://docs.aws.amazon.com/athena/)
  - [Glue Developer Guide](https://docs.aws.amazon.com/glue/)
  - [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

- **Project-Specific Help:**
  - Review Terraform outputs: `terraform output`
  - Check AWS Console for visual verification
  - Review CloudWatch logs for detailed error messages

---

**Good luck with your data lake deployment! 🚀**
