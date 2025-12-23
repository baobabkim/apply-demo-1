"""
Process test data and generate JSON for dashboard
"""

import pandas as pd
import json
from datetime import datetime

# Load data
print("[*] Loading test data...")
users_df = pd.read_csv('test_data/users_20251223.csv')
events_df = pd.read_csv('test_data/events_20251223.csv')

print(f"[OK] Loaded {len(users_df)} users and {len(events_df)} events")

# Calculate metrics
total_users = len(users_df)
total_events = len(events_df)
events_per_user = total_events / total_users

# Funnel metrics
funnel_order = ['page_view', 'search', 'item_view', 'chat_click', 'chat_send']
funnel_counts = events_df['event_type'].value_counts()
funnel_data = {event: funnel_counts.get(event, 0) for event in funnel_order}

# Calculate conversion rates
conversions = []
for i in range(len(funnel_order) - 1):
    if funnel_data[funnel_order[i]] > 0:
        rate = (funnel_data[funnel_order[i + 1]] / funnel_data[funnel_order[i]]) * 100
        conversions.append({
            'from': funnel_order[i],
            'to': funnel_order[i + 1],
            'rate': round(rate, 1),
            'dropoff': round(100 - rate, 1)
        })

# User segments
segment_counts = users_df['user_segment'].value_counts().to_dict()
verified_counts = users_df['verified_neighborhood'].value_counts().to_dict()

# A/B test data
ab_events = events_df[events_df['ab_group'].isin(['control', 'treatment'])]
ab_results = []

for group in ['control', 'treatment']:
    group_data = ab_events[ab_events['ab_group'] == group]
    item_views = len(group_data[group_data['event_type'] == 'item_view'])
    chat_clicks = len(group_data[group_data['event_type'] == 'chat_click'])
    rate = (chat_clicks / item_views * 100) if item_views > 0 else 0
    ab_results.append({
        'group': group,
        'item_views': item_views,
        'chat_clicks': chat_clicks,
        'conversion_rate': round(rate, 1)
    })

# Calculate lift
if len(ab_results) == 2:
    lift = ((ab_results[1]['conversion_rate'] - ab_results[0]['conversion_rate']) / 
            ab_results[0]['conversion_rate'] * 100) if ab_results[0]['conversion_rate'] > 0 else 0
else:
    lift = 0

# Create dashboard data
dashboard_data = {
    'metadata': {
        'generated_at': datetime.now().isoformat(),
        'data_source': 'GitHub Actions Test Run #20470933138',
        'total_users': total_users,
        'total_events': total_events
    },
    'kpis': {
        'total_users': total_users,
        'total_events': total_events,
        'events_per_user': round(events_per_user, 1),
        'verified_users': verified_counts.get(True, 0),
        'verified_percentage': round(verified_counts.get(True, 0) / total_users * 100, 1)
    },
    'funnel': {
        'stages': [
            {
                'name': 'Page View',
                'count': funnel_data['page_view'],
                'percentage': 100.0,
                'dropoff': 0.0
            },
            {
                'name': 'Search',
                'count': funnel_data['search'],
                'percentage': round(funnel_data['search'] / funnel_data['page_view'] * 100, 1),
                'dropoff': round((1 - funnel_data['search'] / funnel_data['page_view']) * 100, 1)
            },
            {
                'name': 'Item View',
                'count': funnel_data['item_view'],
                'percentage': round(funnel_data['item_view'] / funnel_data['search'] * 100, 1),
                'dropoff': round((1 - funnel_data['item_view'] / funnel_data['search']) * 100, 1)
            },
            {
                'name': 'Chat Click',
                'count': funnel_data['chat_click'],
                'percentage': round(funnel_data['chat_click'] / funnel_data['item_view'] * 100, 1),
                'dropoff': round((1 - funnel_data['chat_click'] / funnel_data['item_view']) * 100, 1),
                'is_bottleneck': True
            },
            {
                'name': 'Chat Send',
                'count': funnel_data['chat_send'],
                'percentage': round(funnel_data['chat_send'] / funnel_data['chat_click'] * 100, 1),
                'dropoff': round((1 - funnel_data['chat_send'] / funnel_data['chat_click']) * 100, 1)
            }
        ]
    },
    'segments': {
        'high_engagement': segment_counts.get('high_engagement', 0),
        'medium_engagement': segment_counts.get('medium_engagement', 0),
        'low_engagement': segment_counts.get('low_engagement', 0)
    },
    'ab_test': {
        'control': ab_results[0] if len(ab_results) > 0 else {},
        'treatment': ab_results[1] if len(ab_results) > 1 else {},
        'lift': round(lift, 1)
    },
    'verification': {
        'verified': verified_counts.get(True, 0),
        'not_verified': verified_counts.get(False, 0),
        'percentage_verified': round(verified_counts.get(True, 0) / total_users * 100, 1)
    }
}

# Save to JSON
output_file = 'dashboards/dashboard_data.json'
with open(output_file, 'w') as f:
    json.dump(dashboard_data, f, indent=2, default=int)

print(f"\n[OK] Dashboard data saved to: {output_file}")
print(f"\n[*] Key Metrics:")
print(f"   Total Users: {total_users}")
print(f"   Total Events: {total_events}")
print(f"   Bottleneck: Item View → Chat Click ({dashboard_data['funnel']['stages'][3]['percentage']}%)")
print(f"   A/B Test Lift: {dashboard_data['ab_test']['lift']}%")
