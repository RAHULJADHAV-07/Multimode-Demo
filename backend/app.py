from flask import Flask, request, jsonify
from flask_cors import CORS
from route_optimizer import RouteOptimizer
from last_mile_service import LastMileService
from user_profiles import UserProfileManager
import json
import time

app = Flask(__name__)
CORS(app)

# Initialize services
route_optimizer = RouteOptimizer()
last_mile_service = LastMileService()
profile_manager = UserProfileManager()

def filter_routes_by_vehicle_types(routes, vehicle_types):
    """Filter routes based on allowed vehicle types"""
    if 'all' in vehicle_types:
        return routes
    
    filtered_routes = []
    mode_mapping = {
        'walk': ['WALK'],
        'bus': ['BUS'],
        'train': ['RAIL'],
        'metro': ['SUBWAY'],
        'auto': ['AUTO', 'CAR']
    }
    
    allowed_modes = set()
    for vehicle_type in vehicle_types:
        if vehicle_type in mode_mapping:
            allowed_modes.update(mode_mapping[vehicle_type])
    
    for route in routes:
        route_modes = set()
        for leg in route.get('legs', []):
            mode = leg.get('mode', '')
            route_modes.add(mode)
        
        # Check if route uses only allowed modes (except WALK which is always allowed)
        non_walk_modes = route_modes - {'WALK'}
        if not non_walk_modes or non_walk_modes.issubset(allowed_modes):
            filtered_routes.append(route)
    
    return filtered_routes

def sort_routes_by_preference(routes, route_preference):
    """Sort routes based on user's route preference"""
    if route_preference == 'fastest':
        return sorted(routes, key=lambda r: r.get('duration', 999))
    elif route_preference == 'cheapest':
        return sorted(routes, key=lambda r: r.get('cost', 999))
    elif route_preference == 'fewest':
        return sorted(routes, key=lambda r: (r.get('transfers', 999), r.get('duration', 999)))
    else:  # eco-friendly (default)
        return sorted(routes, key=lambda r: -r.get('eco_score', 0))  # Descending eco score

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Yatri API',
        'version': '1.0.0'
    })

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get all stations for dropdown"""
    try:
        stations = route_optimizer.get_all_stations()
        return jsonify({
            'success': True,
            'stations': stations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plan', methods=['POST'])
def plan_journey():
    """Main route planning endpoint with vehicle type and route preference filtering"""
    try:
        data = request.json
        
        # Validate input
        if not data.get('origin') or not data.get('destination'):
            return jsonify({
                'success': False,
                'error': 'Origin and destination are required'
            }), 400
        
        origin = data['origin']
        destination = data['destination']
        profile_type = data.get('profile', 'comfort')
        
        # Extract new filter parameters
        filters = data.get('filters', {})
        vehicle_types = filters.get('vehicleTypes', ['all'])
        route_preference = filters.get('routePreference', 'eco')
        
        print(f"Planning route from {origin} to {destination}")
        print(f"Profile: {profile_type}, Vehicle types: {vehicle_types}, Route preference: {route_preference}")
        
        # Get user profile preferences and merge with filters
        user_profile = profile_manager.get_profile(profile_type)
        
        # Apply vehicle type filters to profile
        if 'all' not in vehicle_types:
            user_profile['allowed_modes'] = vehicle_types
        else:
            user_profile['allowed_modes'] = ['walk', 'bus', 'train', 'metro', 'auto']
        
        # Apply route preference to profile
        if route_preference == 'fastest':
            user_profile['time_preference'] = 0.7
            user_profile['transfer_preference'] = 0.2
            user_profile['cost_preference'] = 0.1
        elif route_preference == 'cheapest':
            user_profile['cost_preference'] = 0.7
            user_profile['time_preference'] = 0.2
            user_profile['transfer_preference'] = 0.1
        elif route_preference == 'fewest':
            user_profile['transfer_preference'] = 0.7
            user_profile['time_preference'] = 0.2
            user_profile['cost_preference'] = 0.1
        else:  # eco-friendly
            user_profile['eco_preference'] = 0.5
            user_profile['transfer_preference'] = 0.3
            user_profile['time_preference'] = 0.2
        
        # Get optimized routes with filters
        routes = route_optimizer.get_routes(origin, destination, user_profile)
        
        # Filter routes based on vehicle type preferences
        if 'all' not in vehicle_types:
            routes = filter_routes_by_vehicle_types(routes, vehicle_types)
        
        # Sort routes based on route preference
        routes = sort_routes_by_preference(routes, route_preference)
        
        # Get coordinates for last-mile calculations
        origin_coords = route_optimizer.get_station_coordinates(origin)
        destination_coords = route_optimizer.get_station_coordinates(destination)
        
        if not routes:
            return jsonify({
                'success': True,
                'routes': [],
                'message': 'No suitable routes found with the selected filters. Try adjusting your preferences.'
            })
        
        # Add last-mile options to each route with real coordinates
        for route in routes:
            route['last_mile'] = last_mile_service.get_options(
                origin, destination, origin_coords, destination_coords
            )
        
        return jsonify({
            'success': True,
            'routes': routes,
            'profile': profile_type,
            'filters': filters,
            'origin': origin,
            'destination': destination
        })
        
    except Exception as e:
        print(f"Error in plan_journey: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Route planning failed: {str(e)}'
        }), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all user profiles"""
    return jsonify({
        'success': True,
        'profiles': profile_manager.get_all_profiles()
    })

