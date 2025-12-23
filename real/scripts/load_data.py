"""
Data Loading Script for BigQuery

This script loads generated CSV data into BigQuery tables.
"""

import os
import sys
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime


def get_bigquery_client(project_id: str = None, credentials_path: str = None):
    """Create and return a BigQuery client"""
    if credentials_path and os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        client = bigquery.Client(credentials=credentials, project=project_id)
    else:
        client = bigquery.Client(project=project_id)
    
    return client


def load_users_data(client: bigquery.Client, csv_path: str, dataset_id: str = "analytics"):
    """
    Load users data from CSV to BigQuery
    
    Args:
        client: BigQuery client
        csv_path: Path to users CSV file
        dataset_id: Dataset name
    """
    table_id = f"{client.project}.{dataset_id}.users"
    
    print(f"[*] Loading users data from {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Convert date columns
    df['join_date'] = pd.to_datetime(df['join_date']).dt.date
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    print(f"[*] Loaded {len(df)} users from CSV")
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=[
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("join_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("verified_neighborhood", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("age_group", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("device_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("user_segment", "STRING", mode="NULLABLE"),
        ]
    )
    
    # Load data
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job to complete
    
    print(f"[OK] Loaded {len(df)} users to {table_id}")


def load_events_data(client: bigquery.Client, csv_path: str, dataset_id: str = "analytics"):
    """
    Load events data from CSV to BigQuery
    
    Args:
        client: BigQuery client
        csv_path: Path to events CSV file
        dataset_id: Dataset name
    """
    table_id = f"{client.project}.{dataset_id}.events"
    
    print(f"[*] Loading events data from {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Convert timestamp column
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    
    # Convert integer columns (handle NaN)
    if 'message_length' in df.columns:
        df['message_length'] = df['message_length'].fillna(0).astype('Int64')
    
    print(f"[*] Loaded {len(df)} events from CSV")
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=[
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("ab_group", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("item_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("search_query", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("message_length", "INTEGER", mode="NULLABLE"),
        ]
    )
    
    # Load data
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job to complete
    
    print(f"[OK] Loaded {len(df)} events to {table_id}")


def verify_data(client: bigquery.Client, dataset_id: str = "analytics"):
    """
    Verify loaded data with sample queries
    
    Args:
        client: BigQuery client
        dataset_id: Dataset name
    """
    print(f"\n[*] Verifying loaded data...")
    
    # Query users count
    query = f"""
    SELECT COUNT(*) as user_count
    FROM `{client.project}.{dataset_id}.users`
    """
    result = client.query(query).result()
    user_count = list(result)[0]['user_count']
    print(f"[OK] Users table: {user_count} rows")
    
    # Query events count
    query = f"""
    SELECT COUNT(*) as event_count
    FROM `{client.project}.{dataset_id}.events`
    """
    result = client.query(query).result()
    event_count = list(result)[0]['event_count']
    print(f"[OK] Events table: {event_count} rows")
    
    # Query event type distribution
    query = f"""
    SELECT event_type, COUNT(*) as count
    FROM `{client.project}.{dataset_id}.events`
    GROUP BY event_type
    ORDER BY count DESC
    """
    result = client.query(query).result()
    print(f"\n[*] Event type distribution:")
    for row in result:
        print(f"    {row['event_type']}: {row['count']}")


def main():
    """Main loading function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load data to BigQuery')
    parser.add_argument('--project-id', type=str, help='GCP Project ID',
                       default=os.getenv('GCP_PROJECT_ID'))
    parser.add_argument('--credentials', type=str, help='Path to service account key file',
                       default=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account-key.json'))
    parser.add_argument('--dataset', type=str, default='analytics', help='Dataset name')
    parser.add_argument('--data-dir', type=str, default='data', help='Directory containing CSV files')
    parser.add_argument('--test', action='store_true', help='Generate test data if CSV files not found')
    
    args = parser.parse_args()
    
    if not args.project_id:
        print("[ERROR] Project ID is required. Set GCP_PROJECT_ID environment variable or use --project-id")
        sys.exit(1)
    
    print(f"[*] Loading data to BigQuery project: {args.project_id}")
    print(f"[*] Dataset: {args.dataset}")
    
    # Create client
    try:
        client = get_bigquery_client(args.project_id, args.credentials)
        print(f"[OK] Connected to BigQuery")
    except Exception as e:
        print(f"[ERROR] Failed to connect to BigQuery: {e}")
        sys.exit(1)
    
    # Find CSV files
    today = datetime.now().strftime("%Y%m%d")
    users_csv = os.path.join(args.data_dir, f'users_{today}.csv')
    events_csv = os.path.join(args.data_dir, f'events_{today}.csv')
    
    # Check if files exist, if not and --test flag, generate them
    if not os.path.exists(users_csv) or not os.path.exists(events_csv):
        if args.test:
            print(f"[*] CSV files not found, generating test data...")
            os.system(f"python scripts/generate_data.py --users 100 --output {args.data_dir}")
        else:
            print(f"[ERROR] CSV files not found in {args.data_dir}")
            print(f"Expected: {users_csv} and {events_csv}")
            print(f"Run 'python scripts/generate_data.py' first, or use --test flag")
            sys.exit(1)
    
    # Load data
    try:
        load_users_data(client, users_csv, args.dataset)
        load_events_data(client, events_csv, args.dataset)
        verify_data(client, args.dataset)
        
        print(f"\n[OK] Data loading complete!")
        print(f"\nNext steps:")
        print(f"  1. View data in BigQuery Console: https://console.cloud.google.com/bigquery")
        print(f"  2. Run analysis queries in Google Colab")
        print(f"  3. Create Looker Studio dashboard")
        
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
