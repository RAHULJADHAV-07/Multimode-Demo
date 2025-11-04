import React, { useState } from 'react';
import RouteDetailModal from './RouteDetailModal';
import MapModal from './MapModal';

const RouteResults = ({ routes, selectedRoute, onRouteSelect, loading, error, origin, destination }) => {
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [mapModalOpen, setMapModalOpen] = useState(false);
  const [modalRoute, setModalRoute] = useState(null);
  
  const handleRouteClick = (route) => {
    onRouteSelect(route);
  };

  const handleDetailClick = (route, event) => {
    event.stopPropagation(); // Prevent route selection
    setModalRoute(route);
    setDetailModalOpen(true);
  };

  const handleMapClick = (route, event) => {
    event.stopPropagation(); // Prevent route selection
    onRouteSelect(route); // Select the route first
    setModalRoute(route);
    setMapModalOpen(true);
  };
  
  const getModeIcon = (mode) => {
    const icons = {
      'WALK': '🚶',
      'BUS': '🚌',
      'RAIL': '🚂',
      'SUBWAY': '🚇',
      'TRAM': '🚋',
      'AUTO': '🛺'
    };
    return icons[mode] || '🚌';
  };

  const getRouteTypeColor = (type) => {
    const colors = {
      'Best': 'bg-green-100 text-green-800',
      'Fastest': 'bg-blue-100 text-blue-800',
      'Budget': 'bg-yellow-100 text-yellow-800',
      'Eco': 'bg-emerald-100 text-emerald-800',
      'Direct': 'bg-purple-100 text-purple-800',
      'Good': 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-center py-8">
          <div className="spinner mr-3"></div>
          <span className="text-gray-600">Finding best routes...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center py-8">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <h3 className="text-lg font-medium text-gray-800 mb-2">Unable to find routes</h3>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (routes.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center py-8">
          <div className="text-gray-400 text-2xl mb-2">🗺️</div>
          <h3 className="text-lg font-medium text-gray-800 mb-2">Ready to plan</h3>
          <p className="text-sm text-gray-600">Select origin and destination to see route options</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-2 sm:p-6">
      <h3 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4 flex items-center px-2 sm:px-0">
        <span className="mr-2">📍</span>
        Route Options ({routes.length})
      </h3>
      
      <div className="space-y-3 sm:space-y-4">
        {routes.map((route) => (
          <div
            key={route.route_id}
            className={`route-card rounded-xl border-2 cursor-pointer transition-all shadow-sm hover:shadow-md ${
              selectedRoute?.route_id === route.route_id
                ? 'border-blue-500 bg-blue-50 shadow-lg'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
            onClick={() => handleRouteClick(route)}
          >
            {/* Mobile-optimized Route Header */}
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getRouteTypeColor(route.route_type)}`}>
                    {route.route_type}
                  </span>
                  <div className="text-lg font-bold text-gray-800">
                    {route.duration}m
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">₹{route.cost}</div>
                  <div className="text-xs text-gray-500">Score: {route.score}/10</div>
                </div>
              </div>

              {/* Action buttons - Mobile optimized */}
              <div className="flex space-x-2 mb-3">
                <button
                  onClick={(e) => handleMapClick(route, e)}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 px-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
                  title="Show route on map"
                >
                  <span>🗺️</span>
                  <span>View Map</span>
                </button>
                <button
                  onClick={(e) => handleDetailClick(route, e)}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
                  title="View detailed route information"
                >
                  <span>ℹ️</span>
                  <span>Details</span>
                </button>
              </div>

              {/* Mobile-friendly Route Details */}
              <div className="space-y-3">
                {/* Quick Stats Row */}
                <div className="flex justify-between items-center bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center text-gray-600">
                      <span className="mr-1">🔄</span>
                      <span className="font-medium">{route.transfers}</span>
                      <span className="text-sm ml-1">transfer{route.transfers !== 1 ? 's' : ''}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="mr-1">🌱</span>
                      <span className="font-medium">{route.eco_score}</span>
                      <span className="text-sm ml-1">/10</span>
                    </div>
                  </div>
                </div>

                {/* Route Journey Steps - Mobile optimized */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700 mb-2">Journey Steps:</div>
                  <div className="grid grid-cols-1 gap-2">
                    {route.legs && route.legs.slice(0, 5).map((leg, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getModeIcon(leg.mode)}</span>
                          <div>
                            <div className="font-medium text-sm text-gray-800">
                              {leg.mode === 'WALK' ? 
                                `Walk ${leg.duration}m` : 
                                (leg.route || leg.mode)
                              }
                            </div>
                            <div className="text-xs text-gray-500">
                              {leg.from_name} → {leg.to_name}
                            </div>
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {leg.duration}min
                        </div>
                      </div>
                    ))}
                    {route.legs && route.legs.length > 5 && (
                      <div className="text-center text-sm text-gray-500 py-1">
                        ... and {route.legs.length - 5} more steps
                      </div>
                    )}
                  </div>
                </div>

                {/* Last Mile Options - Mobile friendly */}
                {route.last_mile && route.last_mile.length > 0 && (
                  <div className="border-t border-gray-100 pt-3">
                    <div className="text-sm font-medium text-gray-700 mb-2">Last-mile options:</div>
                    <div className="grid grid-cols-3 gap-2">
                      {route.last_mile.slice(0, 3).map((option, index) => (
                        <button
                          key={index}
                          className="bg-blue-50 hover:bg-blue-100 text-blue-800 p-2 rounded-lg transition-colors text-center"
                          title={`${option.name}: ₹${option.cost}, ${option.time} min`}
                        >
                          <div className="text-lg mb-1">{option.icon}</div>
                          <div className="text-xs font-medium">₹{option.cost}</div>
                          <div className="text-xs text-blue-600">{option.time}m</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Mobile-optimized Route Comparison */}
      {routes.length > 1 && (
        <div className="mt-4 mx-2 sm:mx-0">
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-medium text-gray-800 mb-3">Quick Comparison</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Fastest</div>
                <div className="font-bold text-blue-600">{Math.min(...routes.map(r => r.duration))}m</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Cheapest</div>
                <div className="font-bold text-green-600">₹{Math.min(...routes.map(r => r.cost))}</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Fewest Transfers</div>
                <div className="font-bold text-purple-600">{Math.min(...routes.map(r => r.transfers))}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Route Detail Modal */}
      <RouteDetailModal
        route={modalRoute}
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setModalRoute(null);
        }}
        origin={origin}
        destination={destination}
      />

      {/* Map Modal */}
      <MapModal
        route={modalRoute}
        isOpen={mapModalOpen}
        onClose={() => {
          setMapModalOpen(false);
          setModalRoute(null);
        }}
        origin={origin}
        destination={destination}
      />
    </div>
  );
};

export default RouteResults;