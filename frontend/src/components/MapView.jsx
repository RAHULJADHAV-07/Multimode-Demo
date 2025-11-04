import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet with Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapView = ({ routes, selectedRoute }) => {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const routeLayer = useRef(null);

  useEffect(() => {
    // Initialize Leaflet map when component mounts
    if (mapRef.current && !leafletMap.current) {
      initializeLeafletMap();
    }

    // Cleanup function
    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove();
        leafletMap.current = null;
      }
    };
  }, []);

  useEffect(() => {
    // Update map when selected route changes
    if (selectedRoute && leafletMap.current) {
      updateMapWithRoute(selectedRoute);
    }
  }, [selectedRoute]);

  const initializeLeafletMap = () => {
    // Mumbai coordinates (center of the city)
    const mumbaiCenter = [19.0760, 72.8777];
    
    // Create the map
    leafletMap.current = L.map(mapRef.current, {
      center: mumbaiCenter,
      zoom: 11,
      zoomControl: true,
      scrollWheelZoom: true,
    });

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(leafletMap.current);

    // Add Mumbai boundary and points of interest
    addMumbaiLandmarks();
  };

  const addMumbaiLandmarks = () => {
    if (!leafletMap.current) return;

    // Major Mumbai landmarks
    const landmarks = [
      { name: 'Gateway of India', coords: [18.9220, 72.8347], type: 'landmark' },
      { name: 'Chhatrapati Shivaji Terminus', coords: [18.9398, 72.8355], type: 'station' },
      { name: 'Mumbai Central', coords: [18.9686, 72.8181], type: 'station' },
      { name: 'Bandra Kurla Complex', coords: [19.0596, 72.8656], type: 'business' },
      { name: 'Andheri Station', coords: [19.1197, 72.8469], type: 'station' },
      { name: 'Thane Station', coords: [19.1972, 72.9636], type: 'station' },
    ];

    landmarks.forEach(landmark => {
      const icon = L.divIcon({
        html: `<div class="landmark-marker ${landmark.type}">
                 <span class="landmark-name">${landmark.name}</span>
               </div>`,
        className: 'custom-landmark',
        iconSize: [120, 30],
        iconAnchor: [60, 15]
      });

      L.marker(landmark.coords, { icon })
        .addTo(leafletMap.current)
        .bindPopup(`<strong>${landmark.name}</strong><br/>Type: ${landmark.type}`);
    });
  };

  const updateMapWithRoute = (route) => {
    if (!leafletMap.current) return;

    // Clear existing route layer
    if (routeLayer.current) {
      leafletMap.current.removeLayer(routeLayer.current);
    }

    // Create new layer group for route
    routeLayer.current = L.layerGroup().addTo(leafletMap.current);

    if (route.legs && route.legs.length > 0) {
      // Generate realistic Mumbai coordinates for route visualization
      const routeCoords = generateRouteCoordinates(route);
      
      // Create route polyline
      const routeLine = L.polyline(routeCoords, {
        color: '#3b82f6',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 5'
      }).addTo(routeLayer.current);

      // Add start marker (green)
      const startIcon = L.divIcon({
        html: '<div class="route-marker start">🚀</div>',
        className: 'custom-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });
      
      L.marker(routeCoords[0], { icon: startIcon })
        .addTo(routeLayer.current)
        .bindPopup('<strong>Start</strong><br/>Your journey begins here');

      // Add end marker (red)
      const endIcon = L.divIcon({
        html: '<div class="route-marker end">🎯</div>',
        className: 'custom-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });
      
      L.marker(routeCoords[routeCoords.length - 1], { icon: endIcon })
        .addTo(routeLayer.current)
        .bindPopup('<strong>Destination</strong><br/>Your journey ends here');

      // Add transfer points
      if (route.transfers > 0 && routeCoords.length > 2) {
        const transferPoints = Math.floor(routeCoords.length / (route.transfers + 1));
        for (let i = 1; i <= route.transfers; i++) {
          const transferIndex = transferPoints * i;
          if (transferIndex < routeCoords.length - 1) {
            const transferIcon = L.divIcon({
              html: '<div class="route-marker transfer">🔄</div>',
              className: 'custom-marker',
              iconSize: [25, 25],
              iconAnchor: [12.5, 12.5]
            });
            
            L.marker(routeCoords[transferIndex], { icon: transferIcon })
              .addTo(routeLayer.current)
              .bindPopup(`<strong>Transfer Point ${i}</strong><br/>Change transport here`);
          }
        }
      }

      // Fit map to show entire route
      leafletMap.current.fitBounds(routeLine.getBounds(), { padding: [20, 20] });
    }
  };

  const generateRouteCoordinates = (route) => {
    // Generate realistic coordinates based on common Mumbai routes
    const mumbaiRoutes = {
      // South to North routes
      'south-north': [
        [18.9220, 72.8347], // Gateway of India
        [18.9398, 72.8355], // CST
        [18.9686, 72.8181], // Mumbai Central
        [19.0178, 72.8478], // Dadar
        [19.0544, 72.8406], // Bandra
        [19.1197, 72.8469], // Andheri
      ],
      // East-West routes
      'east-west': [
        [19.0760, 72.8777], // Mumbai Center
        [19.0760, 72.9000], // Kurla area
        [19.0860, 72.9081], // Ghatkopar
        [19.1160, 72.9350], // Mulund
        [19.1972, 72.9636], // Thane
      ],
      // Default circular route
      'default': [
        [19.0760, 72.8777], // Start
        [19.0500, 72.8900], // Southeast
        [19.0900, 72.9200], // Northeast  
        [19.1200, 72.9000], // North
        [19.1100, 72.8600], // Northwest
        [19.0800, 72.8400], // West
      ]
    };

    // Choose route type based on route characteristics
    let routeType = 'default';
    if (route.duration < 30) {
      routeType = 'south-north';
    } else if (route.transfers > 1) {
      routeType = 'east-west';
    }

    let coords = mumbaiRoutes[routeType];
    
    // Add some randomization and smooth the path
    return coords.map((coord, index) => {
      const randomOffset = 0.005; // Small random offset for variety
      return [
        coord[0] + (Math.random() - 0.5) * randomOffset,
        coord[1] + (Math.random() - 0.5) * randomOffset
      ];
    });
  };

  return (
    <div className="relative w-full h-full">
      {/* Leaflet Map Container */}
      <div ref={mapRef} className="w-full h-full z-0"></div>
      
      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 bg-white bg-opacity-95 rounded-lg p-3 shadow-lg z-10">
        <h4 className="text-sm font-semibold text-gray-800 mb-2">Legend</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center">
            <span className="mr-2">🚀</span>
            <span>Origin</span>
          </div>
          <div className="flex items-center">
            <span className="mr-2">🎯</span>
            <span>Destination</span>
          </div>
          <div className="flex items-center">
            <span className="mr-2">🔄</span>
            <span>Transfer Point</span>
          </div>
          <div className="flex items-center">
            <div className="w-6 h-0.5 bg-blue-500 mr-2" style={{borderStyle: 'dashed'}}></div>
            <span>Route Path</span>
          </div>
        </div>
      </div>

      {/* Route Summary Overlay */}
      {selectedRoute && (
        <div className="absolute top-4 right-4 bg-white bg-opacity-95 rounded-lg p-3 shadow-lg z-10 max-w-xs">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Active Route</h4>
          <div className="space-y-1 text-xs text-gray-600">
            <div>Type: <span className="font-medium text-blue-600">{selectedRoute.route_type}</span></div>
            <div>Duration: <span className="font-medium">{selectedRoute.duration} min</span></div>
            <div>Transfers: <span className="font-medium">{selectedRoute.transfers}</span></div>
            <div>Cost: <span className="font-medium text-green-600">₹{selectedRoute.cost}</span></div>
            <div>Eco Score: <span className="font-medium text-green-600">{selectedRoute.eco_score}/10</span></div>
          </div>
          
          {/* Route Legs Details */}
          {selectedRoute.legs && selectedRoute.legs.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-200">
              <h5 className="text-xs font-medium text-gray-700 mb-1">Route Details</h5>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {selectedRoute.legs.map((leg, index) => (
                  <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {leg.mode === 'WALK' ? '🚶' : 
                         leg.mode === 'BUS' ? '🚌' : 
                         leg.mode === 'RAIL' ? '🚆' : 
                         leg.mode === 'SUBWAY' ? '🚇' : '🚊'} 
                        {leg.route || leg.mode}
                      </span>
                      <span>{leg.duration} min</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {leg.from_name} → {leg.to_name}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Last-mile options */}
          {selectedRoute.last_mile && selectedRoute.last_mile.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-200">
              <h5 className="text-xs font-medium text-gray-700 mb-1">Last-Mile Options</h5>
              <div className="space-y-1">
                {selectedRoute.last_mile.slice(0, 3).map((option, index) => (
                  <button
                    key={index}
                    className="block w-full text-left text-xs bg-blue-50 hover:bg-blue-100 text-blue-800 p-2 rounded transition-colors"
                    onClick={() => {
                      if (option.deep_link) {
                        window.open(option.deep_link, '_blank');
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span>{option.icon} {option.name}</span>
                      <span>₹{option.cost}</span>
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      {option.time} min • ETA: {option.eta}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Custom CSS for map markers and styling */}
      <style>{`
        .landmark-marker {
          background: white;
          border: 2px solid #3b82f6;
          border-radius: 6px;
          padding: 2px 6px;
          font-size: 10px;
          font-weight: 500;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .landmark-marker.station {
          border-color: #10b981;
          background: #ecfdf5;
        }
        
        .landmark-marker.business {
          border-color: #f59e0b;
          background: #fffbeb;
        }
        
        .route-marker {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          background: white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .route-marker.start {
          border: 3px solid #10b981;
        }
        
        .route-marker.end {
          border: 3px solid #ef4444;
        }
        
        .route-marker.transfer {
          border: 2px solid #f59e0b;
        }
        
        .leaflet-popup-content-wrapper {
          border-radius: 8px;
        }
        
        .leaflet-popup-content {
          font-size: 12px;
          line-height: 1.4;
        }
        
        /* Hide default leaflet attribution for cleaner look */
        .leaflet-control-attribution {
          font-size: 10px;
          background: rgba(255,255,255,0.8) !important;
        }
      `}</style>
    </div>
  );
};

export default MapView;