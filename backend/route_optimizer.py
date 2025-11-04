import requests
import json
from datetime import datetime, timedelta
import os

class RouteOptimizer:
    def __init__(self):
        # Removed OTP server dependency - using only stations.json
        self.stations = self.load_stations()
        self.train_fares = self.initialize_train_fares()
        
    def load_stations(self):
        """Load stations from JSON file"""
        try:
            print("📂 Loading stations from stations.json...")
            # Try different possible paths for stations.json
            possible_paths = [
                '../data/stations.json',
                './data/stations.json',
                'data/stations.json'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"✅ Loaded {len(data)} stations from: {path}")
                        # Convert JSON format to internal format
                        converted_stations = []
                        for station in data:
                            if isinstance(station, dict):
                                # Support both formats:
                                # Format 1: {"label": "Name", "value": "lat,lng"}
                                # Format 2: {"name": "Name", "lat": x, "lng": y, "type": "STATION"}
                                
                                if 'name' in station and 'lat' in station and 'lng' in station:
                                    # Already in correct format (real data)
                                    converted_stations.append(station)
                                elif 'label' in station and 'value' in station:
                                    # Old format - convert it
                                    coords = station['value'].split(',')
                                    if len(coords) == 2:
                                        converted_stations.append({
                                            'name': station['label'],
                                            'lat': float(coords[0]),
                                            'lng': float(coords[1]),
                                            'type': 'STATION'
                                        })
                        return converted_stations
            
            # If no file found, return mock data
            print("⚠️  stations.json not found, using mock data")
            return self.get_mock_stations()
            
        except Exception as e:
            print(f"❌ Error loading stations: {e}")
            return self.get_mock_stations()
    
    def initialize_train_fares(self):
        """Initialize Mumbai train fare data with station-to-station pricing"""
        return {
            # Western Railway (WR) - Key stations and their fare zones
            'WR': {
                'stations': [
                    'Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road', 
                    'Mumbai Central', 'Mahalaxmi', 'Lower Parel', 'Prabhadevi', 
                    'Dadar', 'Matunga', 'Mahim', 'Bandra', 'Khar Road', 'Santacruz',
                    'Vile Parle', 'Andheri', 'Jogeshwari', 'Ram Mandir', 'Goregaon',
                    'Malad', 'Kandivali', 'Borivali', 'Dahisar', 'Mira Road', 'Bhayandar',
                    'Naigaon', 'Vasai Road', 'Nallasopara', 'Virar'
                ],
                'fare_zones': {
                    # Distance-based fare zones for WR
                    ('Churchgate', 'Dadar'): {'2nd': 10, '1st': 40, 'AC': 50},
                    ('Churchgate', 'Andheri'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Churchgate', 'Borivali'): {'2nd': 20, '1st': 85, 'AC': 95},
                    ('Churchgate', 'Virar'): {'2nd': 25, '1st': 100, 'AC': 115},
                    ('Dadar', 'Andheri'): {'2nd': 10, '1st': 35, 'AC': 45},
                    ('Dadar', 'Borivali'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Dadar', 'Virar'): {'2nd': 20, '1st': 85, 'AC': 95},
                    ('Andheri', 'Borivali'): {'2nd': 10, '1st': 30, 'AC': 40},
                    ('Andheri', 'Virar'): {'2nd': 15, '1st': 55, 'AC': 65},
                    ('Borivali', 'Virar'): {'2nd': 10, '1st': 25, 'AC': 35}
                }
            },
            # Central Railway (CR) - Main line stations
            'CR': {
                'stations': [
                    'CSMT', 'Masjid', 'Sandhurst Road', 'Dockyard Road', 'Reay Road',
                    'Cotton Green', 'Sewri', 'Wadala', 'King Circle', 'Mahim',
                    'Dadar', 'Matunga', 'Sion', 'Kurla', 'Vidyavihar', 'Ghatkopar',
                    'Vikhroli', 'Kanjurmarg', 'Bhandup', 'Nahur', 'Mulund',
                    'Thane', 'Kalwa', 'Mumbra', 'Diva', 'Kopar', 'Dombivli',
                    'Thakurli', 'Kalyan', 'Vithalwadi', 'Ulhasnagar', 'Ambernath'
                ],
                'fare_zones': {
                    ('CSMT', 'Dadar'): {'2nd': 5, '1st': 25, 'AC': 35},
                    ('CSMT', 'Kurla'): {'2nd': 10, '1st': 50, 'AC': 70},
                    ('CSMT', 'Thane'): {'2nd': 15, '1st': 85, 'AC': 95},
                    ('CSMT', 'Kalyan'): {'2nd': 20, '1st': 100, 'AC': 105},
                    ('Dadar', 'Kurla'): {'2nd': 5, '1st': 20, 'AC': 30},
                    ('Dadar', 'Thane'): {'2nd': 10, '1st': 45, 'AC': 55},
                    ('Dadar', 'Kalyan'): {'2nd': 15, '1st': 70, 'AC': 80},
                    ('Kurla', 'Thane'): {'2nd': 10, '1st': 35, 'AC': 45},
                    ('Kurla', 'Kalyan'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Thane', 'Kalyan'): {'2nd': 10, '1st': 30, 'AC': 40}
                }
            },
            # Harbour Railway (HR) - CSMT to Panvel line
            'HR': {
                'stations': [
                    'CSMT', 'Dockyard Road', 'Reay Road', 'Cotton Green', 'Sewri',
                    'Wadala', 'King Circle', 'Kurla', 'Chunabhatti', 'Tilak Nagar',
                    'Chembur', 'Govandi', 'Mankhurd', 'Vashi', 'Sanpada',
                    'Juinagar', 'Nerul', 'Seawoods', 'Belapur', 'Kharghar',
                    'Mansarovar', 'Khandeshwar', 'Panvel'
                ],
                'fare_zones': {
                    ('CSMT', 'Panvel'): {'2nd': 20, '1st': 100, 'AC': 110},
                    ('CSMT', 'Vashi'): {'2nd': 15, '1st': 70, 'AC': 80},
                    ('CSMT', 'Nerul'): {'2nd': 18, '1st': 85, 'AC': 95},
                    ('Kurla', 'Panvel'): {'2nd': 15, '1st': 75, 'AC': 85},
                    ('Kurla', 'Vashi'): {'2nd': 10, '1st': 50, 'AC': 60},
                    ('Vashi', 'Panvel'): {'2nd': 10, '1st': 35, 'AC': 45}
                }
            },
            # Default fare calculation based on distance zones
            'default_fares': {
                'short': {'2nd': 5, '1st': 25, 'AC': 35},    # 0-5 km
                'medium': {'2nd': 10, '1st': 50, 'AC': 70},   # 5-15 km  
                'long': {'2nd': 15, '1st': 75, 'AC': 85},     # 15-30 km
                'very_long': {'2nd': 20, '1st': 100, 'AC': 110}  # 30+ km
            }
        }
            
    def get_mock_stations(self):
        """Mock Mumbai stations for demo"""
        return [
            {"name": "Churchgate", "lat": 18.9322, "lng": 72.8264, "type": "WR"},
            {"name": "Marine Lines", "lat": 18.9456, "lng": 72.8239, "type": "WR"},
            {"name": "Charni Road", "lat": 18.9539, "lng": 72.8200, "type": "WR"},
            {"name": "Grant Road", "lat": 18.9633, "lng": 72.8152, "type": "WR"},
            {"name": "Mumbai Central", "lat": 18.9686, "lng": 72.8181, "type": "WR"},
            {"name": "Mahalaxmi", "lat": 18.9827, "lng": 72.8186, "type": "WR"},
            {"name": "Lower Parel", "lat": 18.9969, "lng": 72.8331, "type": "WR"},
            {"name": "Elphinstone Road", "lat": 19.0041, "lng": 72.8339, "type": "WR"},
            {"name": "Dadar", "lat": 19.0178, "lng": 72.8478, "type": "WR"},
            {"name": "Matunga Road", "lat": 19.0270, "lng": 72.8489, "type": "WR"},
            {"name": "Mahim", "lat": 19.0411, "lng": 72.8411, "type": "WR"},
            {"name": "Bandra", "lat": 19.0544, "lng": 72.8406, "type": "WR"},
            {"name": "Khar Road", "lat": 19.0689, "lng": 72.8372, "type": "WR"},
            {"name": "Santacruz", "lat": 19.0822, "lng": 72.8386, "type": "WR"},
            {"name": "Vile Parle", "lat": 19.0989, "lng": 72.8469, "type": "WR"},
            {"name": "Andheri", "lat": 19.1197, "lng": 72.8469, "type": "WR"},
            # CR Line
            {"name": "CST", "lat": 18.9398, "lng": 72.8355, "type": "CR"},
            {"name": "Masjid", "lat": 18.9556, "lng": 72.8408, "type": "CR"},
            {"name": "Sandhurst Road", "lat": 18.9644, "lng": 72.8447, "type": "CR"},
            {"name": "King's Circle", "lat": 19.0270, "lng": 72.8578, "type": "CR"},
            {"name": "Kurla", "lat": 19.0692, "lng": 72.8789, "type": "CR"},
            {"name": "Ghatkopar", "lat": 19.0864, "lng": 72.9081, "type": "CR"},
            {"name": "Thane", "lat": 19.1972, "lng": 72.9636, "type": "CR"}
        ]
    
    def get_all_stations(self):
        """Get all stations for frontend dropdown"""
        if isinstance(self.stations, list):
            return self.stations
        else:
            # If stations.json has different structure, adapt accordingly
            return list(self.stations.values()) if isinstance(self.stations, dict) else []
    
    def get_routes(self, origin, destination, user_profile):
        """Get and optimize routes based on user profile - using mock data only"""
        try:
            print(f"🔍 Getting routes from {origin} to {destination}")
            
            # If origin/destination are strings, convert to coordinates
            origin_coords = self.get_station_coordinates(origin)
            destination_coords = self.get_station_coordinates(destination)
            
            if not origin_coords or not destination_coords:
                print("❌ Could not find coordinates for origin/destination")
                raw_routes = self.get_mock_routes(origin, destination, user_profile)
                return self.optimize_routes(raw_routes, user_profile)
            
            # Using mock routes only (no OTP server)
            print("🎭 Generating mock routes (OTP server removed)")
            raw_routes = self.get_mock_routes(origin, destination, user_profile)
            
            # Process routes through optimization pipeline to add coordinates
            return self.optimize_routes(raw_routes, user_profile)
            
        except Exception as e:
            print(f"❌ Error in get_routes: {e}")
            raw_routes = self.get_mock_routes(origin, destination, user_profile)
            return self.optimize_routes(raw_routes, user_profile)
    
    def get_station_coordinates(self, station_name):
        """Get coordinates for a station name with enhanced fuzzy matching"""
        if isinstance(station_name, dict):
            return station_name  # Already has coordinates
            
        print(f"🔍 Looking up coordinates for: '{station_name}'")
        
        # Normalize the search term
        search_term = station_name.lower().strip()
        
        # Search strategies
        exact_match = None
        best_partial_match = None
        railway_matches = []  # Prioritize railway stations
        word_matches = []
        
        # Define railway station indicators
        railway_indicators = ['local', 'station', 'railway', 'central', 'western']
        
        for station in self.stations:
            if isinstance(station, dict):
                name = station.get('name', '').lower().strip()
                
                # 1. Exact match
                if name == search_term:
                    exact_match = station
                    break
                
                # Check if this is a railway station
                is_railway = any(indicator in name for indicator in railway_indicators)
                
                # 2. Partial matching (contains each other)
                if search_term in name or name in search_term:
                    # Prioritize railway stations
                    if is_railway:
                        railway_matches.append((station, len(name)))
                    elif not best_partial_match or len(name) < len(best_partial_match.get('name', '')):
                        best_partial_match = station
                
                # 3. Word-based matching for complex names like "D.N.NAGAR, BARFIWALA VIDYALAYA"
                search_words = [w.strip() for w in search_term.replace(',', ' ').replace('.', ' ').split() if w.strip()]
                station_words = [w.strip() for w in name.replace(',', ' ').replace('.', ' ').split() if w.strip()]
                
                # Count matching words
                matching_words = 0
                for search_word in search_words:
                    for station_word in station_words:
                        if search_word in station_word or station_word in search_word:
                            matching_words += 1
                            break
                
                if matching_words > 0:
                    match_score = matching_words / len(search_words)
                    word_matches.append((station, match_score, matching_words, is_railway))
        
        # Use the best match found
        found_station = None
        match_type = ""
        
        if exact_match:
            found_station = exact_match
            match_type = "exact"
        elif railway_matches:
            # Prioritize railway stations, prefer shorter names (more specific)
            railway_matches.sort(key=lambda x: x[1])
            found_station = railway_matches[0][0]
            match_type = "railway station"
        elif best_partial_match:
            found_station = best_partial_match
            match_type = "partial"
        elif word_matches:
            # Sort by railway first, then match score, then number of matching words
            word_matches.sort(key=lambda x: (not x[3], -x[1], -x[2]))
            found_station = word_matches[0][0]
            match_type = f"word ({word_matches[0][1]:.2f} score)"
        
        if found_station:
            coords = {
                'lat': found_station['lat'], 
                'lng': found_station.get('lng') or found_station.get('lon')
            }
            print(f"✅ Found coordinates: {coords['lat']}, {coords['lng']} for '{found_station['name']}' (match: {match_type})")
            return coords
        
        # Fallback: Try to use known Mumbai area coordinates
        mumbai_areas = {
            'andheri': {'lat': 19.1136, 'lng': 72.8697},
            'bandra': {'lat': 19.0544, 'lng': 72.8406},
            'churchgate': {'lat': 18.9322, 'lng': 72.8264},
            'cst': {'lat': 18.9395, 'lng': 72.8353},
            'csmt': {'lat': 18.9395, 'lng': 72.8353},
            'dadar': {'lat': 19.0178, 'lng': 72.8478},
            'mumbai central': {'lat': 18.9686, 'lng': 72.8181},
            'lower parel': {'lat': 18.9969, 'lng': 72.8331},
            'kurla': {'lat': 19.0692, 'lng': 72.8789},
            'ghatkopar': {'lat': 19.0864, 'lng': 72.9081},
            'thane': {'lat': 19.1860, 'lng': 72.9756},
            'navi mumbai': {'lat': 19.0330, 'lng': 73.0297}
        }
        
        # Check if station name contains known area
        search_lower = search_term.lower()
        for area, coords in mumbai_areas.items():
            if area in search_lower or any(word in area for word in search_lower.split()):
                print(f"✅ Using approximate coordinates for '{area}': {coords['lat']}, {coords['lng']}")
                return coords
        
        print(f"❌ Could not find coordinates for station: '{station_name}'")
        print(f"📝 Available stations sample: {[s.get('name', 'Unknown')[:40] for s in self.stations[:5] if isinstance(s, dict)]}")
        return None
    
    def fetch_otp_routes(self, origin, destination):
        """Fetch comprehensive routes mixing all transport modes for best optimization"""
        try:
            # Current time
            now = datetime.now()
            
            # Comprehensive mode combinations for different route types
            mode_combinations = [
                # Public transit combinations
                ('WALK,TRANSIT', 'all_transit'),
                ('WALK,BUS', 'bus_only'),
                ('WALK,RAIL', 'rail_only'),  
                ('WALK,SUBWAY', 'metro_only'),
                ('WALK,BUS,RAIL', 'bus_rail_mix'),
                ('WALK,BUS,SUBWAY', 'bus_metro_mix'),
                ('WALK,RAIL,SUBWAY', 'rail_metro_mix'),
                
                # Auto-rickshaw options
                ('CAR', 'auto_direct'),
                ('WALK,CAR', 'walk_auto_mix'),
                
                # Mixed multimodal (auto + transit)
                ('WALK,BUS,CAR', 'auto_bus_mix'),
                ('WALK,RAIL,CAR', 'auto_rail_mix'),
                
                # Walking options
                ('WALK', 'walk_only'),
            ]
            
            all_routes = []
            
            for modes, route_category in mode_combinations:
                # Different optimization targets
                optimization_variants = [
                    {'optimize': 'QUICK', 'transferPenalty': 300},     # Fastest
                    {'optimize': 'TRANSFERS', 'transferPenalty': 1800}, # Fewest transfers
                    {'optimize': 'WALKING', 'transferPenalty': 600},   # Balanced
                ]
                
                for variant in optimization_variants:
                    params = {
                        'fromPlace': f"{origin['lat']},{origin['lng']}",
                        'toPlace': f"{destination['lat']},{destination['lng']}",
                        'time': now.strftime('%H:%M'),
                        'date': now.strftime('%m-%d-%Y'),
                        'mode': modes,
                        'optimize': variant['optimize'],
                        'maxTransfers': 5,
                        'numItineraries': 2,
                        'arriveBy': 'false',
                        'walkReluctance': 2,
                        'transferPenalty': variant['transferPenalty'],
                        'waitReluctance': 1.5,
                        'walkSpeed': 1.3  # m/s - average walking speed
                    }
                    
                    print(f"🌐 Calling OTP: {modes} (optimize: {variant['optimize']})")
                    
                    try:
                        response = requests.get(self.otp_url, params=params, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'plan' in data and 'itineraries' in data['plan']:
                                routes = data['plan']['itineraries']
                                print(f"✅ Got {len(routes)} routes for {modes} ({variant['optimize']})")
                                
                                # Tag routes with their category and optimization
                                for route in routes:
                                    route['_category'] = route_category
                                    route['_optimization'] = variant['optimize']
                                    route['_mode_combo'] = modes
                                
                                all_routes.extend(routes)
                            else:
                                print(f"⚠️  No routes for {modes} ({variant['optimize']})")
                        else:
                            print(f"❌ OTP error {response.status_code} for {modes}")
                            
                    except requests.exceptions.Timeout:
                        print(f"⏰ Timeout for {modes} ({variant['optimize']})")
                        continue
                    except Exception as e:
                        print(f"❌ Error for {modes}: {e}")
                        continue
            
            if all_routes:
                # Advanced deduplication and categorization
                unique_routes = self.categorize_and_deduplicate_routes(all_routes)
                print(f"✅ Total categorized routes: {len(unique_routes)}")
                return unique_routes
            else:
                print("⚠️  No routes found, falling back to mock data")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching comprehensive routes: {e}")
            return []
    
    def categorize_and_deduplicate_routes(self, all_routes):
        """Categorize routes by fastest, cheapest, fewest transfers and remove duplicates. Filter out direct auto routes."""
        
        # First filter out direct auto-only and walk-only routes
        filtered_routes = []
        for route in all_routes:
            is_direct_only = self.is_direct_auto_route(route)  # Now filters both auto and walk
            if is_direct_only:
                print(f"🚫 Filtering out direct-only route: {route.get('duration', 0)}min, ₹{route.get('cost', 0)}")
            else:
                filtered_routes.append(route)
        
        print(f"✅ Route filtering: {len(all_routes)} → {len(filtered_routes)} routes")
        
        categorized = {
            'fastest': [],
            'cheapest': [],
            'fewest_transfers': [],
            'mixed': []
        }
        
        # Calculate metrics for filtered routes
        route_metrics = []
        for route in filtered_routes:
            duration = route.get('duration', 0) / 60  # minutes
            transfers = self.count_transfers(route)
            cost_info = self.estimate_cost(route)
            cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
            
            # Calculate composite scores
            route_metrics.append({
                'route': route,
                'duration': duration,
                'transfers': transfers,
                'cost': cost,
                'speed_score': 100 / max(duration, 1),  # Higher is faster
                'transfer_score': 100 / max(transfers + 1, 1),  # Higher is fewer transfers
                'cost_score': 100 / max(cost, 1)  # Higher is cheaper
            })
        
        # Sort by different criteria
        by_speed = sorted(route_metrics, key=lambda x: x['duration'])
        by_cost = sorted(route_metrics, key=lambda x: x['cost'])
        by_transfers = sorted(route_metrics, key=lambda x: x['transfers'])
        
        # Select best routes for each category
        unique_signatures = set()
        
        def add_unique_route(route_data, category):
            route = route_data['route']
            # Create signature to avoid duplicates
            signature = f"{int(route_data['duration']//5)}_{route_data['transfers']}_{int(route_data['cost']//10)}"
            
            if signature not in unique_signatures and len(categorized[category]) < 3:
                unique_signatures.add(signature)
                categorized[category].append(route)
                return True
            return False
        
        # Add fastest routes
        for route_data in by_speed[:5]:
            add_unique_route(route_data, 'fastest')
        
        # Add cheapest routes  
        for route_data in by_cost[:5]:
            add_unique_route(route_data, 'cheapest')
        
        # Add fewest transfer routes
        for route_data in by_transfers[:5]:
            add_unique_route(route_data, 'fewest_transfers')
        
        # Add some mixed/balanced routes
        balanced = sorted(route_metrics, key=lambda x: -(x['speed_score'] + x['transfer_score'] + x['cost_score']))
        for route_data in balanced[:3]:
            if len(categorized['mixed']) < 2:
                add_unique_route(route_data, 'mixed')
        
        # Flatten to single list with category tags
        final_routes = []
        for category, routes in categorized.items():
            for route in routes:
                route['_route_category'] = category
                final_routes.append(route)
        
        return final_routes[:10]  # Return top 10 diverse routes
    
    def is_direct_auto_route(self, route):
        """Check if this is a direct auto-only or walk-only route (not multimodal) - filter both"""
        legs = route.get('legs', [])
        
        # Count different transport modes (looking for CAR since conversion happens later)
        car_legs = [leg for leg in legs if leg.get('mode') == 'CAR']
        transit_legs = [leg for leg in legs if leg.get('mode') in ['BUS', 'RAIL', 'SUBWAY']]
        walk_legs = [leg for leg in legs if leg.get('mode') == 'WALK']
        
        print(f"🔍 Route check: {len(car_legs)} car, {len(transit_legs)} transit, {len(walk_legs)} walk legs")
        
        # Filter out direct walk routes (walk-only with no other transport)
        if len(walk_legs) > 0 and len(transit_legs) == 0 and len(car_legs) == 0:
            walk_duration = sum(leg.get('duration', 0) for leg in walk_legs)
            # Convert seconds to minutes if needed (OTP returns duration in seconds)
            if walk_duration > 1000:  # Likely in seconds
                walk_duration = walk_duration / 60
            if walk_duration > 60:  # Filter out very long walking routes (>60 minutes)
                print(f"🚫 Marking as direct walk route (walk: {walk_duration:.1f}min)")
                return True
        
        # Filter out direct car/auto routes (car-only with no public transit)
        if len(car_legs) > 0 and len(transit_legs) == 0:
            # Calculate total non-walk duration
            non_walk_duration = sum(leg.get('duration', 0) for leg in legs if leg.get('mode') != 'WALK')
            car_duration = sum(leg.get('duration', 0) for leg in car_legs)
            
            # Convert seconds to minutes if needed (OTP returns duration in seconds)
            if car_duration > 1000:  # Likely in seconds
                car_duration = car_duration / 60
                non_walk_duration = non_walk_duration / 60
            
            print(f"🚗 Car duration: {car_duration:.1f} min, Non-walk duration: {non_walk_duration:.1f} min")
            
            # If car is the dominant mode (more than 60% of non-walk time) and longer than 20 minutes
            if car_duration > 20 and (car_duration / max(non_walk_duration, 1)) > 0.6:
                print(f"🚫 Marking as direct auto route (car: {car_duration:.1f}min / total non-walk: {non_walk_duration:.1f}min)")
                return True
                
        return False
    
    def optimize_routes(self, routes, user_profile):
        """Optimize routes and categorize by Fastest, Cheapest, and Fewest Transfers"""
        if not routes:
            return []
        
        print(f"🔍 Optimizing {len(routes)} routes with categorical approach")
        
        # Calculate comprehensive metrics for all routes
        route_analysis = []
        
        for route in routes:
            # Check if duration is in seconds or minutes
            raw_duration = route['duration']
            if raw_duration > 300:  # If greater than 5 minutes in seconds (300), assume it's in seconds
                duration_minutes = raw_duration / 60
            else:
                duration_minutes = raw_duration  # Already in minutes
                
            transfers = self.count_transfers(route)
            cost_info = self.estimate_cost(route)
            cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
            walk_time = route.get('walkTime', 0) / 60
            
            # Get route category if available
            category = route.get('_route_category', 'mixed')
            
            route_data = {
                'raw_route': route,
                'duration': duration_minutes,
                'transfers': transfers,
                'cost': cost,
                'walk_time': walk_time,
                'category': category,
                'score': self.calculate_score(route, user_profile),
                'eco_score': self.calculate_eco_score(route)
            }
            
            route_analysis.append(route_data)
            print(f"📊 Route: {duration_minutes:.1f}min, {transfers} transfers, ₹{cost} ({category})")
        
        # Categorize routes by primary criteria
        categorized_routes = {
            'fastest': [],
            'cheapest': [],
            'fewest_transfers': []
        }
        
        # Sort by each criteria
        by_speed = sorted(route_analysis, key=lambda x: x['duration'])
        by_cost = sorted(route_analysis, key=lambda x: x['cost'])
        by_transfers = sorted(route_analysis, key=lambda x: (x['transfers'], x['duration']))
        
        print("🚀 FASTEST ROUTES:")
        for i, route_data in enumerate(by_speed[:2]):
            if route_data not in categorized_routes['fastest']:
                categorized_routes['fastest'].append(route_data)
                print(f"  {i+1}. {route_data['duration']:.1f}min, {route_data['transfers']} transfers, ₹{route_data['cost']}")
        
        print("💰 CHEAPEST ROUTES:")
        for i, route_data in enumerate(by_cost[:2]):
            if route_data not in categorized_routes['cheapest']:
                categorized_routes['cheapest'].append(route_data)
                print(f"  {i+1}. ₹{route_data['cost']}, {route_data['duration']:.1f}min, {route_data['transfers']} transfers")
        
        print("🔄 FEWEST TRANSFERS:")
        for i, route_data in enumerate(by_transfers[:2]):
            if route_data not in categorized_routes['fewest_transfers']:
                categorized_routes['fewest_transfers'].append(route_data)
                print(f"  {i+1}. {route_data['transfers']} transfers, {route_data['duration']:.1f}min, ₹{route_data['cost']}")
        
        # Convert back to frontend format with proper categorization
        final_routes = []
        route_id = 1
        
        # Add fastest routes
        for route_data in categorized_routes['fastest']:
            formatted_route = self.format_route_for_frontend(route_data, route_id, "Fastest")
            final_routes.append(formatted_route)
            route_id += 1
        
        # Add cheapest routes (if different from fastest)
        for route_data in categorized_routes['cheapest']:
            if not any(abs(r['duration'] - route_data['duration']) < 2 for r in final_routes):
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Cheapest")
                final_routes.append(formatted_route)
                route_id += 1
        
        # Add fewest transfer routes (if different from others)
        for route_data in categorized_routes['fewest_transfers']:
            if not any(abs(r['duration'] - route_data['duration']) < 2 for r in final_routes):
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Direct" if route_data['transfers'] == 0 else "Best")
                final_routes.append(formatted_route)
                route_id += 1
        
        # Ensure we have at least 3 routes by adding balanced options
        if len(final_routes) < 3:
            remaining_routes = [r for r in route_analysis if not any(abs(fr['duration'] - r['duration']) < 3 for fr in final_routes)]
            balanced_routes = sorted(remaining_routes, key=lambda x: -(x['score']))
            
            for route_data in balanced_routes[:3-len(final_routes)]:
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Good")
                final_routes.append(formatted_route)
                route_id += 1
        
        print(f"✅ Returning {len(final_routes)} categorized routes")
        return final_routes[:5]  # Maximum 5 routes
    
    def format_route_for_frontend(self, route_data, route_id, route_type):
        """Format route data for frontend consumption with detailed fare information"""
        raw_route = route_data['raw_route']
        cost_info = self.estimate_cost(raw_route)
        
        print(f"🔧 Formatting route {route_id} ({route_type})")
        print(f"   📊 Raw route legs: {len(raw_route.get('legs', []))}")
        for i, leg in enumerate(raw_route.get('legs', [])):
            print(f"      Leg {i+1}: {leg.get('mode')} - {leg.get('from_name')} → {leg.get('to_name')} ({leg.get('duration')}min)")
        
        # Generate coordinate path for the route
        formatted_route = {
            'route_id': route_id,
            'duration': int(route_data['duration']),
            'transfers': route_data['transfers'],
            'score': round(route_data['score'], 2),
            'cost': cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info,
            'fare_breakdown': cost_info.get('breakdown', []) if isinstance(cost_info, dict) else [],
            'eco_score': round(route_data['eco_score'], 1),
            'route_type': route_type,
            'legs': self.format_legs_with_coordinates(raw_route.get('legs', [])),
            'start_time': raw_route.get('startTime', 0),
            'end_time': raw_route.get('endTime', 0),
            'walkTime': route_data['walk_time'],
            'transitTime': raw_route.get('transitTime', 0) / 60,
            'waitingTime': raw_route.get('waitingTime', 0) / 60,
            'raw_route': raw_route
        }
        
        # Add coordinate path for map visualization
        formatted_route['coordinate_path'] = self.generate_route_coordinates(raw_route.get('legs', []))
        
        # Debug: Print coordinate information
        print(f"🗺️ Route {route_id} coordinate path: {len(formatted_route['coordinate_path'])} points")
        if formatted_route['coordinate_path']:
            print(f"   📍 First point: {formatted_route['coordinate_path'][0]}")
            print(f"   📍 Last point: {formatted_route['coordinate_path'][-1]}")
        
        print(f"   ✅ Formatted legs: {len(formatted_route['legs'])}")
        for i, leg in enumerate(formatted_route['legs']):
            print(f"      Formatted Leg {i+1}: {leg.get('mode')} - {leg.get('from_name')} → {leg.get('to_name')} ({leg.get('duration')}min)")
        
        return formatted_route
    
    def count_transfers(self, route):
        """Count number of transfers in a route including auto-rickshaw"""
        transit_legs = 0
        for leg in route.get('legs', []):
            mode = leg.get('mode')
            if mode in ['BUS', 'RAIL', 'SUBWAY', 'TRAM', 'CAR']:  # CAR = auto-rickshaw
                transit_legs += 1
        return max(0, transit_legs - 1)  # First boarding is not a transfer
    
    def calculate_score(self, route, profile):
        """Calculate route score based on user profile"""
        transfer_weight = profile.get('transfer_preference', 0.4)
        time_weight = profile.get('time_preference', 0.3)
        cost_weight = profile.get('cost_preference', 0.2)
        eco_weight = profile.get('eco_preference', 0.1)
        
        # Normalize scores (0-10 scale)
        transfers = self.count_transfers(route)
        duration_minutes = route['duration'] / 60
        
        transfer_score = max(0, 10 - transfers * 3)  # Fewer transfers = higher score
        time_score = max(0, 10 - duration_minutes / 10)  # Faster = higher score
        cost_info = self.estimate_cost(route)
        cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
        cost_score = max(0, 10 - cost / 10)  # Cheaper = higher score
        eco_score = self.calculate_eco_score(route)
        
        total_score = (
            transfer_score * transfer_weight +
            time_score * time_weight +
            cost_score * cost_weight +
            eco_score * eco_weight
        )
        
        return total_score
    
    def calculate_train_fare(self, from_station, to_station, distance_km=0):
        """Calculate accurate Mumbai train fare between stations with class options"""
        
        # Clean and normalize station names
        from_station = self.normalize_station_name(from_station)
        to_station = self.normalize_station_name(to_station)
        
        print(f"🚂 Calculating train fare: {from_station} → {to_station} ({distance_km:.1f}km)")
        
        # Try to find exact fare from our fare table
        for line, line_data in self.train_fares.items():
            if line == 'default_fares':
                continue
                
            fare_zones = line_data.get('fare_zones', {})
            
            # Check direct route
            direct_key = (from_station, to_station)
            reverse_key = (to_station, from_station)
            
            if direct_key in fare_zones:
                fares = fare_zones[direct_key]
                print(f"✅ Found direct fare on {line}: 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
                return fares
            elif reverse_key in fare_zones:
                fares = fare_zones[reverse_key] 
                print(f"✅ Found reverse fare on {line}: 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
                return fares
        
        # If no exact match, use distance-based calculation
        if distance_km > 0:
            if distance_km <= 5:
                zone = 'short'
            elif distance_km <= 15:
                zone = 'medium'
            elif distance_km <= 30:
                zone = 'long'
            else:
                zone = 'very_long'
                
            fares = self.train_fares['default_fares'][zone]
            print(f"✅ Using distance-based fare ({zone}): 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
            return fares
        
        # Ultimate fallback
        default_fare = {'2nd': 10, '1st': 50, 'AC': 70}
        print(f"⚠️  Using default train fare: 2nd=₹{default_fare['2nd']}, 1st=₹{default_fare['1st']}, AC=₹{default_fare['AC']}")
        return default_fare
    
    def normalize_station_name(self, station_name):
        """Normalize station names for fare lookup"""
        if not station_name:
            return ""
            
        # Convert to standard format
        name = station_name.strip().upper()
        
        # Common name mappings
        name_mappings = {
            'CST': 'CSMT',
            'CSMT': 'CSMT',  # Keep CSMT as-is
            'CHHATRAPATI SHIVAJI TERMINUS': 'CSMT', 
            'CHHATRAPATI SHIVAJI MAHARAJ TERMINUS': 'CSMT',
            'VT': 'CSMT',
            'VICTORIA TERMINUS': 'CSMT',
            'MUMBAI CENTRAL': 'Mumbai Central',
            'BCT': 'Mumbai Central',
            'BOMBAY CENTRAL': 'Mumbai Central',
            'CHURCHGATE': 'Churchgate',
            'DADAR': 'Dadar',
            'ANDHERI': 'Andheri',
            'BORIVALI': 'Borivali',
            'VIRAR': 'Virar',
            'KURLA': 'Kurla',
            'THANE': 'Thane',
            'KALYAN': 'Kalyan',
            'PANVEL': 'Panvel',
            'VASHI': 'Vashi',
            'NERUL': 'Nerul'
        }
        
        return name_mappings.get(name, station_name.title())
    
    def estimate_cost(self, route):
        """Estimate route cost in INR with accurate Mumbai transport pricing and class options (2025)"""
        total_cost = 0
        fare_breakdown = []
        
        for leg in route.get('legs', []):
            mode = leg.get('mode', '')
            distance = leg.get('distance', 0) / 1000  # Convert to km
            from_name = self.extract_place_name(leg.get('from', {}))
            to_name = self.extract_place_name(leg.get('to', {}))
            
            leg_cost = 0
            fare_details = {}
            
            if mode == 'BUS':
                # BEST bus fare: ₹8-₹25 based on distance
                if distance <= 3:
                    leg_cost = 8  # Short distance
                elif distance <= 10:
                    leg_cost = 15  # Medium distance
                else:
                    leg_cost = 25  # Long distance
                    
                fare_details = {
                    'mode': 'BUS',
                    'operator': 'BEST',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fare': leg_cost,
                    'route_number': leg.get('tripShortName', '').replace('-UP', '').replace('-DN', '')
                }
                    
            elif mode == 'RAIL':
                # Mumbai Local Train: Use accurate fare table
                train_fares = self.calculate_train_fare(from_name, to_name, distance)
                leg_cost = train_fares['2nd']  # Default to 2nd class for cost calculation
                
                # Determine line based on route information
                route_info = leg.get('routeLongName', '')
                line = 'WR' if 'western' in route_info.lower() else 'CR' if 'central' in route_info.lower() else 'HR' if 'harbour' in route_info.lower() else 'LOCAL'
                
                fare_details = {
                    'mode': 'RAIL',
                    'operator': 'Indian Railways',
                    'line': line,
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fares': {
                        '2nd_class': train_fares['2nd'],
                        '1st_class': train_fares['1st'], 
                        'ac_local': train_fares['AC']
                    },
                    'default_fare': train_fares['2nd']
                }
                    
            elif mode == 'SUBWAY':
                # Mumbai Metro: ₹10-₹50 based on distance and specific route patterns
                if distance <= 3:
                    leg_cost = 10  # Short metro ride (1-3 stations)
                elif distance <= 6:
                    leg_cost = 20  # Medium metro ride
                elif distance <= 12:
                    leg_cost = 40  # Long metro ride (like Ghatkopar to D.N.Nagar = 9.5km)
                else:
                    leg_cost = 50  # Very long metro ride (end-to-end Blue Line)
                    
                fare_details = {
                    'mode': 'METRO',
                    'operator': 'Mumbai Metro',
                    'line': 'Blue Line (ML-1)',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fare': leg_cost
                }
                    
            elif mode == 'TRAM':
                leg_cost = 5   # Heritage tram (rare)
                fare_details = {
                    'mode': 'TRAM',
                    'operator': 'BEST',
                    'from': from_name,
                    'to': to_name,
                    'fare': leg_cost
                }
                
            elif mode in ['CAR', 'AUTO']:  # Auto-rickshaw
                # Mumbai auto fare 2025: ₹28 base + ₹18/km (with traffic surcharge)
                base_fare = 28
                distance_fare = distance * 18
                # Add waiting time surcharge for longer trips
                if distance > 3:
                    distance_fare += 10  # Traffic/waiting surcharge
                leg_cost = base_fare + distance_fare
                
                fare_details = {
                    'mode': 'AUTO',
                    'operator': 'Auto Rickshaw',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'base_fare': base_fare,
                    'distance_fare': round(distance_fare),
                    'total_fare': round(leg_cost)
                }
            
            # WALK mode has no cost
            if leg_cost > 0:
                total_cost += leg_cost
                fare_breakdown.append(fare_details)
        
        return {
            'total_cost': max(5, int(total_cost)),  # Minimum ₹5, rounded to integer
            'breakdown': fare_breakdown
        }
    
    def calculate_eco_score(self, route):
        """Calculate eco-friendliness score (0-10) based on transport modes and emissions"""
        total_distance = 0
        eco_points = 0
        
        # Calculate points based on transport modes used
        for leg in route.get('legs', []):
            distance = leg.get('distance', 0) / 1000  # Convert to km
            mode = leg.get('mode', 'WALK')
            total_distance += distance
            
            # Eco points per km based on transport mode
            if mode == 'WALK':
                eco_points += distance * 10  # Walking is best (10 points/km)
            elif mode in ['RAIL', 'SUBWAY']:
                eco_points += distance * 8   # Public transit is great (8 points/km)
            elif mode == 'BUS':
                eco_points += distance * 5   # Bus is average (5 points/km)
            elif mode == 'TRAM':
                eco_points += distance * 9   # Tram is excellent (9 points/km)
            elif mode in ['CAR', 'AUTO']:
                eco_points += distance * 2   # Auto/car is poor (2 points/km)
            else:
                eco_points += distance * 5   # Unknown mode gets neutral score
        
        if total_distance == 0:
            return 5.0
        
        # Calculate final score (0-10 scale)
        # Perfect score (10) = average 8+ points per km (mostly public transport + walking)
        # Good score (7-9) = average 6-8 points per km (mix of public transport)
        # Average score (5-7) = average 4-6 points per km (some private transport)
        # Poor score (1-4) = average <4 points per km (mostly private transport)
        
        avg_points_per_km = eco_points / total_distance
        eco_score = min(10, max(1, avg_points_per_km * 1.25))  # Scale to 0-10
        
        return round(eco_score, 1)
    
    def get_route_type(self, route, profile, route_index=0):
        """Determine route type label based on route characteristics"""
        transfers = self.count_transfers(route)
        duration = route['duration'] / 60  # minutes
        walk_time = route.get('walkTime', 0) / 60  # minutes
        
        # Check if it's an auto-rickshaw route (CAR mode converted to AUTO)
        legs = route.get('legs', [])
        has_auto = any(leg.get('mode') == 'CAR' for leg in legs)
        if has_auto:
            return "Direct" if transfers == 0 else "Premium"
        
        # Check for specific transit modes
        has_rail = any(leg.get('mode') == 'RAIL' for leg in legs)
        has_bus = any(leg.get('mode') == 'BUS' for leg in legs)
        has_subway = any(leg.get('mode') == 'SUBWAY' for leg in legs)
        
        # First route is usually "Best" unless it's clearly something else
        if route_index == 0 and not has_auto:
            return "Best"
        
        # Direct routes (no transfers)
        if transfers == 0:
            if has_rail:
                return "Direct"
            elif has_bus:
                return "Direct"
            else:
                return "Direct"
        
        # Fast routes (short duration)
        if duration <= 35:
            return "Fastest"
        
        # Eco-friendly routes (more walking)
        if walk_time > duration * 0.25:  # 25%+ walking
            return "Eco"
        
        # Rail-based routes
        if has_rail and not has_bus:
            return "Express" if transfers <= 1 else "Rail"
        
        # Bus-only routes
        if has_bus and not has_rail:
            return "Budget" if transfers <= 1 else "Economy"
        
        # Mixed mode routes
        if has_rail and has_bus:
            return "Comfort" if transfers <= 2 else "Mixed"
        
        # Metro routes
        if has_subway:
            return "Metro"
        
        # Default classification based on transfers
        if transfers == 1:
            return "Good"
        elif transfers == 2:
            return "Standard"
        else:
            return "Alternative"
    
    def format_legs(self, legs):
        """Format route legs for frontend display with enhanced OTP data extraction"""
        formatted = []
        for leg in legs:
            # Extract mode information and convert CAR to AUTO for better UX
            mode = leg.get('mode', 'WALK')
            if mode == 'CAR':
                mode = 'AUTO'  # Convert car to auto-rickshaw for Indian context
            
            # Extract route information (for transit legs) with proper bus/train numbers
            route_info = ''
            route_number = ''
            if mode not in ['WALK', 'AUTO']:
                # Try to get route number from multiple fields in priority order
                # For bus routes, extract from tripShortName or headsign
                trip_short = leg.get('tripShortName', '')
                headsign = leg.get('headsign', '')
                route_short = leg.get('routeShortName', '')
                
                if mode == 'BUS':
                    # Extract bus number from tripShortName (like "56-UP", "2LTD-UP", "181-UP")
                    if trip_short and trip_short != 'BEST':
                        # Remove direction suffixes
                        route_number = trip_short.replace('-UP', '').replace('-DN', '').replace('2:', '').strip()
                    elif headsign and headsign not in ['BEST Bus', 'BEST']:
                        route_number = headsign.replace('-UP', '').replace('-DN', '').strip()
                    elif route_short and route_short not in ['BEST', 'BEST Bus']:
                        route_number = route_short
                        
                    # Clean up route number
                    if route_number and route_number != 'BEST':
                        route_description = f"BEST {route_number}"
                    else:
                        route_number = 'BEST'
                        route_description = 'BEST Bus'
                        
                elif mode == 'RAIL':
                    # For trains, get the line name and train info
                    route_description = leg.get('routeLongName', 'Local Train')
                    if trip_short:
                        # Extract train info (like "Virar - Churchgate", "AAR-DAH-235")
                        if ' - ' in trip_short:
                            route_number = trip_short.split(' - ')[0]
                        else:
                            route_number = trip_short.replace('2:', '')
                    elif route_short:
                        route_number = route_short
                    else:
                        route_number = 'LOCAL'
                        
                elif mode == 'SUBWAY':
                    # For metro, get the line name and number
                    route_description = leg.get('routeLongName', 'Metro')
                    if route_short:
                        route_number = route_short
                    elif trip_short:
                        route_number = trip_short.replace('2:', '')
                    else:
                        route_number = 'ML-1'
                
                # Combine route number and description for display
                if mode == 'BUS':
                    route_info = route_description  # Already formatted as "BEST {number}"
                elif mode == 'RAIL':
                    if route_number and route_number != 'LOCAL':
                        route_info = f"{route_number} - {route_description}" if route_description != route_number else route_number
                    else:
                        route_info = route_description
                elif mode == 'SUBWAY':
                    if route_number and route_description:
                        route_info = f"{route_number} - {route_description}" if route_description != route_number else route_number
                    else:
                        route_info = route_description or 'Metro'
                        
                # Fallback to generic names if nothing found
                if not route_info:
                    if mode == 'BUS':
                        route_info = 'BEST Bus'
                        route_number = 'BEST'
                    elif mode == 'RAIL':
                        route_info = 'Local Train'
                        route_number = 'LOCAL'
                    elif mode == 'SUBWAY':
                        route_info = 'Metro'
                        route_number = 'ML-1'
                    else:
                        route_info = mode
                        route_number = mode
            elif mode == 'AUTO':
                route_info = 'Auto Rickshaw'
                route_number = 'AUTO'
            
            # Extract timing information with fallback calculation
            duration_raw = leg.get('duration', 0)
            start_time = leg.get('startTime', 0)
            end_time = leg.get('endTime', 0)
            
            # Calculate duration from timestamps if duration is 0 or missing
            if duration_raw == 0 and start_time and end_time:
                duration_seconds = (end_time - start_time) / 1000  # Convert milliseconds to seconds
                duration_minutes = int(duration_seconds / 60) if duration_seconds else 0
                print(f"🔧 Calculated duration from timestamps: {duration_seconds}s for {mode}")
            else:
                # Check if duration is in seconds or minutes (same logic as route duration)
                if duration_raw > 300:  # If greater than 5 minutes in seconds (300), assume it's in seconds
                    duration_minutes = int(duration_raw / 60)
                else:
                    duration_minutes = duration_raw  # Already in minutes
            
            # For transit legs, ensure minimum realistic duration based on distance
            if mode in ['BUS', 'RAIL', 'SUBWAY'] and duration_minutes < 1:
                distance_km = leg.get('distance', 0) / 1000
                if distance_km > 0.5:  # Only for distances > 500m
                    # Estimate minimum duration based on mode and distance
                    if mode == 'BUS':
                        # Mumbai bus average speed: 15-20 km/h in traffic
                        estimated_minutes = max(2, int(distance_km * 4))  # ~15 km/h average
                    elif mode == 'SUBWAY':
                        # Mumbai metro average speed: 35-40 km/h including stops
                        estimated_minutes = max(1, int(distance_km * 2))  # ~30 km/h average
                    elif mode == 'RAIL':
                        # Mumbai local train average speed: 40-50 km/h including stops
                        estimated_minutes = max(2, int(distance_km * 1.5))  # ~40 km/h average
                    
                    if estimated_minutes > duration_minutes:
                        duration_minutes = estimated_minutes
                        print(f"🔧 Adjusted {mode} duration to {duration_minutes}min based on {distance_km:.1f}km distance")
            
            # Extract location information
            from_place = leg.get('from', {})
            to_place = leg.get('to', {})
            
            # Get proper station/stop names with better cleaning
            # Handle both OTP format (from/to objects) and mock format (from_name/to_name strings)
            if leg.get('from_name') and leg.get('to_name'):
                # Mock route format - use the names directly
                from_name = leg.get('from_name')
                to_name = leg.get('to_name')
            else:
                # OTP format - extract from place objects
                from_name = self.extract_place_name(from_place)
                to_name = self.extract_place_name(to_place)
            
            # Extract distance
            distance = int(leg.get('distance', 0))
            
            formatted_leg = {
                'mode': mode,
                'route': route_info,
                'route_number': route_number,  # Add specific route number
                'duration': duration_minutes,
                'distance': distance,
                'from_name': from_name,
                'to_name': to_name,
                'start_time': start_time,
                'end_time': end_time,
                'departureTime': self.format_timestamp(start_time) if start_time else None,
                'arrivalTime': self.format_timestamp(end_time) if end_time else None
            }
            
            # Add transit-specific information with enhanced route details
            if mode not in ['WALK', 'AUTO']:
                # Add route-specific details
                formatted_leg.update({
                    'routeLongName': leg.get('routeLongName', ''),
                    'routeShortName': leg.get('routeShortName', ''),
                    'routeId': leg.get('routeId', ''),
                    'headsign': leg.get('headsign', ''),
                })
                
                # Add trip information if available
                if 'trip' in leg:
                    trip_info = leg['trip']
                    formatted_leg.update({
                        'trip_headsign': trip_info.get('tripHeadsign', ''),
                        'trip_id': trip_info.get('tripId', ''),
                        'trip_short_name': trip_info.get('tripShortName', ''),
                        'block_id': trip_info.get('blockId', '')
                    })
                
                # Add agency information
                if 'agencyName' in leg:
                    formatted_leg['agency'] = leg['agencyName']
            
            formatted.append(formatted_leg)
            
        return formatted
    
    def format_legs_with_coordinates(self, legs):
        """Format route legs with coordinate information for map visualization"""
        formatted = self.format_legs(legs)
        
        # Add coordinate information to each leg
        for i, leg in enumerate(formatted):
            # Get coordinates for start and end points
            from_coords = self.get_station_coordinates(leg['from_name'])
            to_coords = self.get_station_coordinates(leg['to_name'])
            
            if from_coords and to_coords:
                leg['from_coords'] = [from_coords['lat'], from_coords['lng']]
                leg['to_coords'] = [to_coords['lat'], to_coords['lng']]
                
                # Generate intermediate coordinates for the leg path
                leg['path_coordinates'] = self.generate_leg_coordinates(
                    leg['from_coords'], 
                    leg['to_coords'], 
                    leg['mode']
                )
            else:
                # Fallback coordinates if station not found
                leg['from_coords'] = [19.0760, 72.8777]  # Mumbai center
                leg['to_coords'] = [19.0760, 72.8777]
                leg['path_coordinates'] = [[19.0760, 72.8777]]
        
        return formatted
    
    def generate_route_coordinates(self, legs):
        """Generate complete coordinate path for the entire route"""
        all_coordinates = []
        
        print(f"🚗 Generating route coordinates for {len(legs)} legs")
        
        for i, leg in enumerate(legs):
            from_name = leg.get('from_name', '')
            to_name = leg.get('to_name', '')
            mode = leg.get('mode', 'WALK')
            
            print(f"   🔗 Leg {i+1}: {mode} from '{from_name}' to '{to_name}'")
            
            from_coords = self.get_station_coordinates(from_name)
            to_coords = self.get_station_coordinates(to_name)
            
            if from_coords and to_coords:
                from_point = [from_coords['lat'], from_coords['lng']]
                to_point = [to_coords['lat'], to_coords['lng']]
                
                print(f"      📍 From: {from_point} To: {to_point}")
                
                # Add leg coordinates
                leg_coordinates = self.generate_leg_coordinates(
                    from_point, 
                    to_point, 
                    mode
                )
                
                print(f"      🗺️ Generated {len(leg_coordinates)} coordinates for this leg")
                
                # Avoid duplicating coordinates at connection points
                if all_coordinates and leg_coordinates:
                    all_coordinates.extend(leg_coordinates[1:])  # Skip first point to avoid duplication
                else:
                    all_coordinates.extend(leg_coordinates)
            else:
                print(f"      ❌ Could not find coordinates for {from_name} -> {to_name}")
        
        print(f"🗺️ Total route coordinates: {len(all_coordinates)}")
        return all_coordinates if all_coordinates else [[19.0760, 72.8777]]  # Fallback to Mumbai center
    
    def generate_leg_coordinates(self, from_coords, to_coords, mode):
        """Generate coordinate path for a single leg based on transport mode"""
        if not from_coords or not to_coords:
            return [from_coords or [19.0760, 72.8777], to_coords or [19.0760, 72.8777]]
        
        # For walking, create a simple straight line with slight curve
        if mode == 'WALK':
            return self.generate_walking_path(from_coords, to_coords)
        
        # For rail transport, follow rail corridors
        elif mode == 'RAIL':
            return self.generate_rail_path(from_coords, to_coords)
        
        # For bus, follow major roads
        elif mode == 'BUS':
            return self.generate_bus_path(from_coords, to_coords)
        
        # For metro, follow metro lines
        elif mode == 'SUBWAY':
            return self.generate_metro_path(from_coords, to_coords)
        
        # Default: straight line with intermediate points
        else:
            return self.generate_simple_path(from_coords, to_coords)
    
    def generate_walking_path(self, from_coords, to_coords):
        """Generate walking path coordinates"""
        # Simple straight line for walking
        return [from_coords, to_coords]
    
    def generate_rail_path(self, from_coords, to_coords):
        """Generate rail path following Mumbai railway corridors"""
        coordinates = [from_coords]
        
        # Determine if this is Western or Central Railway
        if self.is_western_railway_stations(from_coords, to_coords):
            # Western Railway follows the coast
            coordinates.extend(self.get_western_railway_intermediate_points(from_coords, to_coords))
        else:
            # Central Railway goes inland
            coordinates.extend(self.get_central_railway_intermediate_points(from_coords, to_coords))
        
        coordinates.append(to_coords)
        return coordinates
    
    def generate_bus_path(self, from_coords, to_coords):
        """Generate bus path following major roads"""
        # Create intermediate points following major Mumbai roads
        coordinates = [from_coords]
        
        # Add intermediate points based on major road network
        lat_diff = to_coords[0] - from_coords[0]
        lng_diff = to_coords[1] - from_coords[1]
        
        # Create 2-3 intermediate points following road patterns
        for i in range(1, 3):
            ratio = i / 3
            intermediate_lat = from_coords[0] + (lat_diff * ratio)
            intermediate_lng = from_coords[1] + (lng_diff * ratio)
            
            # Adjust coordinates to follow road patterns (slight curves)
            if i == 1:
                # First intermediate point - slight curve toward major roads
                intermediate_lng += lng_diff * 0.1  # Slight curve
            
            coordinates.append([intermediate_lat, intermediate_lng])
        
        coordinates.append(to_coords)
        return coordinates
    
    def generate_metro_path(self, from_coords, to_coords):
        """Generate metro path coordinates"""
        # Metro lines are mostly straight
        return self.generate_simple_path(from_coords, to_coords)
    
    def generate_simple_path(self, from_coords, to_coords):
        """Generate simple path with intermediate points"""
        coordinates = [from_coords]
        
        # Add one intermediate point
        lat_mid = (from_coords[0] + to_coords[0]) / 2
        lng_mid = (from_coords[1] + to_coords[1]) / 2
        coordinates.append([lat_mid, lng_mid])
        
        coordinates.append(to_coords)
        return coordinates
    
    def is_western_railway_stations(self, from_coords, to_coords):
        """Check if the coordinates correspond to Western Railway stations"""
        # Western Railway runs along the western coast (longitude around 72.82-72.85)
        avg_lng = (from_coords[1] + to_coords[1]) / 2
        return 72.80 <= avg_lng <= 72.86
    
    def get_western_railway_intermediate_points(self, from_coords, to_coords):
        """Get intermediate points along Western Railway line"""
        points = []
        
        # Western Railway key points (approximate coordinates)
        wr_stations = [
            [18.9322, 72.8264],  # Churchgate
            [19.0178, 72.8478],  # Dadar
            [19.0544, 72.8406],  # Bandra
            [19.1197, 72.8469],  # Andheri
            [19.2306, 72.8567]   # Borivali
        ]
        
        # Find relevant intermediate stations
        start_lat = min(from_coords[0], to_coords[0])
        end_lat = max(from_coords[0], to_coords[0])
        
        for station_coords in wr_stations:
            if start_lat <= station_coords[0] <= end_lat:
                points.append(station_coords)
        
        return points
    
    def get_central_railway_intermediate_points(self, from_coords, to_coords):
        """Get intermediate points along Central Railway line"""
        points = []
        
        # Central Railway key points (approximate coordinates)
        cr_stations = [
            [18.9398, 72.8355],  # CST
            [19.0178, 72.8478],  # Dadar
            [19.0692, 72.8789],  # Kurla
            [19.0864, 72.9081],  # Ghatkopar
            [19.1972, 72.9636]   # Thane
        ]
        
        # Find relevant intermediate stations
        start_lat = min(from_coords[0], to_coords[0])
        end_lat = max(from_coords[0], to_coords[0])
        
        for station_coords in cr_stations:
            if start_lat <= station_coords[0] <= end_lat:
                points.append(station_coords)
        
        return points
    
    def extract_place_name(self, place):
        """Extract a readable place name from OTP place object with better cleaning"""
        if not place:
            return 'Unknown'
        
        # Try different name fields in order of preference
        name = (place.get('name') or 
                place.get('stopName') or 
                place.get('stationName') or 
                place.get('vertexType', ''))
        
        # Clean up the name for better readability
        if name:
            # Remove coordinate suffixes like "::1234,5678"
            if '::' in name:
                name = name.split('::')[0]
            
            # Remove parenthetical coordinates
            if name.endswith(')') and '(' in name:
                paren_pos = name.rfind('(')
                potential_coords = name[paren_pos+1:-1]
                # Check if it looks like coordinates (numbers, commas, dots)
                if all(c.isdigit() or c in '.,- ' for c in potential_coords):
                    name = name[:paren_pos].strip()
            
            # Clean up common OTP artifacts
            name = name.replace('_', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
            
            # Handle common Mumbai station name patterns
            if 'STATION' in name.upper():
                name = name.replace('STATION', 'Station')
            if 'ROAD' in name.upper():
                name = name.replace('ROAD', 'Road')
            if 'DEPOT' in name.upper():
                name = name.replace('DEPOT', 'Depot')
                
            return name
        
        # Fallback to coordinates if no name available
        lat = place.get('lat', 0)
        lon = place.get('lon', 0)
        return f"Location ({lat:.4f}, {lon:.4f})"
    
    def format_timestamp(self, timestamp):
        """Format Unix timestamp to readable time"""
        if not timestamp:
            return None
        
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)  # OTP uses milliseconds
            return dt.strftime('%H:%M')
        except:
            return None
    
    def find_nearest_station_by_type(self, origin_name, station_type_keywords, exclude_origin=True):
        """Find nearest station matching type keywords (like 'Local', 'Metro', etc.)"""
        origin_coords = self.get_station_coordinates(origin_name)
        if not origin_coords:
            return None
            
        best_station = None
        min_distance = float('inf')
        origin_lower = origin_name.lower()
        
        for station in self.stations:
            if isinstance(station, dict):
                station_name = station.get('name', '')
                station_name_lower = station_name.lower()
                
                # Skip if it's the same as origin and we want to exclude it
                if exclude_origin and station_name_lower == origin_lower:
                    continue
                
                # Check if station name contains any of the type keywords
                if any(keyword.lower() in station_name_lower for keyword in station_type_keywords):
                    # Calculate approximate distance
                    lat_diff = abs(station['lat'] - origin_coords['lat'])
                    lng_diff = abs(station['lng'] - origin_coords['lng'])
                    distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_station = station
        
        return best_station.get('name') if best_station else None
    
    def find_intermediate_station(self, origin_name, destination_name, station_type_keywords):
        """Find an intermediate station between origin and destination"""
        origin_coords = self.get_station_coordinates(origin_name)
        dest_coords = self.get_station_coordinates(destination_name)
        
        if not origin_coords or not dest_coords:
            return self.find_nearest_station_by_type(origin_name, station_type_keywords)
        
        # Calculate midpoint
        mid_lat = (origin_coords['lat'] + dest_coords['lat']) / 2
        mid_lng = (origin_coords['lng'] + dest_coords['lng']) / 2
        
        best_station = None
        min_distance = float('inf')
        
        for station in self.stations:
            if isinstance(station, dict):
                station_name = station.get('name', '').lower()
                # Check if station matches type
                if any(keyword.lower() in station_name for keyword in station_type_keywords):
                    # Calculate distance from midpoint
                    lat_diff = abs(station['lat'] - mid_lat)
                    lng_diff = abs(station['lng'] - mid_lng)
                    distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_station = station
        
        return best_station.get('name') if best_station else None
    
    def is_railway_corridor_route(self, origin, destination):
        """Check if this is a well-known railway corridor route"""
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Western Railway stations (south to north)
        wr_stations = ['churchgate', 'marine lines', 'charni road', 'grant road', 
                      'mumbai central', 'mahalaxmi', 'lower parel', 'dadar', 
                      'matunga', 'mahim', 'bandra', 'khar', 'santacruz', 
                      'vile parle', 'andheri', 'jogeshwari', 'goregaon', 
                      'malad', 'kandivali', 'borivali', 'dahisar', 'virar']
        
        # Central Railway stations (south to north)
        cr_stations = ['csmt', 'cst', 'masjid', 'sandhurst road', 'dockyard road',
                      'reay road', 'cotton green', 'sewri', 'wadala', 'kurla',
                      'vidyavihar', 'ghatkopar', 'vikhroli', 'bhandup', 'mulund',
                      'thane', 'dombivli', 'kalyan']
        
        # Check if both stations are on same line
        origin_in_wr = any(station in origin_lower for station in wr_stations)
        dest_in_wr = any(station in dest_lower for station in wr_stations)
        origin_in_cr = any(station in origin_lower for station in cr_stations)
        dest_in_cr = any(station in dest_lower for station in cr_stations)
        
        if origin_in_wr and dest_in_wr:
            return 'WR'
        elif origin_in_cr and dest_in_cr:
            return 'CR'
        elif (origin_in_wr and dest_in_cr) or (origin_in_cr and dest_in_wr):
            return 'CROSS_LINE'  # Need transfer at Dadar
        
        return None

    def get_intelligent_route(self, origin, destination):
        """Generate intelligent route based on actual Mumbai geography"""
        railway_route = self.is_railway_corridor_route(origin, destination)
        
        # For major railway corridors, provide direct train routes
        if railway_route == 'WR':
            return self.get_western_railway_route(origin, destination)
        elif railway_route == 'CR':
            return self.get_central_railway_route(origin, destination)
        elif railway_route == 'CROSS_LINE':
            return self.get_cross_line_route(origin, destination)
        else:
            return self.get_mixed_transport_route(origin, destination)

    def get_western_railway_route(self, origin, destination):
        """Generate Western Railway direct route"""
        return [
            {
                'route_id': 1,
                'duration': 35,
                'transfers': 0,
                'score': 9.2,
                'cost': 10,
                'eco_score': 9.5,
                'route_type': 'Direct',
                'fare_breakdown': [
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways (WR)',
                        'line': 'Western Line',
                        'from': origin,
                        'to': destination,
                        'distance_km': 15.2,
                        'fares': {
                            '2nd_class': 10,
                            '1st_class': 50,
                            'ac_local': 70
                        },
                        'default_fare': 10
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 3, 'from_name': origin, 'to_name': f'{origin} Station', 'distance': 150, 'route': '', 'route_number': ''},
                    {'mode': 'RAIL', 'route': 'Western Line Local', 'route_number': 'WR', 'duration': 30, 'from_name': f'{origin} Station', 'to_name': f'{destination} Station', 'distance': 15200},
                    {'mode': 'WALK', 'duration': 2, 'from_name': f'{destination} Station', 'to_name': destination, 'distance': 100, 'route': '', 'route_number': ''}
                ]
            }
        ]

    def get_central_railway_route(self, origin, destination):
        """Generate Central Railway direct route"""
        return [
            {
                'route_id': 1,
                'duration': 40,
                'transfers': 0,
                'score': 9.0,
                'cost': 15,
                'eco_score': 9.3,
                'route_type': 'Direct',
                'fare_breakdown': [
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways (CR)',
                        'line': 'Central Line',
                        'from': origin,
                        'to': destination,
                        'distance_km': 18.5,
                        'fares': {
                            '2nd_class': 15,
                            '1st_class': 65,
                            'ac_local': 85
                        },
                        'default_fare': 15
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 4, 'from_name': origin, 'to_name': f'{origin} Station', 'distance': 200, 'route': '', 'route_number': ''},
                    {'mode': 'RAIL', 'route': 'Central Line Local', 'route_number': 'CR', 'duration': 34, 'from_name': f'{origin} Station', 'to_name': f'{destination} Station', 'distance': 18500},
                    {'mode': 'WALK', 'duration': 2, 'from_name': f'{destination} Station', 'to_name': destination, 'distance': 120, 'route': '', 'route_number': ''}
                ]
            }
        ]

    def get_cross_line_route(self, origin, destination):
        """Generate route requiring transfer at Dadar"""
        return [
            {
                'route_id': 1,
                'duration': 55,
                'transfers': 1,
                'score': 8.5,
                'cost': 20,
                'eco_score': 8.8,
                'route_type': 'Express',
                'fare_breakdown': [
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways',
                        'line': 'WR + CR via Dadar',
                        'from': origin,
                        'to': destination,
                        'distance_km': 22.3,
                        'fares': {
                            '2nd_class': 20,
                            '1st_class': 85,
                            'ac_local': 105
                        },
                        'default_fare': 20
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 4, 'from_name': origin, 'to_name': f'{origin} Station', 'distance': 200, 'route': '', 'route_number': ''},
                    {'mode': 'RAIL', 'route': 'To Dadar Junction', 'route_number': 'LOCAL', 'duration': 25, 'from_name': f'{origin} Station', 'to_name': 'Dadar Station', 'distance': 12000},
                    {'mode': 'WALK', 'duration': 5, 'from_name': 'Dadar Station (Platform)', 'to_name': 'Dadar Station (Transfer)', 'distance': 150, 'route': '', 'route_number': ''},
                    {'mode': 'RAIL', 'route': 'From Dadar Junction', 'route_number': 'LOCAL', 'duration': 19, 'from_name': 'Dadar Station', 'to_name': f'{destination} Station', 'distance': 10300},
                    {'mode': 'WALK', 'duration': 2, 'from_name': f'{destination} Station', 'to_name': destination, 'distance': 120, 'route': '', 'route_number': ''}
                ]
            }
        ]

    def get_mixed_transport_route(self, origin, destination):
        """Generate mixed transport route for non-railway corridors"""
        # Find actual nearby stations for origin and destination
        origin_railway = self.find_nearest_station_by_type(origin, ['Local-CR', 'Local-WR', 'Local-Habr'], exclude_origin=True)
        dest_railway = self.find_nearest_station_by_type(destination, ['Local-CR', 'Local-WR', 'Local-Habr'], exclude_origin=True)
        origin_bus = self.find_nearest_station_by_type(origin, ['BEST'], exclude_origin=True)
        dest_bus = self.find_nearest_station_by_type(destination, ['BEST'], exclude_origin=True)
        
        # Use fallback names if needed
        railway_from = origin_railway if origin_railway else 'Nearest Railway Station'
        railway_to = dest_railway if dest_railway else 'Destination Railway Station'
        bus_from = origin_bus if origin_bus else 'Nearby Bus Stop'
        bus_to = dest_bus if dest_bus else 'Destination Bus Stop'
        
        return [
            {
                'route_id': 1,
                'duration': 45,
                'transfers': 1,
                'score': 8.2,
                'cost': 25,
                'eco_score': 8.5,
                'route_type': 'Mixed',
                'fare_breakdown': [
                    {
                        'mode': 'BUS',
                        'operator': 'BEST',
                        'from': bus_from,
                        'to': railway_from,
                        'distance_km': 2.5,
                        'fare': 15,
                        'route_number': 'BEST'
                    },
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways',
                        'line': 'Local Train',
                        'from': railway_from,
                        'to': railway_to,
                        'distance_km': 8.2,
                        'fares': {
                            '2nd_class': 10,
                            '1st_class': 45,
                            'ac_local': 65
                        },
                        'default_fare': 10
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 5, 'from_name': origin, 'to_name': bus_from, 'distance': 300, 'route': '', 'route_number': ''},
                    {'mode': 'BUS', 'route': 'BEST Bus', 'route_number': 'BEST', 'duration': 18, 'from_name': bus_from, 'to_name': railway_from, 'distance': 2500},
                    {'mode': 'RAIL', 'route': 'Local Train', 'route_number': 'LOCAL', 'duration': 20, 'from_name': railway_from, 'to_name': railway_to, 'distance': 8200},
                    {'mode': 'WALK', 'duration': 2, 'from_name': railway_to, 'to_name': destination, 'distance': 150, 'route': '', 'route_number': ''}
                ]
            }
        ]
    def get_mock_routes(self, origin, destination, user_profile):
        """Generate intelligent routes based on Mumbai transport geography"""
        print(f"🎯 Generating intelligent routes for: {origin} → {destination}")
        
        # Use intelligent routing based on actual Mumbai transport network
        routes = self.get_intelligent_route(origin, destination)
        
        # Add alternative routes based on profile preferences
        if len(routes) == 1:
            # Add a bus-only alternative for comparison
            bus_route = self.get_bus_alternative_route(origin, destination)
            if bus_route:
                routes.extend(bus_route)
        
        print(f"✅ Generated {len(routes)} intelligent routes")
        return routes[:3]  # Return max 3 routes

    def get_bus_alternative_route(self, origin, destination):
        """Generate bus-only alternative route"""
        origin_bus = self.find_nearest_station_by_type(origin, ['BEST'], exclude_origin=True)
        dest_bus = self.find_nearest_station_by_type(destination, ['BEST'], exclude_origin=True)
        
        if not origin_bus or not dest_bus:
            return None
            
        return [
            {
                'route_id': 2,
                'duration': 65,
                'transfers': 1,
                'score': 7.8,
                'cost': 30,
                'eco_score': 7.5,
                'route_type': 'Budget',
                'fare_breakdown': [
                    {
                        'mode': 'BUS',
                        'operator': 'BEST',
                        'from': origin_bus,
                        'to': dest_bus,
                        'distance_km': 12.5,
                        'fare': 25,
                        'route_number': 'BEST'
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 8, 'from_name': origin, 'to_name': origin_bus, 'distance': 500, 'route': '', 'route_number': ''},
                    {'mode': 'BUS', 'route': 'BEST Direct', 'route_number': 'BEST', 'duration': 55, 'from_name': origin_bus, 'to_name': dest_bus, 'distance': 12500},
                    {'mode': 'WALK', 'duration': 2, 'from_name': dest_bus, 'to_name': destination, 'distance': 150, 'route': '', 'route_number': ''}
                ]
            }
        ]