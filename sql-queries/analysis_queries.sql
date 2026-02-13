-- ============================================================================
-- ATHENA SQL QUERIES - Stroke Data Lake Analytics
-- ============================================================================
-- These queries can be run in Amazon Athena after data is loaded and crawled
-- Database: stroke_analytics_db
-- ============================================================================

-- ============================================================================
-- QUERY 1: Overall Dataset Summary
-- ============================================================================
-- Purpose: Get a quick overview of the dataset

SELECT 
    COUNT(*) as total_patients,
    SUM(stroke) as total_strokes,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate_percent,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi,
    ROUND(AVG(avg_glucose_level), 1) as avg_glucose,
    MIN(age) as min_age,
    MAX(age) as max_age
FROM stroke_data_processed;

-- ============================================================================
-- QUERY 2: Stroke Prevalence by Age Group
-- ============================================================================
-- Purpose: Identify which age groups are most affected by stroke
-- Speech Therapy Relevance: Helps plan service capacity by age demographics

SELECT 
    age_group,
    COUNT(*) as total_patients,
    SUM(stroke) as stroke_count,
    ROUND(AVG(stroke) * 100, 2) as stroke_percentage,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi
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

-- ============================================================================
-- QUERY 3: Risk Factor Analysis
-- ============================================================================
-- Purpose: Analyze how different risk factors correlate with stroke
-- Speech Therapy Relevance: Understand patient profiles for therapy planning

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
ORDER BY stroke_rate DESC
LIMIT 20;

-- ============================================================================
-- QUERY 4: Gender and Marital Status Patterns
-- ============================================================================
-- Purpose: Examine demographic patterns in stroke occurrence

SELECT 
    gender,
    ever_married,
    COUNT(*) as total_patients,
    SUM(stroke) as stroke_count,
    ROUND(AVG(stroke) * 100, 2) as stroke_percentage,
    ROUND(AVG(age), 1) as avg_age
FROM stroke_data_processed
GROUP BY gender, ever_married
ORDER BY stroke_percentage DESC;

-- ============================================================================
-- QUERY 5: Stroke vs Non-Stroke Patient Comparison
-- ============================================================================
-- Purpose: Compare characteristics between patients who had strokes vs those who didn't

