import React, { useState, useEffect } from 'react';
import RouteSearch from './components/RouteSearch';
import RouteResults from './components/RouteResults';
import yatriLogo from './assets/yatri-removebg-preview.png';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

// Simple fetch wrapper to replace axios
const api = {
  get: async (url) => {
    const response = await fetch(`${API_BASE_URL}${url}`);
    return { data: await response.json() };
  },
  post: async (url, data) => {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return { data: await response.json() };
  }
};

function App() {
  const [stations, setStations] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [userProfile, setUserProfile] = useState({
    preferredMode: 'balanced',
    walkingTolerance: 500,
    maxTransfers: 2,
    timePreference: 'fastest'
  });

  // Load stations on app start
  useEffect(() => {
    loadStations();
  }, []);

  const loadStations = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stations');
      const data = await response.json();
      
      if (data.success && Array.isArray(data.stations)) {
        setStations(data.stations);
        console.log(`Loaded ${data.stations.length} stations`);
      } else {
        console.error('Invalid stations data:', data);
      }
    } catch (error) {
      console.error('Error loading stations:', error);
    }
  };

  const handleRouteSearch = async (origin, destination, searchParams = {}) => {
    setLoading(true);
    setError(null);
    setRoutes([]);
    setSelectedRoute(null);
    
    // Store origin and destination for the modal
    setOrigin(origin);
    setDestination(destination);
    
    // Extract filters from searchParams
    const filters = {
      vehicleTypes: searchParams.vehicleTypes || ['all'],
      routePreference: searchParams.routePreference || 'eco'
    };

    try {
      console.log('Searching routes from', origin, 'to', destination, 'with filters:', filters);
      
      const requestBody = {
        origin: origin,
        destination: destination,
        preferences: userProfile,
        filters: filters // Include the new filters
      };

      const response = await fetch('http://localhost:5000/api/plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      console.log('Route planning response:', data);

      if (data.success && Array.isArray(data.routes)) {
        setRoutes(data.routes);
        if (data.routes.length > 0) {
          setSelectedRoute(data.routes[0]); // Auto-select first route
        }
      } else {
        setError(data.error || 'No routes found');
      }
    } catch (error) {
      console.error('Error planning route:', error);
      setError('Unable to plan route. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRouteSelect = (route) => {
    setSelectedRoute(route);
    console.log('Selected route:', route);
  };

  const handleProfileUpdate = (profile) => {
    setUserProfile(profile);
    console.log('Updated user profile:', profile);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-500 to-blue-600 shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 lg:px-8">
          {/* Main Header Row */}
          <div className="flex items-center justify-between h-20">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <img 
                  src={yatriLogo} 
                  alt="Yatri Logo" 
                  className="h-12 w-auto object-contain"
                />
                <div className="ml-3">
                  <h1 className="text-2xl font-bold text-white">Yatri</h1>
                  <p className="text-sm text-green-100 font-medium">Smart Journey Planner</p>
                </div>
              </div>
            </div>

            {/* Network Status & Stats */}
            <div className="hidden md:flex items-center space-x-6">
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm font-semibold text-white">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white bg-opacity-20 text-white">
                      <span className="w-2 h-2 bg-green-300 rounded-full mr-2 animate-pulse"></span>
                      {stations.length} stations loaded
                    </span>
                  </div>
                  <p className="text-xs text-green-200 mt-1">Mumbai Transit Network</p>
                </div>
              </div>
              
              {/* Feature Pills */}
              <div className="flex items-center space-x-2">
                <div className="flex items-center px-3 py-1.5 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-full">
                  <span className="text-green-200 text-sm mr-1">🌱</span>
                  <span className="text-xs font-medium text-white">Eco-First</span>
                </div>
                <div className="flex items-center px-3 py-1.5 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-full">
                  <span className="text-blue-200 text-sm mr-1">🔄</span>
                  <span className="text-xs font-medium text-white">Min Transfers</span>
                </div>
              </div>
            </div>

            {/* Mobile Menu Button (for future use) */}
            <div className="md:hidden">
              <button className="p-2 rounded-lg text-white hover:text-green-200 hover:bg-white hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>

          {/* Sub-header with tagline */}
          <div className="border-t border-white border-opacity-20 py-3">
            <div className="flex flex-col sm:flex-row items-center justify-between">
              <div className="flex items-center space-x-6 text-sm text-green-200">
                <div className="flex items-center">
                  <span className="text-green-200 mr-1">🚶</span>
                  <span>Walking</span>
                </div>
                <div className="flex items-center">
                  <span className="text-blue-200 mr-1">🚇</span>
                  <span>Metro</span>
                </div>
                <div className="flex items-center">
                  <span className="text-purple-500 mr-1">�</span>
                  <span>Train</span>
                </div>
                <div className="flex items-center">
                  <span className="text-orange-200 mr-1">🚌</span>
                  <span>Bus</span>
                </div>
                <div className="hidden sm:flex items-center">
                  <span className="text-emerald-200 mr-1">♻️</span>
                  <span>Sustainable Travel</span>
                </div>
              </div>
              
              <div className="mt-2 sm:mt-0 text-xs text-green-200 font-medium">
                Eco-Friendly • Minimal Transfers • Real-time Routes
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-8">
        <div className="space-y-6 sm:space-y-8">
          {/* Search Section */}
          <div className="w-full">
            <RouteSearch
              onRouteSearch={handleRouteSearch}
              stations={stations}
              loading={loading}
            />
          </div>

          {/* Results Section */}
          <div className="w-full">
            <RouteResults
              routes={routes}
              selectedRoute={selectedRoute}
              onRouteSelect={handleRouteSelect}
              loading={loading}
              error={error}
              origin={origin}
              destination={destination}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center text-gray-800">
                <span className="mr-2">🌱</span>
                Eco-Friendly Travel
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Prioritizing sustainable transport options like walking, cycling, metro, and public transit for a greener Mumbai.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center text-gray-800">
                <span className="mr-2">🔄</span>
                Minimal Transfers
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Optimized routes with 1-2 transfers for comfortable and efficient journeys. Balancing time, cost, and sustainability.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center text-gray-800">
                <span className="mr-2">🚊</span>
                Smart Routing
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Enhanced OpenTripPlanner integration with real Mumbai transit data for practical and comfortable travel solutions.
              </p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center space-x-3 mb-4 sm:mb-0">
              <img src={yatriLogo} alt="Yatri" className="h-8 w-auto object-contain" />
              <div>
                <div className="text-sm font-semibold text-gray-800">
                  © 2024 Yatri - Empowering sustainable commuting in Mumbai
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center space-x-6 text-sm text-gray-600">
              <span className="flex items-center">
                <span className="text-green-500 mr-1">🌍</span>
                Carbon Neutral
              </span>
              <span className="flex items-center">
                <span className="text-blue-500 mr-1">⚡</span>
                Real-time Data
              </span>
              <span className="flex items-center">
                <span className="text-purple-500 mr-1">🎯</span>
                User-Optimized
              </span>
            </div>
          </div>
        </div>
      </footer>

      {/* Loading Spinner Styles */}
      <style jsx>{`
        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #f3f4f6;
          border-top: 2px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;