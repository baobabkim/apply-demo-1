"""
BigQuery Setup Script

This script creates the BigQuery dataset and tables for the C2C marketplace analytics project.
"""

import os
import sys
from google.cloud import bigquery
from google.oauth2 import service_account


def get_bigquery_client(project_id: str = None, credentials_path: str = None):
    """
    Create and return a BigQuery client
    
    Args:
        project_id: GCP project ID (if None, uses environment variable)
        credentials_path: Path to service account key file
        
    Returns:
        BigQuery client
    """
    if credentials_path and os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        client = bigquery.Client(credentials=credentials, project=project_id)
    else:
        # Use default credentials (environment variable or gcloud auth)
        client = bigquery.Client(project=project_id)
    
    return client


def create_dataset(client: bigquery.Client, dataset_id: str = "analytics"):
    """
    Create the analytics dataset
    
    Args:
        client: BigQuery client
        dataset_id: Dataset name
    """
    dataset_ref = f"{client.project}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"[OK] Dataset {dataset_ref} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-northeast3"  # Seoul region
        dataset.description = "C2C Marketplace User Retention Analysis Data"
        
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"[OK] Created dataset {dataset_ref}")


def create_users_table(client: bigquery.Client, dataset_id: str = "analytics"):
    """
    Create the users table with partitioning
    
    Args:
        client: BigQuery client
        dataset_id: Dataset name
    """
    table_id = f"{client.project}.{dataset_id}.users"
    
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Unique user identifier"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="User name"),
        bigquery.SchemaField("location", "STRING", mode="NULLABLE", description="User location (city/district)"),
        bigquery.SchemaField("join_date", "DATE", mode="REQUIRED", description="User registration date"),
        bigquery.SchemaField("verified_neighborhood", "BOOLEAN", mode="REQUIRED", description="Whether user verified their neighborhood"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Record creation timestamp"),
        bigquery.SchemaField("age_group", "STRING", mode="NULLABLE", description="User age group"),
        bigquery.SchemaField("device_type", "STRING", mode="NULLABLE", description="User device type (iOS/Android)"),
        bigquery.SchemaField("user_segment", "STRING", mode="NULLABLE", description="User engagement segment"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    
    # Partition by join_date (DATE)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="join_date",
    )
    
    # Cluster by user_segment and verified_neighborhood for better query performance
    table.clustering_fields = ["user_segment", "verified_neighborhood"]
    
    try:
        client.get_table(table_id)
        print(f"[OK] Table {table_id} already exists")
    except Exception:
        table = client.create_table(table)
        print(f"[OK] Created table {table_id}")
        print(f"    - Partitioned by: join_date (DATE)")
        print(f"    - Clustered by: user_segment, verified_neighborhood")


def create_events_table(client: bigquery.Client, dataset_id: str = "analytics"):
    """
    Create the events table with partitioning
    
    Args:
        client: BigQuery client
        dataset_id: Dataset name
    """
    table_id = f"{client.project}.{dataset_id}.events"
    
    schema = [
        bigquery.SchemaField("event_id", "STRING", mode="REQUIRED", description="Unique event identifier"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="User identifier"),
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED", description="Session identifier"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED", description="Type of event (page_view, search, item_view, chat_click, chat_send)"),
        bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED", description="Event timestamp"),
        bigquery.SchemaField("ab_group", "STRING", mode="REQUIRED", description="A/B test group (control, treatment, none)"),
        bigquery.SchemaField("item_id", "STRING", mode="NULLABLE", description="Item identifier (for item-related events)"),
        bigquery.SchemaField("search_query", "STRING", mode="NULLABLE", description="Search query text"),
        bigquery.SchemaField("message_length", "INTEGER", mode="NULLABLE", description="Chat message length"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    
    # Partition by event_timestamp (TIMESTAMP)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="event_timestamp",
    )
    
    # Cluster by event_type and ab_group for better query performance
    table.clustering_fields = ["event_type", "ab_group"]
    
    try:
        client.get_table(table_id)
        print(f"[OK] Table {table_id} already exists")
    except Exception:
        table = client.create_table(table)
        print(f"[OK] Created table {table_id}")
        print(f"    - Partitioned by: event_timestamp (TIMESTAMP)")
        print(f"    - Clustered by: event_type, ab_group")


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up BigQuery infrastructure')
    parser.add_argument('--project-id', type=str, help='GCP Project ID', 
                       default=os.getenv('GCP_PROJECT_ID'))
    parser.add_argument('--credentials', type=str, help='Path to service account key file',
                       default=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account-key.json'))
    parser.add_argument('--dataset', type=str, default='analytics', help='Dataset name')
    
    args = parser.parse_args()
    
    if not args.project_id:
        print("[ERROR] Project ID is required. Set GCP_PROJECT_ID environment variable or use --project-id")
        sys.exit(1)
    
    print(f"[*] Setting up BigQuery infrastructure for project: {args.project_id}")
    print(f"[*] Dataset: {args.dataset}")
    
    # Create client
    try:
        client = get_bigquery_client(args.project_id, args.credentials)
        print(f"[OK] Connected to BigQuery")
    except Exception as e:
        print(f"[ERROR] Failed to connect to BigQuery: {e}")
        sys.exit(1)
    
    # Create dataset
    print(f"\n[*] Creating dataset...")
    create_dataset(client, args.dataset)
    
    # Create tables
    print(f"\n[*] Creating users table...")
    create_users_table(client, args.dataset)
    
    print(f"\n[*] Creating events table...")
    create_events_table(client, args.dataset)
    
    print(f"\n[OK] BigQuery setup complete!")
    print(f"\nYou can now:")
    print(f"  1. Run 'python scripts/load_data.py' to load data")
    print(f"  2. Query tables in BigQuery Console: https://console.cloud.google.com/bigquery")


if __name__ == "__main__":
    main()
