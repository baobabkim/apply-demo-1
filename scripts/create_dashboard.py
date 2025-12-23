"""
Dashboard visualization script for C2C marketplace data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'

# Load data
print("[*] Loading data...")
users_df = pd.read_csv('test_data/users_20251223.csv')
events_df = pd.read_csv('test_data/events_20251223.csv')

print(f"[OK] Loaded {len(users_df)} users and {len(events_df)} events")

# Convert timestamps
events_df['event_timestamp'] = pd.to_datetime(events_df['event_timestamp'])
users_df['join_date'] = pd.to_datetime(users_df['join_date'])

# Create dashboard
fig = plt.figure(figsize=(20, 12))
fig.suptitle('C2C Marketplace Analytics Dashboard - Test Data', 
             fontsize=20, fontweight='bold', y=0.98)

# 1. Funnel Analysis
ax1 = plt.subplot(2, 3, 1)
funnel_order = ['page_view', 'search', 'item_view', 'chat_click', 'chat_send']
funnel_counts = events_df['event_type'].value_counts()
funnel_data = [funnel_counts.get(event, 0) for event in funnel_order]

colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
bars = ax1.barh(funnel_order, funnel_data, color=colors, alpha=0.8, edgecolor='black')
ax1.set_xlabel('Number of Events', fontsize=11, fontweight='bold')
ax1.set_title('User Journey Funnel', fontsize=13, fontweight='bold', pad=10)
ax1.invert_yaxis()

for i, (event, count) in enumerate(zip(funnel_order, funnel_data)):
    ax1.text(count, i, f'  {count:,}', va='center', fontsize=10, fontweight='bold')

# 2. Conversion Rates
ax2 = plt.subplot(2, 3, 2)
conversion_rates = []
stage_names = []
for i in range(len(funnel_data) - 1):
    if funnel_data[i] > 0:
        rate = (funnel_data[i + 1] / funnel_data[i]) * 100
        conversion_rates.append(rate)
        stage_names.append(f"{funnel_order[i][:8]}\n→\n{funnel_order[i+1][:8]}")

bar_colors = ['red' if rate < 30 else 'orange' if rate < 60 else 'green' 
              for rate in conversion_rates]
bars = ax2.bar(range(len(conversion_rates)), conversion_rates, 
               color=bar_colors, alpha=0.7, edgecolor='black')
ax2.set_xticks(range(len(conversion_rates)))
ax2.set_xticklabels(stage_names, fontsize=9)
ax2.set_ylabel('Conversion Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Stage-to-Stage Conversion Rates', fontsize=13, fontweight='bold', pad=10)
ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% threshold')

for i, rate in enumerate(conversion_rates):
    ax2.text(i, rate + 2, f'{rate:.1f}%', ha='center', fontsize=10, fontweight='bold')

# 3. A/B Test Results
ax3 = plt.subplot(2, 3, 3)
ab_events = events_df[events_df['ab_group'].isin(['control', 'treatment'])]
ab_summary = []

for group in ['control', 'treatment']:
    group_data = ab_events[ab_events['ab_group'] == group]
    item_views = len(group_data[group_data['event_type'] == 'item_view'])
    chat_clicks = len(group_data[group_data['event_type'] == 'chat_click'])
    rate = (chat_clicks / item_views * 100) if item_views > 0 else 0
    ab_summary.append({'group': group, 'rate': rate})

ab_df = pd.DataFrame(ab_summary)
colors_ab = ['#3498db', '#e74c3c']
bars = ax3.bar(ab_df['group'], ab_df['rate'], color=colors_ab, alpha=0.8, edgecolor='black')
ax3.set_ylabel('Chat Click Rate (%)', fontsize=11, fontweight='bold')
ax3.set_title('A/B Test: Chat Click Rate', fontsize=13, fontweight='bold', pad=10)
ax3.set_ylim(0, max(ab_df['rate']) * 1.3)

for i, (group, rate) in enumerate(zip(ab_df['group'], ab_df['rate'])):
    ax3.text(i, rate + 1, f'{rate:.1f}%', ha='center', fontsize=12, fontweight='bold')

if len(ab_df) == 2:
    lift = ((ab_df.iloc[1]['rate'] - ab_df.iloc[0]['rate']) / ab_df.iloc[0]['rate'] * 100)
    ax3.text(0.5, max(ab_df['rate']) * 1.15, f'Lift: {lift:+.1f}%', 
             ha='center', fontsize=11, fontweight='bold', 
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

# 4. User Segments
ax4 = plt.subplot(2, 3, 4)
segment_counts = users_df['user_segment'].value_counts()
colors_seg = ['#2ecc71', '#f39c12', '#e74c3c']
wedges, texts, autotexts = ax4.pie(segment_counts.values, labels=segment_counts.index,
                                     autopct='%1.1f%%', colors=colors_seg[:len(segment_counts)],
                                     startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
ax4.set_title('User Segment Distribution', fontsize=13, fontweight='bold', pad=10)

# 5. Verification Status
ax5 = plt.subplot(2, 3, 5)
verified_counts = users_df['verified_neighborhood'].value_counts()
colors_ver = ['#2ecc71', '#e74c3c']
labels = ['Verified', 'Not Verified']
bars = ax5.bar(labels, [verified_counts.get(True, 0), verified_counts.get(False, 0)],
               color=colors_ver, alpha=0.8, edgecolor='black')
ax5.set_ylabel('Number of Users', fontsize=11, fontweight='bold')
ax5.set_title('Neighborhood Verification Status', fontsize=13, fontweight='bold', pad=10)

for i, count in enumerate([verified_counts.get(True, 0), verified_counts.get(False, 0)]):
    ax5.text(i, count + 1, f'{count}\n({count/len(users_df)*100:.1f}%)', 
             ha='center', fontsize=10, fontweight='bold')

# 6. Key Metrics Summary
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')

metrics_text = f"""
KEY METRICS SUMMARY
{'='*40}

