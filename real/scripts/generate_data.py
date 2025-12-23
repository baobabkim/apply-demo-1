"""
Main script to generate synthetic data for C2C marketplace analysis
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.generator.users import UserGenerator
from src.generator.events import EventGenerator


def generate_data(num_users: int = 1000, output_dir: str = 'data'):
    """
    Generate synthetic user and event data
    
    Args:
        num_users: Number of users to generate
        output_dir: Directory to save output files
    """
    print(f"[*] Starting data generation for {num_users} users...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate users
    print("\n[*] Generating user profiles...")
    user_gen = UserGenerator(seed=42)
    users_df = user_gen.generate_users(num_users=num_users)
    users_df = user_gen.generate_user_segments(users_df)
    
    print(f"[OK] Generated {len(users_df)} users")
    print(f"   - Verified neighborhood: {users_df['verified_neighborhood'].sum()} ({users_df['verified_neighborhood'].mean()*100:.1f}%)")
    print(f"   - Segments: {dict(users_df['user_segment'].value_counts())}")
    
    # Generate events
    print("\n[*] Generating user events...")
    event_gen = EventGenerator(seed=42)
    events_df = event_gen.generate_events_for_users(
        users_df,
        events_per_user_range=(2, 10),
        days_range=30
    )
    
    print(f"[OK] Generated {len(events_df)} events")
    print(f"   - Event types: {dict(events_df['event_type'].value_counts())}")
    print(f"   - A/B groups: {dict(events_df['ab_group'].value_counts())}")
    
    # Calculate funnel conversion rates
    print("\n[*] Funnel Analysis:")
    event_counts = events_df['event_type'].value_counts()
    
    page_views = event_counts.get('page_view', 0)
    searches = event_counts.get('search', 0)
    item_views = event_counts.get('item_view', 0)
    chat_clicks = event_counts.get('chat_click', 0)
    chat_sends = event_counts.get('chat_send', 0)
    
    if page_views > 0:
        print(f"   Page View → Search: {searches/page_views*100:.1f}%")
    if searches > 0:
        print(f"   Search → Item View: {item_views/searches*100:.1f}%")
    if item_views > 0:
        print(f"   Item View -> Chat Click: {chat_clicks/item_views*100:.1f}% [!] BOTTLENECK")
    if chat_clicks > 0:
        print(f"   Chat Click → Chat Send: {chat_sends/chat_clicks*100:.1f}%")
    
    # Save to CSV
    users_file = os.path.join(output_dir, f'users_{datetime.now().strftime("%Y%m%d")}.csv')
    events_file = os.path.join(output_dir, f'events_{datetime.now().strftime("%Y%m%d")}.csv')
    
    users_df.to_csv(users_file, index=False, encoding='utf-8-sig')
    events_df.to_csv(events_file, index=False, encoding='utf-8-sig')
    
    print(f"\n[OK] Data saved:")
    print(f"   - Users: {users_file}")
    print(f"   - Events: {events_file}")
    
    return users_df, events_df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic C2C marketplace data')
    parser.add_argument('--users', type=int, default=1000, help='Number of users to generate')
    parser.add_argument('--output', type=str, default='data', help='Output directory')
    
    args = parser.parse_args()
    
    users_df, events_df = generate_data(num_users=args.users, output_dir=args.output)
