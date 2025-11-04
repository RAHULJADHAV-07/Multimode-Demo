import React, { useState, useEffect } from 'react';

const RouteSearch = ({ onRouteSearch, stations, loading }) => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [selectedVehicles, setSelectedVehicles] = useState(['all']);
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destinationSuggestions, setDestinationSuggestions] = useState([]);
  const [showOriginSuggestions, setShowOriginSuggestions] = useState(false);
  const [showDestinationSuggestions, setShowDestinationSuggestions] = useState(false);
  
  const vehicleTypes = [
    { id: 'walk', label: 'Walk', icon: '🚶', color: 'green', eco: true },
    { id: 'bus', label: 'Bus', icon: '🚌', color: 'orange', eco: true },
    { id: 'train', label: 'Train', icon: '🚊', color: 'blue', eco: true },
    { id: 'metro', label: 'Metro', icon: '🚇', color: 'purple', eco: true },
    { id: 'auto', label: 'Auto', icon: '🛺', color: 'yellow', eco: false },
    { id: 'all', label: 'All', icon: '🌍', color: 'emerald', eco: false }
  ];

  const handleVehicleSelect = (vehicleId) => {
    if (vehicleId === 'all') {
      setSelectedVehicles(['all']);
    } else {
      const newSelection = selectedVehicles.filter(v => v !== 'all');
      if (newSelection.includes(vehicleId)) {
        const filtered = newSelection.filter(v => v !== vehicleId);
        setSelectedVehicles(filtered.length === 0 ? ['all'] : filtered);
      } else {
        setSelectedVehicles([...newSelection, vehicleId]);
      }
    }
  };

  const searchStations = (query) => {
    if (!query || query.length < 2) return [];
    
    const lowercaseQuery = query.toLowerCase();
    return stations
      .filter(station => station.name.toLowerCase().includes(lowercaseQuery))
      .slice(0, 8);
  };

  const handleOriginChange = (e) => {
    const value = e.target.value;
    setOrigin(value);
    
    if (value.length >= 2) {
      setOriginSuggestions(searchStations(value));
      setShowOriginSuggestions(true);
    } else {
      setShowOriginSuggestions(false);
    }
  };

  const handleDestinationChange = (e) => {
    const value = e.target.value;
    setDestination(value);
    
    if (value.length >= 2) {
      setDestinationSuggestions(searchStations(value));
      setShowDestinationSuggestions(true);
    } else {
      setShowDestinationSuggestions(false);
    }
  };

  const selectOriginSuggestion = (station) => {
    setOrigin(station.name);
    setShowOriginSuggestions(false);
  };

  const selectDestinationSuggestion = (station) => {
    setDestination(station.name);
    setShowDestinationSuggestions(false);
  };

  // Pre-populated route suggestions for easier testing
  const quickRoutes = [
    { from: 'CHURCHGATE', to: 'ANDHERI', icon: '🚊', label: 'Western Line' },
    { from: 'CST', to: 'THANE', icon: '🚄', label: 'Central Line' },
    { from: 'BANDRA', to: 'GHATKOPAR', icon: '🚇', label: 'Cross Mumbai' },
    { from: 'DADAR', to: 'BORIVALI', icon: '🚌', label: 'North Route' }
  ];

  const useQuickRoute = (route) => {
    setOrigin(route.from);
    setDestination(route.to);
    setShowOriginSuggestions(false);
    setShowDestinationSuggestions(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (origin && destination) {
      const searchParams = {
        vehicleTypes: selectedVehicles,
        routePreference: 'eco' // Default to eco-friendly
      };
      onRouteSearch(origin, destination, searchParams);
    }
  };
  
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-blue-600 p-3 sm:p-6 text-white">
        <h2 className="text-base sm:text-2xl font-bold mb-2 flex items-center">
          <span className="mr-2 sm:mr-3 text-lg sm:text-2xl">🌱</span>
          <span className="truncate">Eco-Friendly Journey Planner</span>
        </h2>
        <p className="text-green-100 text-[10px] sm:text-sm leading-tight sm:leading-normal">
          Sustainable travel with minimal transfers • Walking • Public Transit • Green Routes
        </p>
      </div>
      <div className="p-3 sm:p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="relative">
              <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                <span className="text-green-600 mr-2">📍</span>
                From
              </label>
              <input
                type="text"
                value={origin}
                onChange={handleOriginChange}
                onBlur={() => setTimeout(() => setShowOriginSuggestions(false), 200)}
                placeholder="Enter origin station..."
                className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm sm:text-base"
                required
              />
              {showOriginSuggestions && originSuggestions.length > 0 && (
                <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1 max-h-48 sm:max-h-60 overflow-y-auto">
                  {originSuggestions.map((station, index) => (
                    <div
                      key={index}
                      onClick={() => selectOriginSuggestion(station)}
                      className="p-2 sm:p-3 hover:bg-green-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900 text-sm sm:text-base">{station.name}</div>
                      <div className="text-xs text-gray-500">
                        {station.lat && station.lng ? `${station.lat.toFixed(4)}, ${station.lng.toFixed(4)}` : 'Mumbai Transit'}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="relative">
              <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                <span className="text-blue-600 mr-2">🎯</span>
                To
              </label>
              <input
                type="text"
                value={destination}
                onChange={handleDestinationChange}
                onBlur={() => setTimeout(() => setShowDestinationSuggestions(false), 200)}
                placeholder="Enter destination station..."
                className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base"
                required
              />
              {showDestinationSuggestions && destinationSuggestions.length > 0 && (
                <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1 max-h-48 sm:max-h-60 overflow-y-auto">
                  {destinationSuggestions.map((station, index) => (
                    <div
                      key={index}
                      onClick={() => selectDestinationSuggestion(station)}
                      className="p-2 sm:p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900 text-sm sm:text-base">{station.name}</div>
                      <div className="text-xs text-gray-500">{station.lat && station.lng ? `${station.lat.toFixed(4)}, ${station.lng.toFixed(4)}` : 'Mumbai Transit'}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Route Suggestions */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="text-green-600 mr-2">⚡</span>
              Quick Routes
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {quickRoutes.map((route, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => useQuickRoute(route)}
                  className="p-2 bg-white border border-gray-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-all duration-200 text-center"
                >
                  <div className="text-lg mb-1">{route.icon}</div>
                  <div className="text-xs font-medium text-gray-700">{route.label}</div>
                  <div className="text-xs text-gray-500">{route.from} → {route.to}</div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Vehicle Type Filters */}
          <div className="space-y-3">
            <label className="flex items-center text-sm font-semibold text-gray-700">
              <span className="text-green-600 mr-2">🚗</span>
              Travel Mode
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {vehicleTypes.map((vehicle) => (
                <button
                  key={vehicle.id}
                  type="button"
                  onClick={() => handleVehicleSelect(vehicle.id)}
                  className={`p-2 sm:p-3 rounded-lg border-2 transition-all duration-200 flex flex-col items-center space-y-1 relative ${
                    selectedVehicles.includes(vehicle.id) || selectedVehicles.includes('all')
                      ? 'border-green-500 bg-green-50 text-green-700 shadow-md'
                      : 'border-gray-300 bg-gray-50 text-gray-600 hover:border-gray-400'
                  }`}
                >
                  <span className="text-lg sm:text-xl">{vehicle.icon}</span>
                  <span className="text-xs font-medium">{vehicle.label}</span>
                  {vehicle.eco && (
                    <div className="absolute -top-1 -right-1 text-xs">🌱</div>
                  )}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2 flex items-center">
              <span className="text-green-600 mr-1">🌱</span>
              Green options are eco-friendly and recommended
            </p>
          </div>

          {/* Route Features */}
          <div className="p-3 sm:p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-center flex-wrap gap-2 sm:gap-6 text-xs sm:text-sm text-gray-700">
              <div className="flex items-center space-x-1 sm:space-x-2">
                <span className="text-base sm:text-lg">🌱</span>
                <span className="whitespace-nowrap">Eco-Friendly</span>
              </div>
              <div className="flex items-center space-x-1 sm:space-x-2">
                <span className="text-base sm:text-lg">⚡</span>
                <span className="whitespace-nowrap">Fastest</span>
              </div>
              <div className="flex items-center space-x-1 sm:space-x-2">
                <span className="text-base sm:text-lg">💰</span>
                <span className="whitespace-nowrap">Cheapest</span>
              </div>
              <div className="flex items-center space-x-1 sm:space-x-2">
                <span className="text-base sm:text-lg">🔄</span>
                <span className="whitespace-nowrap hidden sm:inline">Fewest Transfers</span>
                <span className="whitespace-nowrap sm:hidden">Few Transfers</span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 sm:py-4 px-4 sm:px-6 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm sm:text-base"
          >
            <span className="text-base sm:text-lg">🌱</span>
            <span>{loading ? 'Finding Eco Routes...' : '🔍 Find Sustainable Routes'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default RouteSearch;