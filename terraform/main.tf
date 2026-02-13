# ============================================================================
# Stroke Data Lake - Main Terraform Configuration
# ============================================================================
# Project: AWS Serverless Data Lake for Stroke Risk Analysis
# Region: eu-north-1 (Stockholm)
# Account: 056563840644
# ============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DataEngineering"
      Purpose     = "StrokeRiskAnalysis"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for AWS region
data "aws_region" "current" {}
