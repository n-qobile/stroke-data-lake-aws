# 🎗️ AWS Serverless Data Lake — Stroke Risk Analytics

![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?style=flat&logo=amazon-aws)
![Terraform](https://img.shields.io/badge/Terraform-IaC-623CE4?style=flat&logo=terraform)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat&logo=plotly)
![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Live-181717?style=flat&logo=github)

> **A production-grade, serverless data lake built on AWS to analyse stroke risk factors across 5,110 patient records — with interactive HTML dashboards hosted live on GitHub Pages.**

---

## 🌐 Live Dashboard

**[View Interactive Dashboards →](https://n-qobile.github.io/stroke-data-lake-aws/)**

No installation required. Navigate between tabs directly in your browser:
- 📊 **WHAT?** — Executive overview, KPIs, and key insights.
- 🗺️ **WHERE?** — Geographic analysis and urban vs rural disparities.
- 🔍 **WHY?** — Risk factor analysis and comorbidity patterns.

---

## ⭐ Key Finding

> **Urban areas detect more strokes (5.2%) than rural areas (4.5%).**
>
> This suggests a diagnostic access gap — rural residents face barriers such as limited specialist availability, delayed diagnosis, and transportation challenges. This finding has direct implications for telehealth expansion and rural speech therapy resource allocation.

---

## 🏗️ Architecture Overview

```
Kaggle Dataset (CSV)
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  BRONZE LAYER                                            │
│  S3 Raw Bucket → Glue Crawler → Glue Data Catalogue      │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  ETL TRANSFORMATION                                      │
│  AWS Glue ETL Job (PySpark)                              │
│  • Deduplication  • BMI imputation  • Feature engineering│
│  • risk_score (0–20)  • Parquet output                   │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  SILVER LAYER                                            │
│  S3 Processed Bucket → Glue Crawler → Glue Catalogue     │
│  Apache Parquet  •  Snappy compression                   │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  ANALYTICS                                               │
│  Amazon Athena (Serverless SQL)  •  5 analytical queries │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  VISUALISATION  (GitHub Pages)                           │
│  Python Plotly → Static HTML Export → GitHub Pages       │
│  No backend server required  •  Free hosting             │
└──────────────────────────────────────────────────────────┘
```

See `docs/architectural_diagrams/architecture-diagram.png` for the full visual diagram.

---

## 📁 Project Structure

```
stroke-data-lake-aws/
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── s3.tf
│   ├── iam.tf
│   ├── glue.tf
│   └── athena.tf
│
├── dashboard.py                # Dashboard generation
│
├── sql-queries/                # Analytical SQL queries
│   └── analysis_queries.sql
│
├── lambda/                     # Alternative ETL (not deployed)
│   └── transform_data.py
│
├── scripts/                     # Alternative Glue Script (not deployed)
│   └── glue_script_fixed.py
│
├── docs/                       # Documentation
│   ├── architecture-diagram.png
│   └── technical-report.md
|   └── deployment-guide.md
│   └──screenshots/                # Evidence: queries & AWS services
|
├── index.html                  # Dashboard tab navigation (GitHub Pages)
│
├── README.md
└── .gitignore
```

---

## 🔬 Dataset

| Attribute | Detail |
|-----------|--------|
| Source | Kaggle Stroke Prediction Dataset |
| Records | 5,110 patients |
| Original format | CSV (semicolon-delimited) |
| Processed format | Apache Parquet (Snappy compressed) |
| Enhanced columns | age_group, bmi_category, glucose_category, risk_score |

---

## 📊 Key Results

| Finding | Data | Implication |
|---------|------|-------------|
| Urban vs Rural Detection | 5.2% vs 4.5% | Healthcare access gap |
| Highest Risk Age Group | 75+ (43 cases) | Priority for services |
| Average Risk Score | 5.3 out of 20 | Moderate risk population |
| Comorbidity Rate | HTN + HD + Smoking = 18.5% | Compounding effect |
| SLP Demand | ~174 patients | ~2,088 therapy sessions needed |

---

## 🎨 Dashboard Colour System

The dashboard uses an intentional colour palette grounded in **speech therapy semantic cueing principles** — each colour reinforces the meaning of its tab rather than applying a generic "traffic light" system.

| Colour | Hex | Purpose |
|--------|-----|---------|
| 🟣 Stroke Purple | `#7C3AED` | Clinical credibility — primary brand across all tabs |
| 🔴 Stroke Red Ribbon | `#EF4444` | International stroke awareness symbol |
| 🔵 Electric Blue | `#3B82F6` | Geographic/systems thinking — WHERE? tab |
| 🟢 Lime Green | `#84CC16` | Rural/environmental context — WHERE? tab |
| 🟠 Vivid Orange | `#F97316` | Risk mechanisms and causation — WHY? tab |

**Why not the standard "green = good, red = bad" system?**

Traditional medical dashboards oversimplify complex healthcare data with traffic-light colours. This approach assigns each tab a thematic colour that reinforces its analytical purpose — making the dashboard more memorable, accessible, and analytically sophisticated. High contrast ratios also support accessibility for stroke survivors with visual deficits.

---

## 🗣️ Speech Therapy Relevance

As a speech therapist, this project bridges clinical knowledge and cloud engineering:

- **70% of stroke survivors** require speech and language therapy (SLP) services.
- **~174 patients** in this dataset are estimated to need SLP intervention.
- **~2,088 sessions** are required based on an average of 12 sessions per patient.
- **Priority population:** Urban residents aged 75+ (highest stroke detection rate).
- **Rural gap:** Telehealth expansion is recommended to address the 0.7 percentage point detection disparity.

---

## 🛠️ Technologies Used

| Category | Technology |
|----------|-----------|
| Cloud Platform | Amazon Web Services (AWS) |
| Infrastructure | Terraform (IaC) |
| Storage | Amazon S3 |
| ETL | AWS Glue (PySpark) |
| Data Catalogue | AWS Glue Data Catalogue |
| Analytics | Amazon Athena (Presto SQL) |
| Visualisation | Python, Plotly (exported to static HTML) |
| Hosting | GitHub Pages |
| Version Control | Git / GitHub |
| Language | Python 3.9+ |

---

## 💰 Cost

| Service | Monthly Cost |
|---------|-------------|
| Amazon S3 (3 buckets, ~1 GB) | ~£0.02 |
| Amazon Athena (100 queries) | ~£0.01 |
| AWS Glue ETL (manual) | £0.00 |
| GitHub Pages (hosting) | £0.00 |
| **Total** | **~£0.04/month** |

Costs are minimised through Parquet compression (80% less data scanned), manual crawler execution, and S3 lifecycle policies.

---

## 🚀 Deployment

### Prerequisites
- AWS account with appropriate IAM permissions.
- Python 3.9+.

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/n-qobile/stroke-data-lake-aws.git
cd stroke-data-lake-aws

# 2. Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# 3. Upload raw data to S3
aws s3 cp data/raw/healthcare-dataset-stroke-data.csv \
    s3://stroke-data-lake-raw-data-ACCOUNT_ID/

# 4. Run Glue ETL job (via AWS Console or CLI)

# 5. Generate dashboards
cd dashboards
python dashboard_enhanced.py
# This creates index.html and 3 tab HTML files

# 6. Commit HTML files and enable GitHub Pages
git add index.html *.html
git commit -m "Add: Dashboard HTML files for GitHub Pages"
git push
# Then: GitHub repo → Settings → Pages → Source: main branch → Save
```

---

## 📸 Screenshots

See the `screenshots/` folder for:
- AWS Console: S3 buckets, Glue job, Glue catalogue, Athena workgroup.
- Athena query results (5 analytical queries with CSVs).

---

## 📄 Documentation

- [`docs/architectural_diagrams/architecture-diagram.png`](docs/architectural_diagrams/architecture-diagram.png) — Full system architecture
- [`docs/technical-report.md`](docs/technical-report.md) — 3-page technical report

---

## 👩‍💻 Author

**Created by Nqobile M**
Speech Therapist & Cloud Data Engineer | February 2026

---

