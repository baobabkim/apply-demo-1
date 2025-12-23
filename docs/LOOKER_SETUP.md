# Looker Studio Setup Guide

This guide walks you through connecting Looker Studio to BigQuery and creating dashboards for the C2C marketplace analytics project.

## Prerequisites

- BigQuery dataset with data (complete Issues #1-#4 first)
- Google account with access to Looker Studio
- BigQuery data populated (run ETL pipeline at least once)

## Step 1: Access Looker Studio

1. Go to [Looker Studio](https://lookerstudio.google.com/)
2. Sign in with your Google account
3. Click **Create** > **Data Source**

## Step 2: Connect to BigQuery

1. In the connector list, search for and select **BigQuery**
2. Click **Authorize** if prompted
3. Select your GCP project
4. Select dataset: `analytics`
5. Select table: `events` (we'll add `users` later)
6. Click **Connect**

## Step 3: Configure Data Source

### Events Data Source

1. Name the data source: "C2C Events"
2. Review the schema - fields should include:
   - event_id (Text)
   - user_id (Text)
   - event_type (Text)
   - event_timestamp (Date & Time)
   - ab_group (Text)
   - item_id (Text)
   - etc.
3. Click **Create Report**

### Add Users Data Source

1. Click **Resource** > **Manage added data sources**
2. Click **Add Data** > **BigQuery**
3. Select `analytics.users` table
4. Name it: "C2C Users"
5. Click **Add**

## Step 4: Create Dashboard

### Dashboard 1: Funnel Analysis

**Purpose**: Visualize user journey and identify drop-off points

#### Chart 1: Funnel Visualization
- **Type**: Funnel Chart
- **Data Source**: C2C Events
- **Dimension**: event_type
- **Metric**: COUNT(event_id)
- **Order**: page_view → search → item_view → chat_click → chat_send

#### Chart 2: Conversion Rates Table
- **Type**: Table
- **Calculated Fields**:
  ```
  Search Rate = COUNT(CASE WHEN event_type = 'search' THEN event_id END) / COUNT(CASE WHEN event_type = 'page_view' THEN event_id END)
  
  Item View Rate = COUNT(CASE WHEN event_type = 'item_view' THEN event_id END) / COUNT(CASE WHEN event_type = 'search' THEN event_id END)
  
  Chat Click Rate = COUNT(CASE WHEN event_type = 'chat_click' THEN event_id END) / COUNT(CASE WHEN event_type = 'item_view' THEN event_id END)
  
  Chat Send Rate = COUNT(CASE WHEN event_type = 'chat_send' THEN event_id END) / COUNT(CASE WHEN event_type = 'chat_click' THEN event_id END)
  ```

### Dashboard 2: A/B Test Results

**Purpose**: Compare control vs treatment group performance

#### Chart 1: Chat Click Rate by A/B Group
- **Type**: Bar Chart
- **Dimension**: ab_group
- **Metric**: Chat Click Rate (calculated field)
- **Filter**: ab_group IN ('control', 'treatment')

#### Chart 2: Conversion Funnel by A/B Group
- **Type**: Stacked Bar Chart
- **Dimension**: event_type
- **Breakdown Dimension**: ab_group
- **Metric**: COUNT(event_id)

### Dashboard 3: User Engagement

**Purpose**: Analyze user behavior patterns

#### Chart 1: Daily Active Users
- **Type**: Time Series
- **Date Range Dimension**: event_timestamp
- **Metric**: COUNT_DISTINCT(user_id)

#### Chart 2: Events by Hour
- **Type**: Heatmap
- **Dimension**: HOUR(event_timestamp)
- **Metric**: COUNT(event_id)

#### Chart 3: User Segment Distribution
- **Type**: Pie Chart
- **Data Source**: C2C Users
- **Dimension**: user_segment
- **Metric**: COUNT(user_id)

## Step 5: Add Filters

Add these filters to make the dashboard interactive:

1. **Date Range Filter**
   - Control: Date Range Control
   - Apply to: All charts

2. **Event Type Filter**
   - Control: Drop-down list
   - Dimension: event_type
   - Apply to: Relevant charts

3. **A/B Group Filter**
   - Control: Drop-down list
   - Dimension: ab_group
   - Apply to: A/B test charts

## Step 6: Styling and Layout

1. **Theme**: Choose a professional theme
   - Recommended: "Simple Dark" or "Corporate"

2. **Layout**:
   - Use grid layout for alignment
   - Group related charts together
   - Add text boxes for section headers

3. **Colors**:
   - Use consistent color scheme
   - Highlight key metrics in accent colors
   - Use red for drop-offs, green for conversions

## Key Metrics to Track

### Primary KPIs
- **D+7 Retention Rate**: Users who return within 7 days
- **Chat Conversion Rate**: item_view → chat_click
- **Transaction Completion Rate**: chat_click → chat_send

### Secondary Metrics
- Daily Active Users (DAU)
- Events per User
- Verified Neighborhood Rate
- A/B Test Lift (Treatment vs Control)

## Sample Queries for Custom Fields

### Retention Rate (7-day)
```sql
COUNT(DISTINCT CASE 
  WHEN DATE_DIFF(CURRENT_DATE(), join_date, DAY) >= 7 
  AND last_activity_date >= DATE_ADD(join_date, INTERVAL 7 DAY)
  THEN user_id 
END) / COUNT(DISTINCT user_id)
```

### Average Events per User
```sql
COUNT(event_id) / COUNT(DISTINCT user_id)
```

### Verified User Rate
```sql
COUNT(DISTINCT CASE WHEN verified_neighborhood = TRUE THEN user_id END) / COUNT(DISTINCT user_id)
```

## Sharing the Dashboard

1. Click **Share** button (top right)
2. Options:
   - **View access**: Anyone with link can view
   - **Edit access**: Specific people can edit
3. Copy and share the link

## Scheduled Email Reports

1. Click **⋯** (three dots) > **Schedule email delivery**
2. Set frequency (daily, weekly, monthly)
3. Add recipients
4. Click **Schedule**

## Best Practices

1. **Keep it simple**: Don't overcrowd dashboards
2. **Use filters**: Allow users to drill down
3. **Add context**: Include text explanations
4. **Update regularly**: Refresh data source connections
5. **Monitor performance**: Optimize slow queries

## Troubleshooting

### Data not showing
- Verify BigQuery tables have data
- Check data source connection
- Refresh data source schema

### Slow dashboard
- Add date range filters
- Use aggregated tables for large datasets
- Limit number of charts per page

### Permission errors
- Ensure you have BigQuery viewer permissions
- Check service account permissions
- Verify project access

## Next Steps

After creating the dashboard:
1. Share with stakeholders
2. Set up scheduled email reports
3. Create additional dashboards for specific analyses
4. Use Google Colab for advanced statistical analysis

## Resources

- [Looker Studio Documentation](https://support.google.com/looker-studio)
- [BigQuery Connector Guide](https://support.google.com/looker-studio/answer/6370296)
- [Calculated Fields Reference](https://support.google.com/looker-studio/answer/6299685)
