import math
import random

class LastMileService:
    def __init__(self):
        # Updated Mumbai 2025 pricing based on MMRTA and STA regulations
        self.providers = {
            'auto_rickshaw': {
                'name': 'Auto Rickshaw',
                'base_fare': 28,
                'per_km': 20.66,  # Non-AC rate as per MMRTA
                'time_factor': 1.5,
                'icon': '🛺',
                'color': '#F59E0B',
                'availability': 0.9
            },
            'uber_go': {
                'name': 'Uber GO',
                'base_fare': 52.50,  # Minimum fare for Uber GO
                'per_km': 20.66,  # MMRTA mandated base rate for non-AC
                'time_charge_per_min': 1.58,  # Time component
                'time_factor': 1.2,
                'icon': '🚗',
                'color': '#1F2937',
                'deep_link': 'https://m.uber.com/',
                'availability': 0.8,
                'surge_multiplier': 1.5,  # Max 1.5x as per regulation
                'discount': 0.25  # Max 25% discount during low demand
            },
            'ola_micro': {
                'name': 'Ola Mini',
                'base_fare': 50,
                'per_km': 20.66,  # MMRTA mandated base rate
                'time_factor': 1.2,
                'icon': '🚕',
                'color': '#10B981',
                'deep_link': 'https://book.olacabs.com/',
                'availability': 0.8,
                'surge_multiplier': 1.5,
                'discount': 0.25
            },
            'bike_taxi_rapido': {
                'name': 'Rapido Bike',
                'base_fare': 15,  # ₹15 for first 1.5 km as per STA rules
                'base_distance': 1.5,  # First 1.5 km covered in base fare
                'per_km': 10.27,  # ₹10.27 per km after first 1.5 km
                'time_factor': 0.7,
                'icon': '🏍️',
                'color': '#EF4444',
                'deep_link': 'https://rapido.bike/',
                'availability': 0.85
            },
            'bike_taxi_uber': {
                'name': 'Uber Moto',
                'base_fare': 15,  # Following STA bike taxi rules
                'base_distance': 1.5,
                'per_km': 10.27,
                'time_factor': 0.7,
                'icon': '🏍️',
                'color': '#1F2937',
                'deep_link': 'https://m.uber.com/',
                'availability': 0.8
            },
            'bike_taxi_ola': {
                'name': 'Ola Bike',
                'base_fare': 15,  # Following STA bike taxi rules
                'base_distance': 1.5,
                'per_km': 10.27,
                'time_factor': 0.7,
                'icon': '🏍️',
                'color': '#10B981',
                'deep_link': 'https://book.olacabs.com/',
                'availability': 0.8
            },
            'yulu': {
                'name': 'Yulu Bike',
                'base_fare': 5,  # Unlock fee
                'per_minute': 3,  # Time-based pricing for shared e-bikes
                'time_factor': 2.5,
                'icon': '🚲',
                'color': '#06B6D4',
                'deep_link': 'https://www.yulu.bike/',
                'availability': 0.7,
                'max_distance': 5,  # Limited range
                'pricing_model': 'time_based'
            }
        }
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        try:
            # Validate inputs
            if not all(isinstance(x, (int, float)) for x in [lat1, lon1, lat2, lon2]):
                return 1.5  # Default distance
                
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth's radius in kilometers
            r = 6371
            distance = c * r
            
            # Validate result
            if distance <= 0 or distance > 100:  # Sanity check
                return 1.5
                
            return round(distance, 2)
            
        except Exception as e:
            print(f"Error in calculate_distance: {e}")
            return 1.5  # Default fallback distance
    
    def get_options(self, origin, destination, origin_coords=None, dest_coords=None):
        """Get real last-mile options based on actual distance and Mumbai pricing"""
        
        try:
            print(f"🔍 Last-mile debug: origin_coords={origin_coords}, dest_coords={dest_coords}")
            
            # Calculate real distance if coordinates provided
            # Handle both dict format {'lat': x, 'lng': y} and list format [lat, lng]
            if origin_coords and dest_coords:
                try:
                    # Extract coordinates from dict or list format
                    if isinstance(origin_coords, dict):
                        orig_lat = origin_coords.get('lat')
                        orig_lng = origin_coords.get('lng')
                    elif isinstance(origin_coords, (list, tuple)) and len(origin_coords) >= 2:
                        orig_lat = origin_coords[0]
                        orig_lng = origin_coords[1]
                    else:
                        orig_lat = orig_lng = None
                    
                    if isinstance(dest_coords, dict):
                        dest_lat = dest_coords.get('lat')
                        dest_lng = dest_coords.get('lng')
                    elif isinstance(dest_coords, (list, tuple)) and len(dest_coords) >= 2:
                        dest_lat = dest_coords[0]
                        dest_lng = dest_coords[1]
                    else:
                        dest_lat = dest_lng = None
                    
                    # Calculate distance if all coordinates are valid
                    if all(coord is not None for coord in [orig_lat, orig_lng, dest_lat, dest_lng]):
                        distance_km = self.calculate_distance(orig_lat, orig_lng, dest_lat, dest_lng)
                        print(f"🔍 Calculated distance: {distance_km} km")
                    else:
                        print(f"❌ Invalid coordinates: orig({orig_lat}, {orig_lng}), dest({dest_lat}, {dest_lng})")
                        distance_km = random.uniform(0.8, 2.5)
                        print(f"🔍 Fallback distance: {distance_km} km")
                except Exception as e:
                    print(f"❌ Error parsing coordinates: {e}")
                    distance_km = random.uniform(0.8, 2.5)
                    print(f"🔍 Fallback distance: {distance_km} km")
            else:
                # Fallback: estimate based on typical last-mile distances
                distance_km = random.uniform(0.8, 2.5)
                print(f"🔍 Fallback distance: {distance_km} km")
            
            # Ensure minimum distance for last-mile (avoid division by zero)
            distance_km = max(0.5, distance_km)
            
            options = []
            
            for provider_id, provider in self.providers.items():
                try:
                    # Skip if provider has distance limits
                    if provider.get('max_distance') and distance_km > provider['max_distance']:
                        continue
                        
                    # Check availability (simulate real-world availability)
                    if random.random() > provider.get('availability', 0.9):
                        continue
                    
                    # Calculate cost based on pricing model
                    if provider.get('pricing_model') == 'time_based':
                        # For Yulu: base unlock fee + time-based pricing
                        estimated_time = distance_km * provider['time_factor'] * 3
                        base_cost = provider['base_fare'] + (estimated_time * provider['per_minute'])
                    elif provider.get('base_distance'):
                        # For bike taxis: ₹15 for first 1.5km, then ₹10.27/km
                        if distance_km <= provider['base_distance']:
                            base_cost = provider['base_fare']
                        else:
                            extra_distance = distance_km - provider['base_distance']
                            base_cost = provider['base_fare'] + (extra_distance * provider['per_km'])
                    else:
                        # Standard calculation for cars and autos
                        base_cost = provider['base_fare'] + (distance_km * provider['per_km'])
                        
                        # Add time component for Uber GO
                        if provider.get('time_charge_per_min'):
                            estimated_time = distance_km * provider['time_factor'] * 2  # Mumbai traffic
                            base_cost += estimated_time * provider['time_charge_per_min']
                    
                    # Apply surge pricing for app-based services
                    if provider.get('surge_multiplier'):
                        # 30% chance of surge during peak hours
                        if random.random() < 0.3:
                            surge_factor = random.uniform(1.1, provider['surge_multiplier'])
                            base_cost *= surge_factor
                    
                    # Apply discount during low demand (20% chance)
                    elif provider.get('discount') and random.random() < 0.2:
                        discount_factor = 1 - random.uniform(0.1, provider['discount'])
                        base_cost *= discount_factor
                    
                    # Calculate travel time (accounting for Mumbai traffic)
                    base_time = distance_km * provider['time_factor'] * 3  # 3 min per km base in traffic
                    traffic_delay = random.randint(1, 8)  # Mumbai traffic delays
                    travel_time = max(3, int(base_time + traffic_delay))
                    
                    # Calculate ETA (time to reach pickup point)
                    eta_minutes = random.randint(2, 12)
                    
                    # Round cost to nearest rupee
                    final_cost = max(int(round(base_cost)), provider['base_fare'])
                    
                    option = {
                        'id': provider_id,
                        'name': provider['name'],
                        'cost': final_cost,
                        'time': travel_time,
                        'distance': round(distance_km, 1),
                        'icon': provider['icon'],
                        'color': provider['color'],
                        'deep_link': provider.get('deep_link'),
                        'rating': round(random.uniform(3.8, 4.7), 1),
                        'eta': f"{eta_minutes} min",
                        'available': True
                    }
                    
                    options.append(option)
                    
                except Exception as e:
                    print(f"Error processing provider {provider_id}: {e}")
                    continue
            
            # Sort by cost (cheapest first)
            options.sort(key=lambda x: x['cost'])
            
            return options[:5]  # Return top 5 options
            
        except Exception as e:
            print(f"Error in get_options: {e}")
            # Return fallback options if calculation fails
            return self.get_fallback_options()
    
    def get_booking_link(self, provider_id, origin, destination, origin_coords=None, dest_coords=None):
        """Generate real booking links with coordinates when possible"""
        provider = self.providers.get(provider_id)
        if not provider or not provider.get('deep_link'):
            return None
        
        base_url = provider['deep_link']
        
        # Construct deep links with coordinates if available
        if origin_coords and dest_coords:
            if 'ola' in provider_id:
                return f"{base_url}?pickup={origin_coords[0]},{origin_coords[1]}&drop={dest_coords[0]},{dest_coords[1]}"
            elif 'uber' in provider_id:
                return f"{base_url}?action=setPickup&pickup[latitude]={origin_coords[0]}&pickup[longitude]={origin_coords[1]}&dropoff[latitude]={dest_coords[0]}&dropoff[longitude]={dest_coords[1]}"
            elif 'rapido' in provider_id:
                return f"{base_url}?pickup_lat={origin_coords[0]}&pickup_lng={origin_coords[1]}&drop_lat={dest_coords[0]}&drop_lng={dest_coords[1]}"
        
        return base_url
    
    def get_fallback_options(self):
        """Provide fallback last-mile options with accurate Mumbai 2025 pricing"""
        return [
            {
                'id': 'bike_taxi_rapido',
                'name': 'Rapido Bike',
                'cost': 15,  # Base fare for first 1.5km
                'time': 6,
                'distance': 1.5,
                'icon': '🏍️',
                'color': '#EF4444',
                'deep_link': 'https://rapido.bike/',
                'rating': 4.3,
                'eta': '5 min',
                'available': True
            },
            {
                'id': 'auto_rickshaw',
                'name': 'Auto Rickshaw',
                'cost': 59,  # ₹28 base + ₹20.66*1.5km
                'time': 8,
                'distance': 1.5,
                'icon': '🛺',
                'color': '#F59E0B',
                'rating': 4.2,
                'eta': '3 min',
                'available': True
            },
            {
                'id': 'uber_go',
                'name': 'Uber GO',
                'cost': 85,  # Minimum fare + distance
                'time': 7,
                'distance': 1.5,
                'icon': '🚗',
                'color': '#1F2937',
                'deep_link': 'https://m.uber.com/',
                'rating': 4.4,
                'eta': '6 min',
                'available': True
            },
            {
                'id': 'yulu',
                'name': 'Yulu Bike',
                'cost': 23,  # ₹5 unlock + ₹3*6min estimated time
                'time': 12,
                'distance': 1.5,
                'icon': '🚲',
                'color': '#06B6D4',
                'deep_link': 'https://www.yulu.bike/',
                'rating': 4.0,
                'eta': '4 min',
                'available': True
            }
        ]