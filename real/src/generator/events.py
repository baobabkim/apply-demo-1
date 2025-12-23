"""
Event Log Data Generator

This module generates synthetic user behavior event logs for the C2C marketplace,
including funnel events and A/B test group assignments.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import uuid


class EventGenerator:
    """Generate synthetic user behavior event logs"""
    
    # Event types in the funnel
    EVENT_TYPES = [
        'page_view',      # User views main page
        'search',         # User performs search
        'item_view',      # User views item detail page
        'chat_click',     # User clicks chat button
        'chat_send'       # User sends actual chat message
    ]
    
    # Funnel conversion rates (baseline)
    FUNNEL_RATES = {
        'page_view_to_search': 0.60,      # 60% of viewers search
        'search_to_item_view': 0.75,      # 75% of searchers view items
        'item_view_to_chat_click': 0.25,  # 25% click chat (KEY BOTTLENECK)
        'chat_click_to_chat_send': 0.80   # 80% who click actually send
    }
    
    def __init__(self, seed: int = 42):
        """
        Initialize the event generator
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.seed = seed
    
    def assign_ab_group(self, user_id: str) -> str:
        """
        Assign user to A/B test group (deterministic based on user_id)
        
        Args:
            user_id: User identifier
            
        Returns:
            'control' or 'treatment'
        """
        # Use hash of user_id for consistent assignment
        hash_val = hash(user_id)
        
        # 40% in experiment (20% control, 20% treatment), 60% not in experiment
        mod_val = hash_val % 100
        
        if mod_val < 20:
            return 'control'
        elif mod_val < 40:
            return 'treatment'
        else:
            return 'none'  # Not in experiment
    
    def generate_user_session(self, user_id: str, user_segment: str,
                              session_start: datetime, ab_group: str) -> List[Dict]:
        """
        Generate events for a single user session
        
        Args:
            user_id: User identifier
            user_segment: User engagement segment
            session_start: Session start timestamp
            ab_group: A/B test group assignment
            
        Returns:
            List of event dictionaries
        """
        events = []
        session_id = str(uuid.uuid4())
        current_time = session_start
        
        # Adjust conversion rates based on user segment
        segment_multiplier = {
            'high_engagement': 1.3,
            'medium_engagement': 1.0,
            'low_engagement': 0.7
        }
        multiplier = segment_multiplier.get(user_segment, 1.0)
        
        # Treatment group gets boost in chat_click conversion
        treatment_boost = 1.4 if ab_group == 'treatment' else 1.0
        
        # Event 1: Page view (always happens)
        events.append(self._create_event(
            user_id, session_id, 'page_view', current_time, ab_group
        ))
        current_time += timedelta(seconds=np.random.randint(5, 30))
        
        # Event 2: Search (probabilistic)
        if np.random.random() < self.FUNNEL_RATES['page_view_to_search'] * multiplier:
            events.append(self._create_event(
                user_id, session_id, 'search', current_time, ab_group,
                extra_data={'search_query': self._generate_search_query()}
            ))
            current_time += timedelta(seconds=np.random.randint(3, 15))
            
            # Event 3: Item view (probabilistic)
            if np.random.random() < self.FUNNEL_RATES['search_to_item_view'] * multiplier:
                item_id = str(uuid.uuid4())
                events.append(self._create_event(
                    user_id, session_id, 'item_view', current_time, ab_group,
                    extra_data={'item_id': item_id}
                ))
                current_time += timedelta(seconds=np.random.randint(10, 60))
                
                # Event 4: Chat click (KEY CONVERSION POINT - affected by A/B test)
                chat_click_rate = self.FUNNEL_RATES['item_view_to_chat_click'] * multiplier * treatment_boost
                if np.random.random() < chat_click_rate:
                    events.append(self._create_event(
                        user_id, session_id, 'chat_click', current_time, ab_group,
                        extra_data={'item_id': item_id}
                    ))
                    current_time += timedelta(seconds=np.random.randint(2, 10))
                    
                    # Event 5: Chat send (probabilistic)
                    if np.random.random() < self.FUNNEL_RATES['chat_click_to_chat_send'] * multiplier:
                        events.append(self._create_event(
                            user_id, session_id, 'chat_send', current_time, ab_group,
                            extra_data={'item_id': item_id, 'message_length': np.random.randint(10, 200)}
                        ))
        
        return events
    
    def _create_event(self, user_id: str, session_id: str, event_type: str,
                     timestamp: datetime, ab_group: str, extra_data: Dict = None) -> Dict:
        """Create a single event dictionary"""
        event = {
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': session_id,
            'event_type': event_type,
            'event_timestamp': timestamp,
            'ab_group': ab_group
        }
        
        if extra_data:
            event.update(extra_data)
        
        return event
    
    def _generate_search_query(self) -> str:
        """Generate realistic search queries"""
        queries = [
            '아이폰', '노트북', '자전거', '책상', '의자', '냉장고', '세탁기',
            '에어컨', '선풍기', '전자레인지', '청소기', '운동화', '패딩',
            '가방', '시계', '카메라', '게임기', '모니터', '키보드', '마우스'
        ]
        return np.random.choice(queries)
    
    def generate_events_for_users(self, users_df: pd.DataFrame,
                                  events_per_user_range: Tuple[int, int] = (1, 5),
                                  days_range: int = 30) -> pd.DataFrame:
        """
        Generate events for all users
        
        Args:
            users_df: DataFrame with user data
            events_per_user_range: Min and max number of sessions per user
            days_range: Number of days to generate events for
            
        Returns:
            DataFrame with event logs
        """
        all_events = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            user_segment = user.get('user_segment', 'medium_engagement')
            join_date = pd.to_datetime(user['join_date'])
            
            # Assign A/B test group
            ab_group = self.assign_ab_group(user_id)
            
            # Generate random number of sessions for this user
            num_sessions = np.random.randint(*events_per_user_range)
            
            for _ in range(num_sessions):
                # Random session start time after join date
                days_since_join = min(days_range, (datetime.now().date() - join_date.date()).days)
                if days_since_join <= 0:
                    continue
                    
                random_day = np.random.randint(0, days_since_join + 1)
                session_date = join_date + timedelta(days=random_day)
                
                # Random hour of the day (weighted towards evening)
                hour = np.random.choice(range(24), p=self._get_hourly_distribution())
                session_start = session_date.replace(
                    hour=hour,
                    minute=np.random.randint(0, 60),
                    second=np.random.randint(0, 60)
                )
                
                # Generate events for this session
                session_events = self.generate_user_session(
                    user_id, user_segment, session_start, ab_group
                )
                all_events.extend(session_events)
        
        # Convert to DataFrame
        events_df = pd.DataFrame(all_events)
        
        # Sort by timestamp
        if len(events_df) > 0:
            events_df = events_df.sort_values('event_timestamp').reset_index(drop=True)
        
        return events_df
    
    def _get_hourly_distribution(self) -> np.ndarray:
        """Get probability distribution for hours of the day"""
        # Higher activity in evening hours (18-23)
        probs = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.01,  # 0-5: very low
            0.02, 0.03, 0.04, 0.04, 0.04, 0.05,  # 6-11: morning
            0.05, 0.04, 0.04, 0.04, 0.05, 0.06,  # 12-17: afternoon
            0.08, 0.09, 0.10, 0.09, 0.07, 0.03   # 18-23: evening peak
        ])
        return probs / probs.sum()  # Normalize


def main():
    """Test the event generator"""
    # First, we need user data - import from users.py
    from .users import UserGenerator
    
    # Generate users
    user_gen = UserGenerator(seed=42)
    users_df = user_gen.generate_users(num_users=100)
    users_df = user_gen.generate_user_segments(users_df)
    
    # Generate events
    event_gen = EventGenerator(seed=42)
    events_df = event_gen.generate_events_for_users(
        users_df,
        events_per_user_range=(2, 8),
        days_range=30
    )
    
    print("Generated Events Sample:")
    print(events_df.head(20))
    print(f"\nTotal events: {len(events_df)}")
    print(f"\nEvent type distribution:")
    print(events_df['event_type'].value_counts())
    print(f"\nA/B group distribution:")
    print(events_df['ab_group'].value_counts())
    
    # Calculate funnel metrics
    print("\n=== Funnel Analysis ===")
    for event_type in EventGenerator.EVENT_TYPES:
        count = len(events_df[events_df['event_type'] == event_type])
        print(f"{event_type}: {count}")
    
    return events_df


if __name__ == "__main__":
    events_df = main()