SELECT 
    CASE WHEN stroke = 1 THEN 'Stroke Patients' ELSE 'Non-Stroke Patients' END as patient_group,
    COUNT(*) as patient_count,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi,
    ROUND(AVG(avg_glucose_level), 1) as avg_glucose,
    ROUND(SUM(CASE WHEN hypertension = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as hypertension_percentage,
    ROUND(SUM(CASE WHEN heart_disease = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as heart_disease_percentage,
    ROUND(SUM(CASE WHEN smoking_status = 'smokes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as current_smokers_percentage
FROM stroke_data_processed
GROUP BY stroke
ORDER BY stroke DESC;

-- ============================================================================
-- QUERY 6: Urban vs Rural Analysis
-- ============================================================================
-- Purpose: Compare stroke patterns between urban and rural populations
-- Speech Therapy Relevance: Helps with geographic resource allocation

SELECT 
    residence_type,
    COUNT(*) as total_patients,
    SUM(stroke) as stroke_cases,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi,
    ROUND(AVG(avg_glucose_level), 1) as avg_glucose,
    ROUND(SUM(CASE WHEN hypertension = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as hypertension_pct
FROM stroke_data_processed
GROUP BY residence_type
ORDER BY stroke_rate DESC;

-- ============================================================================
-- QUERY 7: High-Risk Patient Identification
-- ============================================================================
-- Purpose: Identify patients at highest risk for stroke
-- Speech Therapy Relevance: Proactive therapy planning and screening programs

SELECT 
    id,
    gender,
    age,
    age_group,
    bmi,
    bmi_category,
    avg_glucose_level,
    glucose_category,
    hypertension,
    heart_disease,
    smoking_status,
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
ORDER BY risk_score DESC, age DESC
LIMIT 100;

-- ============================================================================
-- QUERY 8: BMI and Glucose Correlation
-- ============================================================================
-- Purpose: Analyze how BMI and glucose levels interact with stroke risk

SELECT 
    bmi_category,
    glucose_category,
    COUNT(*) as patient_count,
    SUM(stroke) as stroke_cases,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(risk_score), 1) as avg_risk_score
FROM stroke_data_processed
GROUP BY bmi_category, glucose_category
HAVING COUNT(*) > 5
ORDER BY stroke_rate DESC;

-- ============================================================================
-- QUERY 9: Work Type Analysis
-- ============================================================================
-- Purpose: Examine stroke patterns across different employment types

SELECT 
    work_type,
    COUNT(*) as total_patients,
    SUM(stroke) as stroke_count,
    ROUND(AVG(stroke) * 100, 2) as stroke_percentage,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(risk_score), 1) as avg_risk_score
FROM stroke_data_processed
GROUP BY work_type
ORDER BY stroke_percentage DESC;

-- ============================================================================
-- QUERY 10: Age and BMI Distribution for Stroke Patients
-- ============================================================================
-- Purpose: Understand the distribution of stroke patients by age and BMI
-- Speech Therapy Relevance: Helps tailor therapy approaches to patient profiles

SELECT 
    age_group,
    bmi_category,
    COUNT(*) as stroke_patient_count,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi,
    ROUND(AVG(risk_score), 1) as avg_risk_score
FROM stroke_data_processed
WHERE stroke = 1
GROUP BY age_group, bmi_category
ORDER BY 
    CASE age_group
        WHEN '18-29' THEN 1
        WHEN '30-44' THEN 2
        WHEN '45-59' THEN 3
        WHEN '60-74' THEN 4
        WHEN '75+' THEN 5
    END,
    stroke_patient_count DESC;

-- ============================================================================
-- QUERY 11: Smoking Impact Analysis
-- ============================================================================
-- Purpose: Detailed analysis of smoking's impact on stroke risk

SELECT 
    smoking_status,
    age_group,
    COUNT(*) as total_patients,
    SUM(stroke) as stroke_cases,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate,
    ROUND(AVG(age), 1) as avg_age
FROM stroke_data_processed
GROUP BY smoking_status, age_group
ORDER BY stroke_rate DESC;

-- ============================================================================
-- QUERY 12: Multi-Factor High Risk Combinations
-- ============================================================================
-- Purpose: Identify the most dangerous combinations of risk factors

SELECT 
    CASE WHEN hypertension = 1 THEN 'Yes' ELSE 'No' END as has_hypertension,
    CASE WHEN heart_disease = 1 THEN 'Yes' ELSE 'No' END as has_heart_disease,
    bmi_category,
    glucose_category,
    COUNT(*) as patient_count,
    SUM(stroke) as stroke_cases,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate
FROM stroke_data_processed
GROUP BY hypertension, heart_disease, bmi_category, glucose_category
HAVING COUNT(*) > 10
ORDER BY stroke_rate DESC
LIMIT 15;

-- ============================================================================
-- QUERY 13: Data Quality Check
-- ============================================================================
-- Purpose: Verify data completeness and identify any issues

SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) as null_ages,
    SUM(CASE WHEN bmi IS NULL THEN 1 ELSE 0 END) as null_bmis,
    SUM(CASE WHEN avg_glucose_level IS NULL THEN 1 ELSE 0 END) as null_glucose,
    SUM(CASE WHEN stroke IS NULL THEN 1 ELSE 0 END) as null_stroke,
    COUNT(DISTINCT id) as unique_patients,
    COUNT(*) - COUNT(DISTINCT id) as duplicate_records
FROM stroke_data_processed;

-- ============================================================================
-- QUERY 14: Risk Score Distribution
-- ============================================================================
-- Purpose: Understand the distribution of risk scores across the population

SELECT 
    risk_score,
    COUNT(*) as patient_count,
    SUM(stroke) as stroke_cases,
    ROUND(AVG(stroke) * 100, 2) as stroke_rate,
    ROUND(AVG(age), 1) as avg_age
FROM stroke_data_processed
GROUP BY risk_score
ORDER BY risk_score DESC;

-- ============================================================================
-- QUERY 15: Therapy Planning Insights
-- ============================================================================
-- Purpose: Create actionable insights for speech therapy service planning
-- Estimates potential therapy needs based on stroke patients

SELECT 
    age_group,
    residence_type,
    SUM(stroke) as stroke_patients,
    -- Assume 70% of stroke patients need speech therapy
    ROUND(SUM(stroke) * 0.70, 0) as estimated_therapy_need,
    -- Assume avg 12 sessions per patient
    ROUND(SUM(stroke) * 0.70 * 12, 0) as estimated_total_sessions,
    ROUND(AVG(CASE WHEN stroke = 1 THEN age ELSE NULL END), 1) as avg_stroke_patient_age
FROM stroke_data_processed
GROUP BY age_group, residence_type
ORDER BY estimated_therapy_need DESC;
