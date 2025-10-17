#!/bin/bash

# Navigate to your Django project directory (if not already there)


# Activate your virtual environment if you have one
source ../myenv/bin/activate

# Run the Django shell command to create badges
python manage.py shell << EOF
from authentication.models import Badge

# List of badges to be created
badges = [
    {'name': 'Lone Wolf', 'description': 'Complete 5 morning motivation sessions', 'points_required': 100},
    {'name': 'Tracker', 'description': 'Log in for 7 consecutive days', 'points_required': 200},
    {'name': 'Hunter', 'description': 'Share 10 quotes on social media', 'points_required': 300},
    {'name': 'Stalker', 'description': 'Read 20 fitness motivation quotes', 'points_required': 400},
    {'name': 'Pack Wolf', 'description': 'Complete the business motivation series', 'points_required': 500},
    {'name': 'Enforcer', 'description': 'Reach top 10 on the leaderboard', 'points_required': 1000},
    {'name': 'Beta Wolf', 'description': 'Read 10 late-night quotes after 10pm', 'points_required': 1500},
    {'name': 'Silver Alpha', 'description': 'Encourage 5 friends to join', 'points_required': 2000},
    {'name': 'Shadow Alpha', 'description': 'Reach level 40', 'points_required': 3000},
    {'name': 'Alpha Wolf', 'description': 'Stay Premium for 1 full year', 'points_required': 4000},
]

# Create badges if they don't exist
for badge_data in badges:
    Badge.objects.get_or_create(**badge_data)
    print(f"Created badge: {badge_data['name']}")

EOF

echo "Badges creation process completed!"