Total Users: {len(users_df):,}
Total Events: {len(events_df):,}
Events per User: {len(events_df)/len(users_df):.1f}

FUNNEL METRICS
{'='*40}
Page Views: {funnel_data[0]:,}
Searches: {funnel_data[1]:,} ({funnel_data[1]/funnel_data[0]*100:.1f}%)
Item Views: {funnel_data[2]:,} ({funnel_data[2]/funnel_data[1]*100:.1f}%)
Chat Clicks: {funnel_data[3]:,} ({funnel_data[3]/funnel_data[2]*100:.1f}%)
Chat Sends: {funnel_data[4]:,} ({funnel_data[4]/funnel_data[3]*100:.1f}%)

BOTTLENECK IDENTIFIED
{'='*40}
Item View → Chat Click: {funnel_data[3]/funnel_data[2]*100:.1f}%
⚠️ PRIMARY CONVERSION ISSUE

A/B TEST RESULTS
{'='*40}
Control: {ab_df.iloc[0]['rate']:.1f}%
Treatment: {ab_df.iloc[1]['rate']:.1f}%
Lift: {lift:+.1f}%

USER INSIGHTS
{'='*40}
Verified: {verified_counts.get(True, 0)} ({verified_counts.get(True, 0)/len(users_df)*100:.1f}%)
High Engagement: {segment_counts.get('high_engagement', 0)}
Medium Engagement: {segment_counts.get('medium_engagement', 0)}
Low Engagement: {segment_counts.get('low_engagement', 0)}
"""

ax6.text(0.05, 0.95, metrics_text, transform=ax6.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save dashboard
output_file = 'dashboards/analytics_dashboard.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\n[OK] Dashboard saved to: {output_file}")

# Create additional detailed charts
print("\n[*] Creating detailed funnel chart...")
fig2, ax = plt.subplots(figsize=(14, 8))
fig2.patch.set_facecolor('white')
ax.set_facecolor('#f8f9fa')

# Funnel with conversion rates
y_pos = np.arange(len(funnel_order))
bars = ax.barh(y_pos, funnel_data, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

ax.set_yticks(y_pos)
ax.set_yticklabels([f.replace('_', ' ').title() for f in funnel_order], fontsize=12, fontweight='bold')
ax.set_xlabel('Number of Events', fontsize=13, fontweight='bold')
ax.set_title('Detailed User Journey Funnel Analysis', fontsize=16, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels and conversion rates
for i, (count, event) in enumerate(zip(funnel_data, funnel_order)):
    # Count label
    ax.text(count, i, f'  {count:,}', va='center', fontsize=11, fontweight='bold')
    
    # Conversion rate to next stage
    if i < len(funnel_data) - 1 and funnel_data[i] > 0:
        conv_rate = (funnel_data[i + 1] / funnel_data[i]) * 100
        color = 'red' if conv_rate < 30 else 'orange' if conv_rate < 60 else 'green'
        ax.text(max(funnel_data) * 0.7, i + 0.5, f'↓ {conv_rate:.1f}%', 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3))

# Add bottleneck annotation
bottleneck_idx = 2  # item_view to chat_click
ax.annotate('BOTTLENECK!', xy=(funnel_data[bottleneck_idx], bottleneck_idx),
            xytext=(funnel_data[bottleneck_idx] * 1.3, bottleneck_idx - 0.3),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            fontsize=12, fontweight='bold', color='red',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig('dashboards/funnel_detail.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] Detailed funnel saved to: dashboards/funnel_detail.png")

# Create A/B test comparison chart
print("\n[*] Creating A/B test comparison chart...")
fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig3.patch.set_facecolor('white')

# Chart 1: Conversion rates
for i, group in enumerate(['control', 'treatment']):
    group_data = ab_events[ab_events['ab_group'] == group]
    item_views = len(group_data[group_data['event_type'] == 'item_view'])
    chat_clicks = len(group_data[group_data['event_type'] == 'chat_click'])
    rate = (chat_clicks / item_views * 100) if item_views > 0 else 0
    
    color = '#3498db' if group == 'control' else '#e74c3c'
    bar = ax1.bar(i, rate, color=color, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
    ax1.text(i, rate + 1, f'{rate:.1f}%\n({chat_clicks}/{item_views})', 
             ha='center', fontsize=11, fontweight='bold')

ax1.set_xticks([0, 1])
ax1.set_xticklabels(['Control', 'Treatment'], fontsize=12, fontweight='bold')
ax1.set_ylabel('Chat Click Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('A/B Test: Conversion Rate Comparison', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylim(0, max(ab_df['rate']) * 1.4)
ax1.set_facecolor('#f8f9fa')
ax1.grid(axis='y', alpha=0.3)

# Add lift annotation
if len(ab_df) == 2:
    lift = ((ab_df.iloc[1]['rate'] - ab_df.iloc[0]['rate']) / ab_df.iloc[0]['rate'] * 100)
    lift_color = 'green' if lift > 0 else 'red'
    ax1.text(0.5, max(ab_df['rate']) * 1.25, f'Lift: {lift:+.1f}%', 
             ha='center', fontsize=13, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.8', facecolor=lift_color, alpha=0.3))

# Chart 2: Event distribution by group
event_types = ['page_view', 'search', 'item_view', 'chat_click', 'chat_send']
x = np.arange(len(event_types))
width = 0.35

control_counts = [len(ab_events[(ab_events['ab_group'] == 'control') & 
                                (ab_events['event_type'] == et)]) for et in event_types]
treatment_counts = [len(ab_events[(ab_events['ab_group'] == 'treatment') & 
                                  (ab_events['event_type'] == et)]) for et in event_types]

bars1 = ax2.bar(x - width/2, control_counts, width, label='Control', 
                color='#3498db', alpha=0.8, edgecolor='black')
bars2 = ax2.bar(x + width/2, treatment_counts, width, label='Treatment', 
                color='#e74c3c', alpha=0.8, edgecolor='black')

ax2.set_xlabel('Event Type', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Events', fontsize=12, fontweight='bold')
ax2.set_title('Event Distribution by A/B Group', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels([et.replace('_', '\n') for et in event_types], fontsize=9)
ax2.legend(fontsize=11, loc='upper right')
ax2.set_facecolor('#f8f9fa')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('dashboards/ab_test_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] A/B test chart saved to: dashboards/ab_test_comparison.png")

print("\n" + "="*60)
print("DASHBOARD GENERATION COMPLETE!")
print("="*60)
print("\nGenerated files:")
print("  1. dashboards/analytics_dashboard.png - Main dashboard")
print("  2. dashboards/funnel_detail.png - Detailed funnel analysis")
print("  3. dashboards/ab_test_comparison.png - A/B test results")
print("\n" + "="*60)
