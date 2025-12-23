# GCP Setup Guide

This guide walks you through setting up Google Cloud Platform for the C2C Marketplace Analytics project.

## Prerequisites

- Google Cloud Platform account
- Billing enabled on your GCP account
- `gcloud` CLI installed (optional but recommended)

## Step 1: Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name: `c2c-marketplace-analytics` (or your preferred name)
5. Note your **Project ID** - you'll need this later

## Step 2: Enable BigQuery API

1. In the GCP Console, go to **APIs & Services > Library**
2. Search for "BigQuery API"
3. Click on it and press **Enable**

## Step 3: Create Service Account

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Enter details:
   - Name: `bigquery-etl-service`
   - Description: `Service account for automated ETL to BigQuery`
4. Click **Create and Continue**
5. Grant the following roles:
   - `BigQuery Admin`
   - `BigQuery Data Editor`
   - `BigQuery Job User`
6. Click **Continue** then **Done**

## Step 4: Generate Service Account Key

1. Find your newly created service account in the list
2. Click on it to open details
3. Go to the **Keys** tab
4. Click **Add Key > Create new key**
5. Select **JSON** format
6. Click **Create**
7. The key file will download automatically
8. **IMPORTANT**: Rename the file to `service-account-key.json` and save it in a secure location
9. **DO NOT** commit this file to git (it's already in `.gitignore`)

## Step 5: Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **New repository secret**
4. Add the following secrets:

### Secret 1: GCP_PROJECT_ID
- Name: `GCP_PROJECT_ID`
- Value: Your GCP Project ID (from Step 1)

### Secret 2: GCP_SA_KEY
- Name: `GCP_SA_KEY`
- Value: The entire contents of your `service-account-key.json` file
  - Open the JSON file in a text editor
  - Copy ALL the content (including the curly braces)
  - Paste it as the secret value

## Step 6: Set Up Local Environment (Optional)

For local development and testing:

```bash
# Set environment variable for authentication
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# On Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

Or create a `.env` file in the project root:

```
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GCP_PROJECT_ID=your-project-id
```

## Verification

To verify your setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Test BigQuery connection
python scripts/setup_bigquery.py
```

## Cost Considerations

BigQuery pricing:
- **Storage**: $0.02 per GB per month (first 10 GB free)
- **Queries**: $5 per TB processed (first 1 TB free per month)

For this project with synthetic data:
- Expected storage: < 1 GB
- Expected query costs: Minimal (within free tier)

## Security Best Practices

1. ✅ Never commit `service-account-key.json` to git
2. ✅ Rotate service account keys regularly (every 90 days)
3. ✅ Use least privilege principle for IAM roles
4. ✅ Enable audit logging for BigQuery
5. ✅ Use GitHub Secrets for CI/CD credentials

## Troubleshooting

### "Permission denied" errors
- Verify service account has correct roles
- Check that `GCP_SA_KEY` secret is properly formatted

### "API not enabled" errors
- Ensure BigQuery API is enabled in GCP Console
- Wait a few minutes after enabling for changes to propagate

### "Project not found" errors
- Verify `GCP_PROJECT_ID` matches your actual project ID
- Check for typos in the project ID

## Next Steps

After completing this setup:
1. Run `python scripts/setup_bigquery.py` to create datasets and tables
2. Run `python scripts/load_data.py` to test data loading
3. Verify data appears in BigQuery Console
