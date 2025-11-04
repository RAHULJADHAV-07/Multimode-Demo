class UserProfileManager:
    def __init__(self):
        self.profiles = {
            'budget': {
                'name': 'Budget Traveler',
                'description': 'Minimize cost, okay with more transfers',
                'max_transfers': 3,
                'time_tolerance': 0.4,  # 40% slower than fastest is okay
                'transfer_preference': 0.2,
                'time_preference': 0.2,
                'cost_preference': 0.5,  # Cost is most important
                'eco_preference': 0.1,
                'icon': '💰',
                'color': '#10B981'  # Green
            },
            'comfort': {
                'name': 'Comfort Seeker',
                'description': 'Fewer transfers, reasonable time',
                'max_transfers': 2,
                'time_tolerance': 0.2,  # Only 20% slower than fastest
                'transfer_preference': 0.5,  # Transfers matter most
                'time_preference': 0.3,
                'cost_preference': 0.1,
                'eco_preference': 0.1,
                'icon': '🛋️',
                'color': '#3B82F6'  # Blue
            },
            'eco': {
                'name': 'Eco Warrior',
                'description': 'Maximize walking, minimize carbon footprint',
                'max_transfers': 2,
                'time_tolerance': 0.5,  # Time is less important
                'transfer_preference': 0.2,
                'time_preference': 0.1,
                'cost_preference': 0.2,
                'eco_preference': 0.5,  # Eco is most important
                'icon': '🌱',
                'color': '#059669'  # Emerald
            },
            'accessibility': {
                'name': 'Accessible Routes',
                'description': 'Wheelchair friendly, minimal transfers',
                'max_transfers': 1,  # Very few transfers
                'time_tolerance': 0.6,  # Time is flexible
                'transfer_preference': 0.6,  # Transfers are critical
                'time_preference': 0.2,
                'cost_preference': 0.1,
                'eco_preference': 0.1,
                'icon': '♿',
                'color': '#7C3AED'  # Purple
            }
        }
    
    def get_profile(self, profile_type):
        """Get profile configuration by type"""
        return self.profiles.get(profile_type, self.profiles['comfort'])
    
    def get_all_profiles(self):
        """Get all available profiles for frontend"""
        return {
            key: {
                'name': profile['name'],
                'description': profile['description'],
                'icon': profile['icon'],
                'color': profile['color']
            }
            for key, profile in self.profiles.items()
        }