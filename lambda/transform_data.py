"""
Lambda Function: Stroke Data Transformation
============================================
This function processes raw stroke data and creates enhanced features
for analysis. It can be triggered manually or by S3 events.

Input: Raw CSV from S3 (healthcare-dataset-stroke-data.csv)
Output: Processed Parquet files with additional features
"""

import json
import boto3
import pandas as pd
import io
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    """
    print("Starting stroke data transformation...")
    
    # Get bucket names from environment or event
    source_bucket = event.get('source_bucket', 'stroke-data-lake-raw-data-056563840644')
    target_bucket = event.get('target_bucket', 'stroke-data-lake-processed-data-056563840644')
    source_key = event.get('source_key', 'healthcare-dataset-stroke-data.csv')
    
    try:
        # Read raw data from S3
        print(f"Reading from s3://{source_bucket}/{source_key}")
        response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Data Quality & Transformations
        print("Applying transformations...")
        
        # 1. Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['id'])
        print(f"Removed {initial_count - len(df)} duplicate records")
        
        # 2. Handle missing BMI values (fill with median)
        bmi_median = df['bmi'].median()
        df['bmi'].fillna(bmi_median, inplace=True)
        print(f"Filled missing BMI values with median: {bmi_median:.2f}")
        
        # 3. Create age groups
        def categorize_age(age):
            if age < 30:
                return '18-29'
            elif age < 45:
                return '30-44'
            elif age < 60:
                return '45-59'
            elif age < 75:
                return '60-74'
            else:
                return '75+'
        
        df['age_group'] = df['age'].apply(categorize_age)
        
        # 4. Create BMI categories (WHO classification)
        def categorize_bmi(bmi):
            if pd.isna(bmi):
                return 'Unknown'
            elif bmi < 18.5:
                return 'Underweight'
            elif bmi < 25:
                return 'Normal'
            elif bmi < 30:
                return 'Overweight'
            else:
                return 'Obese'
        
        df['bmi_category'] = df['bmi'].apply(categorize_bmi)
        
        # 5. Create glucose categories
        def categorize_glucose(glucose):
            if pd.isna(glucose):
                return 'Unknown'
            elif glucose < 100:
                return 'Normal'
            elif glucose < 126:
                return 'Prediabetic'
            else:
                return 'Diabetic'
        
        df['glucose_category'] = df['avg_glucose_level'].apply(categorize_glucose)
        
        # 6. Create simple risk score
        def calculate_risk_score(row):
            score = 0
            
            # Age component (0-10 points)
            score += int(row['age'] / 10)
            
            # Hypertension (2 points)
            score += row['hypertension'] * 2
            
            # Heart disease (3 points)
            score += row['heart_disease'] * 3
            
            # Smoking (0-2 points)
            if row['smoking_status'] == 'smokes':
                score += 2
            elif row['smoking_status'] == 'formerly smoked':
                score += 1
            
            # BMI (0-2 points)
            if row['bmi'] > 30:
                score += 2
            elif row['bmi'] > 25:
                score += 1
            
            return score
        
        df['risk_score'] = df.apply(calculate_risk_score, axis=1)
        
        # 7. Standardize text fields
        df['gender'] = df['gender'].str.upper()
        df['ever_married'] = df['ever_married'].str.upper()
        df['work_type'] = df['work_type'].str.title()
        df['Residence_type'] = df['Residence_type'].str.title()
        
        # 8. Add metadata
        df['processed_date'] = datetime.utcnow().isoformat()
        df['data_source'] = 'kaggle_stroke_prediction'
        df['processing_method'] = 'lambda_function'
        
        print(f"Transformations complete. Final record count: {len(df)}")
        
        # Convert to Parquet and upload to S3
        target_key = 'stroke_data_processed/stroke_data.parquet'
        print(f"Writing to s3://{target_bucket}/{target_key}")
        
        # Convert to Parquet in memory
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=parquet_buffer.getvalue(),
            ContentType='application/octet-stream'
        )
        
        print("Data successfully processed and uploaded!")
        
        # Generate summary statistics
        summary = {
            'total_records': len(df),
            'stroke_cases': int(df['stroke'].sum()),
            'stroke_rate': float(df['stroke'].mean() * 100),
            'avg_age': float(df['age'].mean()),
            'avg_bmi': float(df['bmi'].mean()),
            'avg_glucose': float(df['avg_glucose_level'].mean()),
            'age_groups': df['age_group'].value_counts().to_dict(),
            'bmi_categories': df['bmi_category'].value_counts().to_dict(),
            'risk_score_stats': {
                'mean': float(df['risk_score'].mean()),
                'median': float(df['risk_score'].median()),
                'max': int(df['risk_score'].max()),
                'min': int(df['risk_score'].min())
            }
        }
        
        print("Summary Statistics:")
        print(json.dumps(summary, indent=2))
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data transformation completed successfully',
                'source': f's3://{source_bucket}/{source_key}',
                'target': f's3://{target_bucket}/{target_key}',
                'summary': summary
            })
        }
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing data',
                'error': str(e)
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'source_bucket': 'stroke-data-lake-raw-data-056563840644',
        'target_bucket': 'stroke-data-lake-processed-data-056563840644',
        'source_key': 'healthcare-dataset-stroke-data.csv'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
