# ============================================================================
# Amazon Athena - Serverless Query Engine
# ============================================================================

# ============================================================================
# ATHENA WORKGROUP
# ============================================================================

resource "aws_athena_workgroup" "stroke_analytics" {
  name        = "${var.project_name}-workgroup"
  description = "Workgroup for stroke analytics queries"
  state       = "ENABLED"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/query-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }

    engine_version {
      selected_engine_version = "AUTO"
    }
  }

  tags = {
    Name        = "Stroke Analytics Workgroup"
    Description = "Athena workgroup for querying stroke data"
    CostCenter  = "DataEngineering"
  }
}

# ============================================================================
# ATHENA NAMED QUERIES - Pre-built queries for common analysis
# ============================================================================

# Query 1: Stroke prevalence by age group
resource "aws_athena_named_query" "stroke_by_age_group" {
  name        = "stroke_prevalence_by_age_group"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Calculate stroke prevalence across different age groups"

  query = <<-EOT
    SELECT 
        age_group,
        COUNT(*) as total_patients,
        SUM(stroke) as stroke_count,
        ROUND(AVG(stroke) * 100, 2) as stroke_percentage,
        ROUND(AVG(age), 1) as avg_age
    FROM stroke_data_processed
    GROUP BY age_group
    ORDER BY 
        CASE age_group
            WHEN '18-29' THEN 1
            WHEN '30-44' THEN 2
            WHEN '45-59' THEN 3
            WHEN '60-74' THEN 4
            WHEN '75+' THEN 5
        END;
  EOT
}

# Query 2: Risk factors analysis
resource "aws_athena_named_query" "risk_factors" {
  name        = "stroke_risk_factors_analysis"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Analyze correlation between risk factors and stroke occurrence"

  query = <<-EOT
    SELECT 
        hypertension,
        heart_disease,
        smoking_status,
        COUNT(*) as patient_count,
        SUM(stroke) as stroke_cases,
        ROUND(AVG(stroke) * 100, 2) as stroke_rate,
        ROUND(AVG(age), 1) as avg_age,
        ROUND(AVG(bmi), 1) as avg_bmi,
        ROUND(AVG(avg_glucose_level), 1) as avg_glucose
    FROM stroke_data_processed
    GROUP BY hypertension, heart_disease, smoking_status
    HAVING COUNT(*) > 10
    ORDER BY stroke_rate DESC;
  EOT
}

# Query 3: Gender and marital status impact
resource "aws_athena_named_query" "demographics" {
  name        = "demographic_stroke_patterns"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Examine stroke patterns by gender and marital status"

  query = <<-EOT
    SELECT 
        gender,
        ever_married,
        COUNT(*) as total,
        SUM(stroke) as strokes,
        ROUND(AVG(stroke) * 100, 2) as stroke_percentage,
        ROUND(AVG(age), 1) as avg_age
    FROM stroke_data_processed
    GROUP BY gender, ever_married
    ORDER BY stroke_percentage DESC;
  EOT
}

# Query 4: Lifestyle and health metrics
resource "aws_athena_named_query" "health_metrics" {
  name        = "health_metrics_comparison"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Compare health metrics between stroke and non-stroke patients"

  query = <<-EOT
    SELECT 
        stroke,
        COUNT(*) as patient_count,
        ROUND(AVG(age), 1) as avg_age,
        ROUND(AVG(bmi), 1) as avg_bmi,
        ROUND(AVG(avg_glucose_level), 1) as avg_glucose,
        ROUND(SUM(CASE WHEN hypertension = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as hypertension_pct,
        ROUND(SUM(CASE WHEN heart_disease = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as heart_disease_pct,
        ROUND(SUM(CASE WHEN smoking_status = 'smokes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as smokers_pct
    FROM stroke_data_processed
    GROUP BY stroke
    ORDER BY stroke DESC;
  EOT
}

# Query 5: Geographic analysis
resource "aws_athena_named_query" "geographic" {
  name        = "urban_vs_rural_stroke_patterns"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Compare stroke rates between urban and rural populations"

  query = <<-EOT
    SELECT 
        residence_type,
        COUNT(*) as total_patients,
        SUM(stroke) as stroke_cases,
        ROUND(AVG(stroke) * 100, 2) as stroke_rate,
        ROUND(AVG(age), 1) as avg_age,
        ROUND(AVG(bmi), 1) as avg_bmi,
        ROUND(AVG(avg_glucose_level), 1) as avg_glucose
    FROM stroke_data_processed
    GROUP BY residence_type
    ORDER BY stroke_rate DESC;
  EOT
}

# Query 6: High-risk patient identification
resource "aws_athena_named_query" "high_risk" {
  name        = "identify_high_risk_patients"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Identify patients at highest risk for stroke (for therapy planning)"

  query = <<-EOT
    SELECT 
        id,
        gender,
        age,
        age_group,
        bmi_category,
        glucose_category,
        hypertension,
        heart_disease,
        smoking_status,
        risk_score,
        stroke
    FROM stroke_data_processed
    WHERE risk_score >= 8
    ORDER BY risk_score DESC, age DESC
    LIMIT 100;
  EOT
}

# Query 7: BMI and glucose correlation
resource "aws_athena_named_query" "bmi_glucose" {
  name        = "bmi_glucose_stroke_correlation"
  database    = aws_glue_catalog_database.stroke_analytics.name
  workgroup   = aws_athena_workgroup.stroke_analytics.name
  description = "Analyze how BMI and glucose levels correlate with stroke risk"

  query = <<-EOT
    SELECT 
        bmi_category,
        glucose_category,
        COUNT(*) as patient_count,
        SUM(stroke) as stroke_cases,
        ROUND(AVG(stroke) * 100, 2) as stroke_rate,
        ROUND(AVG(age), 1) as avg_age
    FROM stroke_data_processed
    GROUP BY bmi_category, glucose_category
    HAVING COUNT(*) > 5
    ORDER BY stroke_rate DESC;
  EOT
}

# ============================================================================
# CLOUDWATCH LOG GROUP for Athena Query Logs
# ============================================================================

resource "aws_cloudwatch_log_group" "athena_logs" {
  name              = "/aws/athena/${var.project_name}"
  retention_in_days = 7

  tags = {
    Name        = "Athena Query Logs"
    Description = "CloudWatch logs for Athena query execution"
  }
}
