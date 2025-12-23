"""
User Profile Data Generator

This module generates synthetic user profile data for the C2C marketplace
using the Faker library.
"""

from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import uuid


class UserGenerator:
    """Generate synthetic user profile data"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize the user generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.fake = Faker('ko_KR')  # Korean locale for realistic Korean names/locations
        Faker.seed(seed)
        np.random.seed(seed)
    
    def generate_users(self, num_users: int = 1000, 
                       start_date: datetime = None,
                       end_date: datetime = None) -> pd.DataFrame:
        """
        Generate user profile data
        
        Args:
            num_users: Number of users to generate
            start_date: Start date for user registration (default: 90 days ago)
            end_date: End date for user registration (default: today)
            
        Returns:
            DataFrame with user profile data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=90)
        if end_date is None:
            end_date = datetime.now()
        
        users = []
        
        for _ in range(num_users):
            user_id = str(uuid.uuid4())
            
            # Generate join date within the specified range
            days_between = (end_date - start_date).days
            random_days = np.random.randint(0, days_between + 1)
            join_date = start_date + timedelta(days=random_days)
            
            # 70% of users verify their neighborhood
            verified_neighborhood = np.random.random() < 0.7
            
            # Generate location (Korean city/district)
            location = self.fake.city()
            
            user = {
                'user_id': user_id,
                'name': self.fake.name(),
                'location': location,
                'join_date': join_date.date(),
                'verified_neighborhood': verified_neighborhood,
                'created_at': join_date,
                # Additional metadata for analysis
                'age_group': np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'], 
                                             p=[0.15, 0.35, 0.25, 0.15, 0.10]),
                'device_type': np.random.choice(['iOS', 'Android'], p=[0.45, 0.55])
            }
            
            users.append(user)
        
        df = pd.DataFrame(users)
        
        # Sort by join_date for realistic chronological data
        df = df.sort_values('join_date').reset_index(drop=True)
        
        return df
    
    def generate_user_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add user segmentation based on behavior patterns
        
        Args:
            df: DataFrame with user data
            
        Returns:
            DataFrame with added segment column
        """
        # Define user segments based on engagement likelihood
        segments = []
        
        for _, row in df.iterrows():
            # Higher engagement if verified neighborhood
            base_engagement = 0.5 if row['verified_neighborhood'] else 0.3
            
            # Age groups have different engagement patterns
            age_multiplier = {
                '18-24': 1.2,
                '25-34': 1.3,
                '35-44': 1.0,
                '45-54': 0.8,
                '55+': 0.6
            }
            
            engagement_score = base_engagement * age_multiplier.get(row['age_group'], 1.0)
            
            # Categorize into segments
            if engagement_score > 0.7:
                segment = 'high_engagement'
            elif engagement_score > 0.4:
                segment = 'medium_engagement'
            else:
                segment = 'low_engagement'
            
            segments.append(segment)
        
        df['user_segment'] = segments
        
        return df


def main():
    """Test the user generator"""
    generator = UserGenerator(seed=42)
    
    # Generate 1000 users
    users_df = generator.generate_users(num_users=1000)
    users_df = generator.generate_user_segments(users_df)
    
    print("Generated Users Sample:")
    print(users_df.head(10))
    print(f"\nTotal users: {len(users_df)}")
    print(f"\nVerified neighborhood: {users_df['verified_neighborhood'].sum()} ({users_df['verified_neighborhood'].mean()*100:.1f}%)")
    print(f"\nUser segments distribution:")
    print(users_df['user_segment'].value_counts())
    
    return users_df


if __name__ == "__main__":
    users_df = main()