@app.route('/api/debug/stations', methods=['GET'])
def debug_stations():
    """Debug endpoint to search stations"""
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 20))
    
    if search:
        # Filter stations by search term
        filtered = []
        search_lower = search.lower()
        for station in route_optimizer.stations[:200]:  # Limit to first 200 for performance
            if isinstance(station, dict):
                name = station.get('name', '').lower()
                if search_lower in name or name in search_lower:
                    filtered.append({
                        'name': station.get('name'),
                        'lat': station.get('lat'),
                        'lng': station.get('lng') or station.get('lon')
                    })
        return jsonify({
            'success': True,
            'stations': filtered[:limit],
            'total_found': len(filtered),
            'search_term': search
        })
    else:
        # Return first few stations
        sample = []
        for station in route_optimizer.stations[:limit]:
            if isinstance(station, dict):
                sample.append({
                    'name': station.get('name'),
                    'lat': station.get('lat'),
                    'lng': station.get('lng') or station.get('lon')
                })
        return jsonify({
            'success': True,
            'stations': sample,
            'total_loaded': len(route_optimizer.stations)
        })

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for routes"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'message', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create feedback record
        feedback = {
            'id': f"feedback_{int(time.time())}",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': data['type'],
            'message': data['message'],
            'rating': int(data['rating']),
            'email': data.get('email', ''),
            'route': data.get('route', ''),
            'route_details': data.get('routeDetails', {}),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # In a real app, you'd save this to a database
        # For now, we'll just log it and store in memory
        print(f"📝 New feedback received:")
        print(f"   Type: {feedback['type']}")
        print(f"   Rating: {feedback['rating']}/5")
        print(f"   Route: {feedback['route']}")
        print(f"   Message: {feedback['message'][:100]}...")
        print(f"   Email: {feedback['email'] or 'Not provided'}")
        
        # You could save to file or database here
        # save_feedback_to_file(feedback)
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback['id']
        })
        
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback'
        }), 500

if __name__ == '__main__':
    print("🚆 Starting Yatri Backend Server...")
    print("📍 API will be available at: http://localhost:5000")
    print("📋 Endpoints:")
    print("   GET  /api/health - Health check")
    print("   GET  /api/stations - Get all stations")
    print("   POST /api/plan - Plan journey")
    print("   GET  /api/profiles - Get user profiles")
    print("   POST /api/feedback - Submit route feedback")
    print("\n✅ Backend using stations.json data only (OTP server removed)")
    print("� Stations loaded from: data/stations.json")
    
    app.run(debug=True, port=5000, host='0.0.0.0')