terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── S3 Data Lake ────────────────────────────────────────────────────────────────

resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name

  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── IAM ─────────────────────────────────────────────────────────────────────────

resource "aws_iam_user" "innerchart" {
  name = "${var.project_name}-pipeline-user"

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_policy" "s3_access" {
  name        = "${var.project_name}-s3-access"
  description = "Allows InnerChart pipeline to read and write to the data lake"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "innerchart" {
  user       = aws_iam_user.innerchart.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_access_key" "innerchart" {
  user = aws_iam_user.innerchart.name
}

# ── Outputs ──────────────────────────────────────────────────────────────────────

output "bucket_name" {
  value = aws_s3_bucket.data_lake.bucket
}

output "aws_access_key_id" {
  value = aws_iam_access_key.innerchart.id
}

output "aws_secret_access_key" {
  value     = aws_iam_access_key.innerchart.secret
  sensitive = true
}
