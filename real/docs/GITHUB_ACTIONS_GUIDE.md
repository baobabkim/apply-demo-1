# GitHub Actions Guide for Daily ETL Pipeline

This guide explains how to use and manage the automated ETL pipeline.

## Overview

The daily ETL pipeline automatically:
1. Generates synthetic user and event data
2. Loads the data to BigQuery
3. Runs daily at 02:00 KST (17:00 UTC)

## Workflow File

Location: `.github/workflows/daily_etl.yml`

## Schedule

- **Automatic**: Runs daily at 02:00 KST (17:00 UTC previous day)
- **Manual**: Can be triggered manually via GitHub Actions UI

## Required Secrets

The workflow requires the following GitHub repository secrets:

### 1. GCP_PROJECT_ID
- Your Google Cloud Project ID
- Example: `c2c-marketplace-analytics`

### 2. GCP_SA_KEY
- Service Account JSON key (entire file contents)
- Must have BigQuery permissions

## Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **New repository secret**
4. Add both secrets as described above

## Manual Trigger

To manually trigger the workflow:

1. Go to **Actions** tab in your GitHub repository
2. Select **Daily ETL Pipeline** from the left sidebar
3. Click **Run workflow** button
4. (Optional) Specify number of users to generate
5. Click **Run workflow**

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab
2. Click on a specific workflow run to see details
3. Expand each step to view logs

### Check Data in BigQuery

After successful run:
1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Navigate to your project > `analytics` dataset
3. Query the `users` and `events` tables

Example query:
```sql
SELECT 
  DATE(event_timestamp) as date,
  event_type,
  COUNT(*) as count
FROM `your-project-id.analytics.events`
WHERE DATE(event_timestamp) = CURRENT_DATE()
GROUP BY date, event_type
ORDER BY count DESC
```

## Artifacts

Each workflow run uploads generated CSV files as artifacts:
- **Name**: `generated-data-{run_number}`
- **Retention**: 7 days
- **Contents**: `users_YYYYMMDD.csv` and `events_YYYYMMDD.csv`

To download artifacts:
1. Go to the workflow run details
2. Scroll to **Artifacts** section
3. Click to download

## Troubleshooting

### Authentication Errors

**Error**: `Failed to connect to BigQuery`

**Solution**:
- Verify `GCP_SA_KEY` secret is correctly set
- Ensure service account has BigQuery permissions
- Check that `GCP_PROJECT_ID` matches your actual project

### Permission Errors

**Error**: `Permission denied on BigQuery`

**Solution**:
- Verify service account has these roles:
  - BigQuery Admin
  - BigQuery Data Editor
  - BigQuery Job User

### Schedule Not Running

**Possible causes**:
- Repository must have at least one workflow run in the last 60 days
- Scheduled workflows may be delayed by up to 15 minutes
- Check if Actions are enabled in repository settings

### Data Not Appearing in BigQuery

**Steps to debug**:
1. Check workflow logs for errors
2. Verify data generation step completed
3. Check BigQuery loading step output
4. Query BigQuery tables directly

## Modifying the Schedule

To change the schedule, edit `.github/workflows/daily_etl.yml`:

```yaml
schedule:
  - cron: '0 17 * * *'  # 02:00 KST = 17:00 UTC
```

Cron syntax: `minute hour day month weekday`

Examples:
- `0 9 * * *` - Daily at 18:00 KST (09:00 UTC)
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1` - Every Monday at 18:00 KST

## Disabling the Workflow

To temporarily disable:
1. Go to **Actions** tab
2. Select **Daily ETL Pipeline**
3. Click **⋯** (three dots) > **Disable workflow**

To re-enable, follow the same steps and select **Enable workflow**

## Cost Monitoring

Monitor GCP costs:
1. Go to [GCP Billing](https://console.cloud.google.com/billing)
2. Check BigQuery usage
3. Set up budget alerts if needed

Expected costs (with 1000 users/day):
- Storage: < $0.01/month
- Queries: Within free tier
- Total: Minimal (likely $0)

## Best Practices

1. **Monitor regularly**: Check workflow runs weekly
2. **Review data quality**: Periodically query BigQuery to ensure data looks correct
3. **Rotate credentials**: Update service account keys every 90 days
4. **Set up alerts**: Configure GCP alerts for BigQuery errors
5. **Version control**: Always commit workflow changes to git

## Support

For issues:
1. Check workflow logs in Actions tab
2. Review BigQuery logs in GCP Console
3. Verify all secrets are correctly configured
4. Check this guide's troubleshooting section
