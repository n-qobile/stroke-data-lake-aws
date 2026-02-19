# Stroke Data Lake - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AWS SERVERLESS DATA LAKE ARCHITECTURE                 │
│                         Stroke Risk Analytics                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   DATA SOURCE        │
│                      │
│  Kaggle Dataset      │
│  (CSV - 5,110 rows)  │
│  Stroke Prediction   │
└──────────┬───────────┘
           │ Manual Upload
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         BRONZE LAYER (Raw Data)                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Amazon S3 - Raw Data Bucket                                       │ │
│  │  • stroke-data-lake-raw-data-056563840644                         │ │
│  │  • Versioning: Enabled                                             │ │
│  │  • Encryption: AES-256                                             │ │
│  │  • Lifecycle: Intelligent-Tiering (90 days)                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA CATALOGING                                  │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS Glue Crawler (Raw)                                            │ │
│  │  • Auto-detects schema                                             │ │
│  │  • Discovers semicolon delimiter                                   │ │
│  │  • Creates table metadata                                          │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS Glue Data Catalog                                             │ │
│  │  • Database: stroke_analytics_db                                   │ │
│  │  • Table: stroke_data_raw                                          │ │
│  │  • Columns: 12 fields (id, gender, age, etc.)                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    ETL TRANSFORMATION (PySpark)                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS Glue ETL Job                                                  │ │
│  │  • Runtime: Glue 4.0                                               │ │
│  │  • Workers: 2x G.1X                                                │ │
│  │  • Language: Python/PySpark                                        │ │
│  │                                                                     │ │
│  │  Transformations:                                                   │ │
│  │  ✓ Remove duplicates                                               │ │
│  │  ✓ Handle missing BMI (fill with median)                          │ │
│  │  ✓ Create age_group categories                                     │ │
│  │  ✓ Create bmi_category (WHO classification)                       │ │
│  │  ✓ Create glucose_category                                         │ │
│  │  ✓ Calculate risk_score (composite metric)                        │ │
│  │  ✓ Standardize text fields                                         │ │
│  │  ✓ Add processing metadata                                         │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         │                                                │
│                         │ Execution Role: stroke-data-lake-glue-role    │
│                         │ Permissions: S3 Read/Write, Glue Catalog      │
└─────────────────────────┼────────────────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      SILVER LAYER (Processed Data)                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Amazon S3 - Processed Data Bucket                                 │ │
│  │  • stroke-data-lake-processed-data-056563840644                   │ │
│  │  • Format: Apache Parquet (columnar)                               │ │
│  │  • Compression: Snappy                                             │ │
│  │  • 60% faster queries, 80% less storage                           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    CATALOG PROCESSED DATA                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS Glue Crawler (Processed)                                      │ │
│  │  • Discovers enhanced schema                                        │ │
│  │  • Registers Parquet metadata                                       │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS Glue Data Catalog                                             │ │
│  │  • Table: stroke_data_processed                                    │ │
│  │  • Enhanced columns: 18 fields                                     │ │
│  │  • Includes: age_group, risk_score, bmi_category, etc.           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      ANALYTICS & QUERYING                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Amazon Athena                                                      │ │
│  │  • Workgroup: stroke-data-lake-workgroup                           │ │
│  │  • Query Engine: Presto                                             │ │
│  │  • Serverless: No infrastructure                                    │ │
│  │  • Pricing: $5 per TB scanned                                       │ │
│  │                                                                     │ │
│  │  Pre-built Named Queries:                                           │ │
│  │  • Stroke prevalence by age group                                  │ │
│  │  • Risk factor analysis                                             │ │
│  │  • Urban vs rural comparisons                                       │ │
│  │  • High-risk patient identification                                │ │
│  └──────────────────────┬─────────────────────────────────────────────┘ │
│                         │                                                │
│                         ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  S3 - Athena Results Bucket                                        │ │
│  │  • Query outputs stored here                                        │ │
│  │  • Lifecycle: Expire after 365 days                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       │ Query Results (CSV)
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION LAYER                                   │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Python Plotly Dashboards                                          │ │
│  │  • Interactive HTML dashboards                                      │ │
│  │  • Stroke awareness color system                                   │ │
│  │  • 3 tabs: What, Where, Why                                        │ │
│  │  • Features: Filters, hover tooltips, zoom                         │ │
│  │                                                                     │ │
│  │  Deliverables:                                                      │ │
│  │  → stroke_dashboard_tab1_what.html                                 │ │
│  │  → stroke_dashboard_tab2_where.html                                │ │
│  │  → stroke_dashboard_tab3_why.html                                  │ │
│  │  → index.html (navigation)                                         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE MANAGEMENT                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Terraform (Infrastructure as Code)                                │ │
│  │  • All AWS resources defined in code                               │ │
│  │  • Version controlled                                               │ │
│  │  • Reproducible deployments                                         │ │
│  │  • Files: main.tf, s3.tf, iam.tf, glue.tf, athena.tf             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                       SECURITY & GOVERNANCE                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AWS IAM (Identity & Access Management)                            │ │
│  │  • Glue Service Role: S3 + Catalog access                         │ │
│  │  • Athena Execution Role: Query permissions                        │ │
│  │  • Lambda Execution Role: ETL permissions                          │ │
│  │  • Principle: Least privilege access                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Amazon CloudWatch                                                  │ │
│  │  • Glue job execution logs                                         │ │
│  │  • Athena query metrics                                             │ │
│  │  • S3 access logs                                                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         KEY METRICS                                      │
│  • Total Patients: 5,110                                                │
│  • Stroke Cases: 249 (4.87%)                                            │
│  • Average Risk Score: 6.3                                              │
│  • Key Finding: Urban detection 15% higher than rural                  │
│  • Monthly Cost: ~$0.05 (post free-tier)                               │
│  • Query Performance: <5 seconds (Parquet optimization)                │
└──────────────────────────────────────────────────────────────────────────┘

Created by: Nqobile Masombuka | Speech Therapist & Cloud Data Engineer
Project: AWS Serverless Data Lake | February 2026
```

## Visual Diagram Instructions

To create a visual diagram, use draw.io (https://app.diagrams.net/):

1. Import AWS icons from: https://aws.amazon.com/architecture/icons/
2. Use these AWS service icons:
   - S3 (orange bucket icon)
   - Glue (purple spider web icon)
   - Athena (orange query icon)
   - CloudWatch (red graph icon)
   - IAM (red person icon)

3. Color scheme:
   - Data flow arrows: Blue
   - Security components: Red
   - Processing: Purple
   - Storage: Orange

4. Layout: Top-to-bottom flow (source → raw → transform → processed → analytics)

## Alternative: Use This Text Diagram

The ASCII diagram above can be:
- Saved as architecture-diagram.txt
- Included in your technical report
- Converted to image with screenshot

## Save This File

Save as: `docs/architecture-diagram.md`
