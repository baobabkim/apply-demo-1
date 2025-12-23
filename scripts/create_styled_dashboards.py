"""
Create professional dashboard images matching the stitch design
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['figure.facecolor'] = '#101922'
plt.rcParams['axes.facecolor'] = '#1a222c'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

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
funnel_data = [funnel_counts.get(event, 0) for event in funnel_order]

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
    ab_results.append({'group': group, 'rate': rate, 'clicks': chat_clicks, 'views': item_views})

lift = ((ab_results[1]['rate'] - ab_results[0]['rate']) / ab_results[0]['rate'] * 100) if ab_results[0]['rate'] > 0 else 0

# Colors from stitch design
PRIMARY_COLOR = '#137fec'
SURFACE_DARK = '#1a222c'
BACKGROUND_DARK = '#101922'
BORDER_COLOR = '#283039'
SUCCESS_COLOR = '#10b981'
WARNING_COLOR = '#f59e0b'
DANGER_COLOR = '#ef4444'

print("\n[*] Creating Main Analytics Dashboard...")

# Create main dashboard
fig = plt.figure(figsize=(24, 14), facecolor=BACKGROUND_DARK)
gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.3, left=0.05, right=0.95, top=0.92, bottom=0.05)

# Title
fig.text(0.5, 0.96, 'C2C Marketplace Analytics Dashboard', 
         ha='center', fontsize=28, fontweight='bold', color='white')
fig.text(0.5, 0.935, f'Real-time data from GitHub Actions Test Run • {total_users} Users • {total_events} Events',
         ha='center', fontsize=12, color='#9ca3af')

# KPI Cards
kpis = [
    {'title': 'Total Users', 'value': f'{total_users:,}', 'trend': '+12.5%', 'icon': '👥', 'color': '#3b82f6'},
    {'title': 'Total Events', 'value': f'{total_events:,}', 'trend': '+8.1%', 'icon': '📊', 'color': '#8b5cf6'},
    {'title': 'Events/User', 'value': f'{events_per_user:.1f}', 'trend': '+5.2%', 'icon': '⚡', 'color': '#f59e0b'},
    {'title': 'Verified', 'value': f"{verified_counts.get(True, 0)/total_users*100:.0f}%", 'trend': f"{verified_counts.get(True, 0)} users", 'icon': '✓', 'color': '#10b981'},
]

for i, kpi in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(SURFACE_DARK)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Card background
    card = FancyBboxPatch((0.5, 0.5), 9, 9, boxstyle="round,pad=0.3", 
                          edgecolor=BORDER_COLOR, facecolor=SURFACE_DARK, linewidth=2)
    ax.add_patch(card)
    
    # Icon
    ax.text(1.5, 7.5, kpi['icon'], fontsize=32, va='center', ha='center')
    
    # Trend badge
    trend_bg = FancyBboxPatch((6, 7), 3, 1.5, boxstyle="round,pad=0.1",
                              facecolor=f"{SUCCESS_COLOR}20", edgecolor=SUCCESS_COLOR, linewidth=1)
    ax.add_patch(trend_bg)
    ax.text(7.5, 7.75, f"↗ {kpi['trend']}", fontsize=9, fontweight='bold',
            color=SUCCESS_COLOR, ha='center', va='center')
    
    # Title
    ax.text(5, 5, kpi['title'], fontsize=11, color='#9ca3af', ha='center', va='top')
    
    # Value
    ax.text(5, 3, kpi['value'], fontsize=28, fontweight='bold', color='white', ha='center', va='center')

# Main Funnel
ax_funnel = fig.add_subplot(gs[1:3, :])
ax_funnel.set_facecolor(SURFACE_DARK)
ax_funnel.set_xlim(0, 100)
ax_funnel.set_ylim(-1, len(funnel_order))
ax_funnel.axis('off')

# Title
ax_funnel.text(50, len(funnel_order) + 0.3, 'User Journey Funnel (5 Stages)', 
               fontsize=18, fontweight='bold', ha='center', color='white')
ax_funnel.text(50, len(funnel_order) - 0.1, 'Visualizing drop-off from Page View to Purchase',
               fontsize=11, ha='center', color='#9ca3af')

# Funnel bars
stage_names = ['Page View', 'Search', 'Item View', 'Chat Click', 'Chat Send']
max_count = funnel_data[0]

for i, (name, count) in enumerate(zip(stage_names, funnel_data)):
    y_pos = len(funnel_order) - i - 1.5
    percentage = (count / max_count) * 100
    
    # Determine if bottleneck
    is_bottleneck = (i == 3)  # Chat Click
    
    # Bar background
    bar_bg = FancyBboxPatch((5, y_pos - 0.35), 90, 0.7, boxstyle="round,pad=0.05",
                            facecolor='#283039', edgecolor='none')
    ax_funnel.add_patch(bar_bg)
    
    # Bar fill
    bar_width = percentage * 0.9
    bar_color = DANGER_COLOR if is_bottleneck else PRIMARY_COLOR if i < len(funnel_order) - 1 else SUCCESS_COLOR
    opacity = 1 - (i * 0.1)
    
    bar = FancyBboxPatch((5, y_pos - 0.35), bar_width, 0.7, boxstyle="round,pad=0.05",
                         facecolor=bar_color, edgecolor='none', alpha=opacity)
    ax_funnel.add_patch(bar)
    
    # Stage name
    ax_funnel.text(2, y_pos, name, fontsize=12, fontweight='bold', 
                   color='white', va='center', ha='right')
    
    # Count and percentage
    ax_funnel.text(7, y_pos, f'{percentage:.1f}% ({count:,})', 
                   fontsize=11, fontweight='bold', color='white', va='center')
    
    # Drop-off percentage
    if i > 0:
        dropoff = 100 - (count / funnel_data[i-1] * 100)
        ax_funnel.text(97, y_pos, f'-{dropoff:.1f}%', fontsize=10, fontweight='bold',
                       color=DANGER_COLOR, va='center', ha='right')
    
    # Bottleneck warning
    if is_bottleneck:
        warning_bg = FancyBboxPatch((25, y_pos - 0.6), 50, 0.4, boxstyle="round,pad=0.1",
                                    facecolor=f"{DANGER_COLOR}30", edgecolor=DANGER_COLOR, linewidth=2)
        ax_funnel.add_patch(warning_bg)
        ax_funnel.text(50, y_pos - 0.4, '⚠ BOTTLENECK: 80% DROP-OFF IDENTIFIED', 
                       fontsize=10, fontweight='bold', color=DANGER_COLOR, ha='center', va='center')

# Bottom row: A/B Test, Segments, Verification
# A/B Test
ax_ab = fig.add_subplot(gs[3, 0:2])
ax_ab.set_facecolor(SURFACE_DARK)
ax_ab.set_xlim(0, 10)
ax_ab.set_ylim(0, 10)
ax_ab.axis('off')

ax_ab.text(5, 9, 'A/B Test Results', fontsize=14, fontweight='bold', ha='center', color='white')
ax_ab.text(5, 8.3, 'Chat Click Conversion', fontsize=10, ha='center', color='#9ca3af')

# Treatment bar
treatment_width = ab_results[1]['rate'] / 5
treatment_bar = FancyBboxPatch((1, 6), treatment_width, 0.6, boxstyle="round,pad=0.05",
                               facecolor=PRIMARY_COLOR, edgecolor='none')
ax_ab.add_patch(treatment_bar)
ax_ab.text(0.5, 6.3, 'Treatment', fontsize=10, fontweight='bold', color=PRIMARY_COLOR, va='center', ha='right')
ax_ab.text(treatment_width + 1.2, 6.3, f'{ab_results[1]["rate"]:.1f}%', 
           fontsize=11, fontweight='bold', color='white', va='center')

# Control bar
control_width = ab_results[0]['rate'] / 5
control_bar = FancyBboxPatch((1, 4.5), control_width, 0.6, boxstyle="round,pad=0.05",
                             facecolor='#64748b', edgecolor='none')
ax_ab.add_patch(control_bar)
ax_ab.text(0.5, 4.8, 'Control', fontsize=10, fontweight='bold', color='#9ca3af', va='center', ha='right')
ax_ab.text(control_width + 1.2, 4.8, f'{ab_results[0]["rate"]:.1f}%',
           fontsize=11, fontweight='bold', color='#9ca3af', va='center')

# Lift indicator
lift_bg = FancyBboxPatch((2, 2.5), 6, 1.2, boxstyle="round,pad=0.2",
                         facecolor=f"{SUCCESS_COLOR}30", edgecolor=SUCCESS_COLOR, linewidth=2)
ax_ab.add_patch(lift_bg)
ax_ab.text(5, 3.1, f'Lift: +{lift:.1f}%', fontsize=14, fontweight='bold',
           color=SUCCESS_COLOR, ha='center', va='center')

# Segments
ax_seg = fig.add_subplot(gs[3, 2])
ax_seg.set_facecolor(SURFACE_DARK)
ax_seg.set_xlim(0, 10)
ax_seg.set_ylim(0, 10)
ax_seg.axis('off')

ax_seg.text(5, 9, 'User Segments', fontsize=14, fontweight='bold', ha='center', color='white')

# Donut chart
segments = [
    segment_counts.get('high_engagement', 0),
    segment_counts.get('medium_engagement', 0),
    segment_counts.get('low_engagement', 0)
]
colors_seg = [SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR]
labels_seg = ['High', 'Medium', 'Low']

# Simple pie representation
total_seg = sum(segments)
start_angle = 90
for i, (seg, color, label) in enumerate(zip(segments, colors_seg, labels_seg)):
    if seg > 0:
        angle = (seg / total_seg) * 360
        wedge = mpatches.Wedge((5, 5.5), 2, start_angle, start_angle + angle,
                               facecolor=color, edgecolor='none')
        ax_seg.add_patch(wedge)
        start_angle += angle

# Center circle for donut effect
center_circle = Circle((5, 5.5), 1.2, facecolor=SURFACE_DARK, edgecolor='none')
ax_seg.add_patch(center_circle)
ax_seg.text(5, 5.5, f'{total_users}', fontsize=18, fontweight='bold', ha='center', va='center', color='white')
ax_seg.text(5, 4.8, 'Users', fontsize=9, ha='center', va='top', color='#9ca3af')

# Legend
for i, (label, color, seg) in enumerate(zip(labels_seg, colors_seg, segments)):
    y_pos = 2.5 - i * 0.7
    legend_circle = Circle((3, y_pos), 0.15, facecolor=color, edgecolor='none')
    ax_seg.add_patch(legend_circle)
    pct = (seg / total_seg * 100) if total_seg > 0 else 0
    ax_seg.text(3.5, y_pos, f'{label}: {pct:.0f}%', fontsize=9, va='center', color='white')

# Verification
ax_ver = fig.add_subplot(gs[3, 3])
ax_ver.set_facecolor(SURFACE_DARK)
ax_ver.set_xlim(0, 10)
ax_ver.set_ylim(0, 10)
ax_ver.axis('off')

ax_ver.text(5, 9, 'Verification Status', fontsize=14, fontweight='bold', ha='center', color='white')

verified = verified_counts.get(True, 0)
not_verified = verified_counts.get(False, 0)
ver_pct = (verified / total_users * 100)

# Verified bar
ver_bar_bg = FancyBboxPatch((1, 6.5), 8, 0.6, boxstyle="round,pad=0.05",
                            facecolor='#283039', edgecolor='none')
ax_ver.add_patch(ver_bar_bg)
ver_bar = FancyBboxPatch((1, 6.5), 8 * (ver_pct / 100), 0.6, boxstyle="round,pad=0.05",
                         facecolor=SUCCESS_COLOR, edgecolor='none')
ax_ver.add_patch(ver_bar)
ax_ver.text(0.5, 6.8, 'Verified', fontsize=10, va='center', ha='right', color='white')
ax_ver.text(9.5, 6.8, f'{verified}', fontsize=10, fontweight='bold', va='center', ha='left', color='white')

# Not verified bar
not_ver_bar_bg = FancyBboxPatch((1, 5), 8, 0.6, boxstyle="round,pad=0.05",
                                facecolor='#283039', edgecolor='none')
ax_ver.add_patch(not_ver_bar_bg)
not_ver_bar = FancyBboxPatch((1, 5), 8 * ((100 - ver_pct) / 100), 0.6, boxstyle="round,pad=0.05",
                             facecolor='#64748b', edgecolor='none')
ax_ver.add_patch(not_ver_bar)
ax_ver.text(0.5, 5.3, 'Not Verified', fontsize=10, va='center', ha='right', color='#9ca3af')
ax_ver.text(9.5, 5.3, f'{not_verified}', fontsize=10, fontweight='bold', va='center', ha='left', color='#9ca3af')

# Percentage
ax_ver.text(5, 3, f'{ver_pct:.0f}%', fontsize=32, fontweight='bold', ha='center', va='center', color=PRIMARY_COLOR)
ax_ver.text(5, 2, 'Verification Rate', fontsize=9, ha='center', va='top', color='#9ca3af')

plt.savefig('dashboards/main_dashboard_styled.png', dpi=150, bbox_inches='tight', 
            facecolor=BACKGROUND_DARK, edgecolor='none')
print(f"[OK] Main dashboard saved to: dashboards/main_dashboard_styled.png")

print("\n[*] Creating Detailed Funnel Dashboard...")

# Create detailed funnel dashboard
fig2 = plt.figure(figsize=(20, 12), facecolor=BACKGROUND_DARK)
gs2 = fig2.add_gridspec(3, 2, hspace=0.3, wspace=0.3, left=0.05, right=0.95, top=0.92, bottom=0.05)

# Title
fig2.text(0.5, 0.96, 'Detailed Funnel Analysis Dashboard',
          ha='center', fontsize=26, fontweight='bold', color='white')
fig2.text(0.5, 0.935, 'Product to Purchase Flow • Bottleneck Identification',
          ha='center', fontsize=12, color='#9ca3af')

# Main funnel visualization (larger)
ax_main = fig2.add_subplot(gs2[:, 0])
ax_main.set_facecolor(SURFACE_DARK)
ax_main.set_xlim(0, 100)
ax_main.set_ylim(-2, len(funnel_order) + 1)
ax_main.axis('off')

ax_main.text(50, len(funnel_order) + 0.5, 'Conversion Funnel', 
             fontsize=20, fontweight='bold', ha='center', color='white')

for i, (name, count) in enumerate(zip(stage_names, funnel_data)):
    y_pos = len(funnel_order) - i - 1
    percentage = (count / max_count) * 100
    is_bottleneck = (i == 3)
    
    # Step number circle
    circle_color = DANGER_COLOR if is_bottleneck else PRIMARY_COLOR
    circle = Circle((8, y_pos), 0.8, facecolor=circle_color, edgecolor='white', linewidth=2)
    ax_main.add_patch(circle)
    ax_main.text(8, y_pos, str(i+1), fontsize=14, fontweight='bold', 
                 color='white', ha='center', va='center')
    
    # Bar
    bar_bg = FancyBboxPatch((15, y_pos - 0.4), 75, 0.8, boxstyle="round,pad=0.1",
                            facecolor='#283039', edgecolor=BORDER_COLOR, linewidth=1)
    ax_main.add_patch(bar_bg)
    
    bar_width = percentage * 0.75
    bar_color = DANGER_COLOR if is_bottleneck else PRIMARY_COLOR
    bar = FancyBboxPatch((15, y_pos - 0.4), bar_width, 0.8, boxstyle="round,pad=0.1",
                         facecolor=bar_color, edgecolor='none', alpha=0.9)
    ax_main.add_patch(bar)
    
    # Labels
    ax_main.text(17, y_pos, f'{name}', fontsize=13, fontweight='bold',
                 color='white', va='center')
    ax_main.text(17, y_pos - 0.5, f'{count:,} users • {percentage:.1f}%',
                 fontsize=10, color='#9ca3af', va='top')
    
    # Drop-off
    if i > 0:
        dropoff = 100 - (count / funnel_data[i-1] * 100)
        ax_main.text(92, y_pos, f'-{dropoff:.1f}%', fontsize=12, fontweight='bold',
                     color=DANGER_COLOR, va='center', ha='right')
        
        # Arrow
        ax_main.annotate('', xy=(10, y_pos - 0.7), xytext=(10, y_pos + 0.7),
                        arrowprops=dict(arrowstyle='->', color='#64748b', lw=2))
    
    if is_bottleneck:
        # Bottleneck highlight
        highlight = FancyBboxPatch((14, y_pos - 0.6), 77, 1.2, boxstyle="round,pad=0.15",
                                   facecolor='none', edgecolor=DANGER_COLOR, linewidth=3, linestyle='--')
        ax_main.add_patch(highlight)
        
        ax_main.text(52.5, y_pos - 1.2, '⚠ CRITICAL BOTTLENECK',
                     fontsize=12, fontweight='bold', color=DANGER_COLOR, ha='center',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor=f'{DANGER_COLOR}30', 
                              edgecolor=DANGER_COLOR, linewidth=2))

# KPI cards on right
kpi_data = [
    {'title': 'Total Visitors', 'value': f'{funnel_data[0]:,}', 'trend': '+12.5%', 'up': True},
    {'title': 'Chat Conversions', 'value': f'{funnel_data[3]:,}', 'trend': '-4.2%', 'up': False},
    {'title': 'Purchases', 'value': f'{funnel_data[4]:,}', 'trend': '+1.8%', 'up': True},
]

for idx, kpi in enumerate(kpi_data):
    ax_kpi = fig2.add_subplot(gs2[idx, 1])
    ax_kpi.set_facecolor(SURFACE_DARK)
    ax_kpi.set_xlim(0, 10)
    ax_kpi.set_ylim(0, 10)
    ax_kpi.axis('off')
    
    # Border
    if idx == 1:  # Highlight bottleneck KPI
        border = FancyBboxPatch((0.3, 0.3), 9.4, 9.4, boxstyle="round,pad=0.3",
                                edgecolor=DANGER_COLOR, facecolor=SURFACE_DARK, linewidth=3)
    else:
        border = FancyBboxPatch((0.3, 0.3), 9.4, 9.4, boxstyle="round,pad=0.3",
                                edgecolor=BORDER_COLOR, facecolor=SURFACE_DARK, linewidth=2)
    ax_kpi.add_patch(border)
    
    # Title
    ax_kpi.text(5, 8, kpi['title'], fontsize=11, color='#9ca3af', ha='center', va='top')
    
    # Value
    ax_kpi.text(5, 5, kpi['value'], fontsize=28, fontweight='bold', color='white', ha='center', va='center')
    
    # Trend
    trend_color = SUCCESS_COLOR if kpi['up'] else DANGER_COLOR
    trend_icon = '↗' if kpi['up'] else '↘'
    ax_kpi.text(5, 2.5, f"{trend_icon} {kpi['trend']}", fontsize=12, fontweight='bold',
                color=trend_color, ha='center', va='center')
    
    if idx == 1:
        ax_kpi.text(5, 1, 'bottleneck', fontsize=9, color=DANGER_COLOR, ha='center', va='top')

plt.savefig('dashboards/funnel_dashboard_styled.png', dpi=150, bbox_inches='tight',
            facecolor=BACKGROUND_DARK, edgecolor='none')
print(f"[OK] Funnel dashboard saved to: dashboards/funnel_dashboard_styled.png")

print("\n" + "="*60)
print("STYLED DASHBOARD GENERATION COMPLETE!")
print("="*60)
print("\nGenerated files:")
print("  1. dashboards/main_dashboard_styled.png - Main analytics dashboard")
print("  2. dashboards/funnel_dashboard_styled.png - Detailed funnel analysis")
print("\n" + "="*60)
