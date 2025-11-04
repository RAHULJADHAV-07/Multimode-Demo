import React, { useState } from 'react';
import FeedbackForm from './FeedbackForm';

const RouteDetailModal = ({ isOpen, onClose, route, origin, destination }) => {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [shareSuccess, setShareSuccess] = useState(false);
  if (!isOpen || !route) return null;

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

  const getModeColor = (mode) => {
    const colors = {
      'WALK': 'bg-green-100 text-green-800',
      'BUS': 'bg-orange-100 text-orange-800',
      'RAIL': 'bg-blue-100 text-blue-800',
      'SUBWAY': 'bg-purple-100 text-purple-800',
      'TRAM': 'bg-indigo-100 text-indigo-800',
      'AUTO': 'bg-yellow-100 text-yellow-800'
    };
    return colors[mode] || 'bg-gray-100 text-gray-800';
  };

  const formatTime = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getCurrentTime = () => {
    // If route has real start time, use it; otherwise use current time
    if (route.start_time) {
      const startDate = new Date(route.start_time);
      return startDate.toLocaleTimeString('en-IN', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    }
    
    const now = new Date();
    return now.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const getArrivalTime = () => {
    // If route has real end time, use it
    if (route.end_time) {
      const endDate = new Date(route.end_time);
      return endDate.toLocaleTimeString('en-IN', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    }
    
    // Fallback to calculation
    const departureTime = getCurrentTime();
    const departure = new Date();
    const [time, period] = departureTime.split(' ');
    const [hours, minutes] = time.split(':');
    
    departure.setHours(
      period === 'PM' && hours !== '12' ? parseInt(hours) + 12 : 
      period === 'AM' && hours === '12' ? 0 : parseInt(hours)
    );
    departure.setMinutes(parseInt(minutes));
    
    const arrival = new Date(departure.getTime() + route.duration * 60000);
    return arrival.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const currentTime = getCurrentTime();
  const arrivalTime = getArrivalTime();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-xl">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800 flex items-center">
              <span className="mr-2">🗺️</span>
              Route Details
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
              ×
            </button>
          </div>
          
          {/* Journey Summary */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-600">
                <span className="font-medium">From:</span> {origin || 'Origin'}
              </div>
              <div className="text-sm text-gray-600">
                <span className="font-medium">To:</span> {destination || 'Destination'}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="text-lg font-bold text-blue-800">
                {formatTime(route.duration)}
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-green-600">₹{route.cost}</div>
                <div className="text-sm text-gray-600">{route.route_type} Route</div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Time Information */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Departure</div>
              <div className="text-lg font-bold text-gray-800">{currentTime}</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-sm text-gray-600">Duration</div>
              <div className="text-lg font-bold text-green-600">{formatTime(route.duration)}</div>
            </div>
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-sm text-gray-600">Arrival</div>
              <div className="text-lg font-bold text-blue-600">{arrivalTime}</div>
            </div>
          </div>

          {/* Route Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Transfers</span>
                <span className="text-lg font-bold text-gray-800">{route.transfers}</span>
              </div>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Eco Score</span>
                <span className="text-lg font-bold text-green-600">{route.eco_score}/10</span>
              </div>
            </div>
          </div>

          {/* Train Fare Breakdown */}
          {route.fare_breakdown && route.fare_breakdown.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                <span className="mr-2">🚂</span>
                Train Fare Comparison
              </h4>
              <div className="space-y-3">
                {route.fare_breakdown
                  .filter(fare => fare.mode === 'RAIL')
                  .map((fare, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-blue-100">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-gray-800">
                          🚂 {fare.operator} ({fare.line})
                        </div>
                        <div className="text-sm text-gray-600">
                          {fare.distance_km}km
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        {fare.from} → {fare.to}
                      </div>
                      
                      {/* Fare Options Grid */}
                      <div className="grid grid-cols-3 gap-2">
                        {/* 2nd Class */}
                        <div className={`p-3 rounded-lg border-2 ${
                          fare.default_fare === fare.fares['2nd_class'] 
                            ? 'border-green-500 bg-green-50' 
                            : 'border-gray-200 bg-gray-50'
                        }`}>
                          <div className="text-center">
                            <div className="text-xs text-gray-600 mb-1">2nd Class</div>
                            <div className="text-lg font-bold text-gray-800">₹{fare.fares['2nd_class']}</div>
                            {fare.default_fare === fare.fares['2nd_class'] && (
                              <div className="text-xs text-green-600 mt-1">✓ Used</div>
                            )}
                          </div>
                        </div>
                        
                        {/* 1st Class */}
                        <div className="p-3 rounded-lg border-2 border-gray-200 bg-gray-50 hover:border-blue-300 cursor-pointer">
                          <div className="text-center">
                            <div className="text-xs text-gray-600 mb-1">1st Class</div>
                            <div className="text-lg font-bold text-blue-600">₹{fare.fares['1st_class']}</div>
                            <div className="text-xs text-blue-600 mt-1">Premium</div>
                          </div>
                        </div>
                        
                        {/* AC Local */}
                        <div className="p-3 rounded-lg border-2 border-gray-200 bg-gray-50 hover:border-purple-300 cursor-pointer">
                          <div className="text-center">
                            <div className="text-xs text-gray-600 mb-1">AC Local</div>
                            <div className="text-lg font-bold text-purple-600">₹{fare.fares['ac_local']}</div>
                            <div className="text-xs text-purple-600 mt-1">Luxury</div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Savings Information */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex justify-between text-xs text-gray-600">
                          <span>💰 Save ₹{fare.fares['1st_class'] - fare.fares['2nd_class']} vs 1st Class</span>
                          <span>❄️ AC comfort +₹{fare.fares['ac_local'] - fare.fares['2nd_class']}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                
                {/* Non-Rail Fare Summary */}
                {route.fare_breakdown.filter(fare => fare.mode !== 'RAIL').length > 0 && (
                  <div className="bg-white rounded-lg p-4 border border-blue-100">
                    <div className="font-medium text-gray-800 mb-2">
                      🚌 Other Transport Costs
                    </div>
                    <div className="space-y-2">
                      {route.fare_breakdown
                        .filter(fare => fare.mode !== 'RAIL')
                        .map((fare, index) => (
                          <div key={index} className="flex justify-between items-center text-sm">
                            <span className="text-gray-600">
                              {fare.mode === 'AUTO' ? '🛺' : fare.mode === 'BUS' ? '🚌' : '🚇'} 
                              {fare.operator} ({fare.distance_km}km)
                            </span>
                            <span className="font-medium">
                              ₹{fare.total_fare || fare.fare}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
                
                {/* Total Cost Summary */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-green-800">
                      💰 Total Journey Cost (2nd Class)
                    </span>
                    <span className="text-xl font-bold text-green-600">₹{route.cost}</span>
                  </div>
                  <div className="text-xs text-green-600 mt-1">
                    Optimized for best value - upgrade individual segments as needed
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Additional Time Breakdown (if available) */}
          {(route.walkTime || route.transitTime || route.waitingTime) && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                <span className="mr-2">⏱️</span>
                Time Breakdown
              </h4>
              <div className="grid grid-cols-3 gap-4 text-sm">
                {route.walkTime > 0 && (
                  <div className="text-center">
                    <div className="font-medium text-gray-800">{formatTime(Math.round(route.walkTime))}</div>
                    <div className="text-xs text-gray-600">Walking</div>
                  </div>
                )}
                {route.transitTime > 0 && (
                  <div className="text-center">
                    <div className="font-medium text-gray-800">{formatTime(Math.round(route.transitTime))}</div>
                    <div className="text-xs text-gray-600">Transit</div>
                  </div>
                )}
                {route.waitingTime > 0 && (
                  <div className="text-center">
                    <div className="font-medium text-gray-800">{formatTime(Math.round(route.waitingTime))}</div>
                    <div className="text-xs text-gray-600">Waiting</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step-by-Step Journey */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📋</span>
              Journey Steps
            </h3>
            
            <div className="space-y-3">
              {route.legs && route.legs.map((leg, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  {/* Step Number */}
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </div>
                  
                  {/* Step Details */}
                  <div className="flex-grow">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getModeColor(leg.mode)}`}>
                        {getModeIcon(leg.mode)} {leg.mode}
                      </span>
                      <span className="text-sm font-medium text-gray-800">
                        {formatTime(leg.duration)}
                      </span>
                      {leg.route && (
                        <span className="text-sm text-blue-600 font-medium">
                          {leg.route}
                        </span>
                      )}
                      {/* Show real timing if available */}
                      {leg.departureTime && leg.arrivalTime && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                          {leg.departureTime} → {leg.arrivalTime}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-sm text-gray-600">
                      <div className="flex items-center mb-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        <span>From: {leg.from_name || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center">
                        <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                        <span>To: {leg.to_name || 'Unknown'}</span>
                      </div>
                      {leg.distance && (
                        <div className="mt-1 text-xs text-gray-500">
                          Distance: {leg.distance}m
                        </div>
                      )}
                      {/* Show headsign for transit legs */}
                      {leg.headsign && leg.mode !== 'WALK' && (
                        <div className="mt-1 text-xs text-blue-600">
                          Direction: {leg.headsign}
                        </div>
                      )}
                      {/* Show agency for transit legs */}
                      {leg.agency && leg.mode !== 'WALK' && (
                        <div className="mt-1 text-xs text-purple-600">
                          Operator: {leg.agency}
                        </div>
                      )}
                    </div>

                    {/* Walking Instructions */}
                    {leg.mode === 'WALK' && (
                      <div className="mt-2 p-2 bg-green-50 rounded text-xs text-green-700">
                        🚶 Walk {leg.distance ? `${leg.distance}m` : ''} to reach your next transport
                      </div>
                    )}

                    {/* Transit Instructions */}
                    {leg.mode !== 'WALK' && (
                      <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-700">
                        {leg.mode === 'BUS' && '🚌 Board the bus at the designated stop'}
                        {leg.mode === 'RAIL' && '🚂 Take the train from platform'}
                        {leg.mode === 'SUBWAY' && '🚇 Enter metro station and follow signs'}
                        {leg.mode === 'TRAM' && '🚋 Wait for tram at the stop'}
                        {leg.mode === 'AUTO' && '🛺 Hail an auto-rickshaw or book via app'}
                        {leg.route && (
                          <div className="mt-1">
                            Route: <span className="font-medium">{leg.route}</span>
                            {leg.headsign && ` towards ${leg.headsign}`}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Last Mile Options */}
          {route.last_mile && route.last_mile.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="mr-2">🛴</span>
                Last-Mile Options
              </h3>
              
              <div className="grid gap-3">
                {route.last_mile.map((option, index) => (
                  <div
                    key={index}
                    className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors"
                    onClick={() => option.deep_link && window.open(option.deep_link, '_blank')}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{option.icon}</span>
                        <div>
                          <div className="font-medium text-gray-800">{option.name}</div>
                          <div className="text-sm text-gray-600">
                            {option.time} min • ETA: {option.eta}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-600">₹{option.cost}</div>
                        {option.deep_link && (
                          <div className="text-xs text-blue-600">Tap to book</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tips and Warnings */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-medium text-yellow-800 mb-2 flex items-center">
              <span className="mr-2">💡</span>
              Travel Tips
            </h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Keep your ticket/pass ready for inspection</li>
              <li>• Allow extra time during peak hours</li>
              {route.transfers > 0 && (
                <li>• Plan your transfers carefully and follow station signs</li>
              )}
              <li>• Check for service updates before traveling</li>
              {route.legs && route.legs.some(leg => leg.mode === 'WALK') && (
                <li>• Wear comfortable shoes for walking segments</li>
              )}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
            <button
              onClick={async () => {
                try {
                  const currentTime = getCurrentTime();
                  const arrivalTime = getArrivalTime();
                  
                  // Create comprehensive route details message with all information
                  let routeDetails = `🌱 Yatri Eco Route Plan

📍 From: ${origin}
📍 To: ${destination}

🕐 Departure: ${currentTime}
⏱️ Duration: ${formatTime(route.duration)}
� Arrival: ${arrivalTime}
🔄 Transfers: ${route.transfers}
🌱 Eco Score: ${route.eco_score || 'N/A'}/10`;

                  // Add fare breakdown if available
                  if (route.fare_breakdown && route.fare_breakdown.length > 0) {
                    routeDetails += '\n\n🚂 Train Fare Breakdown:';
                    route.fare_breakdown
                      .filter(fare => fare.mode === 'RAIL')
                      .forEach((fare, index) => {
                        routeDetails += `\n🚂 ${fare.operator} (${fare.line}) - ${fare.distance_km}km`;
                        routeDetails += `\n${fare.from} → ${fare.to}`;
                        routeDetails += `\n• 2nd Class: ₹${fare.fares['2nd_class']} ✓ Used`;
                        routeDetails += `\n• 1st Class: ₹${fare.fares['1st_class']} (Premium)`;
                        routeDetails += `\n• AC Local: ₹${fare.fares['ac_local']} (Luxury)`;
                        if (index < route.fare_breakdown.filter(f => f.mode === 'RAIL').length - 1) {
                          routeDetails += '\n';
                        }
                      });
                    
                    routeDetails += `\n\n� Total Journey Cost: ₹${route.cost}`;
                    routeDetails += '\nOptimized for best value - upgrade individual segments as needed';
                  } else {
                    routeDetails += `\n\n💰 Cost: ₹${route.cost}`;
                  }

                  // Add time breakdown if available
                  if (route.walkTime || route.transitTime || route.waitingTime) {
                    routeDetails += '\n\n⏱️ Time Breakdown:';
                    if (route.walkTime > 0) routeDetails += `\n🚶 Walking: ${formatTime(Math.round(route.walkTime))}`;
                    if (route.transitTime > 0) routeDetails += `\n🚌 Transit: ${formatTime(Math.round(route.transitTime))}`;
                    if (route.waitingTime > 0) routeDetails += `\n⏳ Waiting: ${formatTime(Math.round(route.waitingTime))}`;
                  }

                  // Add detailed journey steps
                  if (route.legs && route.legs.length > 0) {
                    routeDetails += '\n\n� Journey Steps:';
                    route.legs.forEach((leg, index) => {
                      const stepIcon = getModeIcon(leg.mode);
                      const stepNumber = index + 1;
                      
                      routeDetails += `\n\n${stepNumber}. ${stepIcon} ${leg.mode} - ${formatTime(leg.duration)}`;
                      
                      // Add timing if available
                      if (leg.departureTime && leg.arrivalTime) {
                        routeDetails += `\n🕐 ${leg.departureTime} → ${leg.arrivalTime}`;
                      }
                      
                      // Add route info
                      if (leg.route) {
                        routeDetails += `\n🚌 Route: ${leg.route}`;
                      }
                      
                      // Add from/to info
                      routeDetails += `\n📍 From: ${leg.from_name || 'Unknown'}`;
                      routeDetails += `\n📍 To: ${leg.to_name || 'Unknown'}`;
                      
                      // Add distance for walking
                      if (leg.mode === 'WALK' && leg.distance) {
                        routeDetails += `\n📏 Distance: ${Math.round(leg.distance)}m`;
                      }
                      
                      // Add direction for transit
                      if (leg.headsign && leg.mode !== 'WALK') {
                        routeDetails += `\n🧭 Direction: ${leg.headsign}`;
                      }
                      
                      // Add operator for transit
                      if (leg.agency && leg.mode !== 'WALK') {
                        routeDetails += `\n🏢 Operator: ${leg.agency}`;
                      }
                    });
                  }

                  // Add travel tips
                  routeDetails += '\n\n💡 Travel Tips:';
                  routeDetails += '\n• Keep your ticket/pass ready for inspection';
                  routeDetails += '\n• Allow extra time during peak hours';
                  if (route.transfers > 0) {
                    routeDetails += '\n• Plan your transfers carefully and follow station signs';
                  }
                  routeDetails += '\n• Check for service updates before traveling';
                  if (route.legs && route.legs.some(leg => leg.mode === 'WALK')) {
                    routeDetails += '\n• Wear comfortable shoes for walking segments';
                  }

                  routeDetails += '\n\n🌿 Generated by Yatri - Smart Journey Planner';
                  routeDetails += `\nGet your eco-friendly routes at: ${window.location.origin}`;
                  
                  await navigator.clipboard.writeText(routeDetails);
                  setCopySuccess(true);
                  setTimeout(() => setCopySuccess(false), 2000);
                } catch (error) {
                  console.error('Failed to copy route details:', error);
                  // Fallback for browsers that don't support clipboard API
                  try {
                    const basicRoute = `Yatri Route: ${origin} → ${destination}\nDeparture: ${getCurrentTime()}\nArrival: ${getArrivalTime()}\nDuration: ${formatTime(route.duration)}\nCost: ₹${route.cost}\nTransfers: ${route.transfers}`;
                    const textArea = document.createElement('textarea');
                    textArea.value = basicRoute;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    setCopySuccess(true);
                    setTimeout(() => setCopySuccess(false), 2000);
                  } catch (fallbackError) {
                    alert(`❌ Unable to copy automatically. Here's your route:\n\n${origin} → ${destination}\nDeparture: ${getCurrentTime()}\nArrival: ${getArrivalTime()}\nDuration: ${formatTime(route.duration)}\nCost: ₹${route.cost}\nTransfers: ${route.transfers}`);
                  }
                }
              }}
              className={`flex-1 ${copySuccess ? 'bg-green-500' : 'bg-blue-500 hover:bg-blue-600'} text-white py-2 sm:py-3 px-3 sm:px-4 rounded-lg font-medium transition-all duration-200 text-sm sm:text-base`}
            >
              {copySuccess ? '✅ Copied!' : '📋 Copy Route Details'}
            </button>
            
            <button
              onClick={async () => {
                try {
                  const currentTime = getCurrentTime();
                  const arrivalTime = getArrivalTime();
                  
                  // Create comprehensive route sharing message with all details
                  let routeDetails = `🌱 *Yatri Eco Route Plan*

📍 *From:* ${origin}
📍 *To:* ${destination}

🕐 *Departure:* ${currentTime}
⏱️ *Duration:* ${formatTime(route.duration)}
� *Arrival:* ${arrivalTime}
🔄 *Transfers:* ${route.transfers}
🌱 *Eco Score:* ${route.eco_score || 'N/A'}/10`;

                  // Add fare breakdown if available
                  if (route.fare_breakdown && route.fare_breakdown.length > 0) {
                    routeDetails += '\n\n🚂 *Train Fare Breakdown:*';
                    route.fare_breakdown
                      .filter(fare => fare.mode === 'RAIL')
                      .forEach((fare, index) => {
                        routeDetails += `\n🚂 ${fare.operator} (${fare.line}) - ${fare.distance_km}km`;
                        routeDetails += `\n${fare.from} → ${fare.to}`;
                        routeDetails += `\n• 2nd Class: ₹${fare.fares['2nd_class']} ✓ Used`;
                        routeDetails += `\n• 1st Class: ₹${fare.fares['1st_class']} (Premium)`;
                        routeDetails += `\n• AC Local: ₹${fare.fares['ac_local']} (Luxury)`;
                        if (index < route.fare_breakdown.filter(f => f.mode === 'RAIL').length - 1) {
                          routeDetails += '\n';
                        }
                      });
                    
                    routeDetails += `\n\n� *Total Journey Cost:* ₹${route.cost}`;
                    routeDetails += '\n_Optimized for best value - upgrade individual segments as needed_';
                  } else {
                    routeDetails += `\n\n💰 *Cost:* ₹${route.cost}`;
                  }

                  // Add time breakdown if available
                  if (route.walkTime || route.transitTime || route.waitingTime) {
                    routeDetails += '\n\n⏱️ *Time Breakdown:*';
                    if (route.walkTime > 0) routeDetails += `\n🚶 Walking: ${formatTime(Math.round(route.walkTime))}`;
                    if (route.transitTime > 0) routeDetails += `\n🚌 Transit: ${formatTime(Math.round(route.transitTime))}`;
                    if (route.waitingTime > 0) routeDetails += `\n⏳ Waiting: ${formatTime(Math.round(route.waitingTime))}`;
                  }

                  // Add detailed journey steps
                  if (route.legs && route.legs.length > 0) {
                    routeDetails += '\n\n📋 *Journey Steps:*';
                    route.legs.forEach((leg, index) => {
                      const stepIcon = getModeIcon(leg.mode);
                      const stepNumber = index + 1;
                      
                      routeDetails += `\n\n*${stepNumber}.* ${stepIcon} *${leg.mode}* - ${formatTime(leg.duration)}`;
                      
                      // Add timing if available
                      if (leg.departureTime && leg.arrivalTime) {
                        routeDetails += `\n🕐 ${leg.departureTime} → ${leg.arrivalTime}`;
                      }
                      
                      // Add route info
                      if (leg.route) {
                        routeDetails += `\n🚌 Route: ${leg.route}`;
                      }
                      
                      // Add from/to info
                      routeDetails += `\n📍 From: ${leg.from_name || 'Unknown'}`;
                      routeDetails += `\n📍 To: ${leg.to_name || 'Unknown'}`;
                      
                      // Add distance for walking
                      if (leg.mode === 'WALK' && leg.distance) {
                        routeDetails += `\n📏 Distance: ${Math.round(leg.distance)}m`;
                      }
                      
                      // Add direction for transit
                      if (leg.headsign && leg.mode !== 'WALK') {
                        routeDetails += `\n🧭 Direction: ${leg.headsign}`;
                      }
                      
                      // Add operator for transit
                      if (leg.agency && leg.mode !== 'WALK') {
                        routeDetails += `\n🏢 Operator: ${leg.agency}`;
                      }
                    });
                  }

                  // Add travel tips
                  routeDetails += '\n\n💡 *Travel Tips:*';
                  routeDetails += '\n• Keep your ticket/pass ready for inspection';
                  routeDetails += '\n• Allow extra time during peak hours';
                  if (route.transfers > 0) {
                    routeDetails += '\n• Plan your transfers carefully and follow station signs';
                  }
                  routeDetails += '\n• Check for service updates before traveling';
                  if (route.legs && route.legs.some(leg => leg.mode === 'WALK')) {
                    routeDetails += '\n• Wear comfortable shoes for walking segments';
                  }

                  routeDetails += '\n\n🌿 *Shared via Yatri - Smart Journey Planner*';
                  routeDetails += `\nGet your eco-friendly routes at: ${window.location.origin}`;

                  const shareData = {
                    title: '🌱 Yatri Eco Route Plan',
                    text: routeDetails
                  };

                  // Try native sharing first
                  if (navigator.share) {
                    await navigator.share(shareData);
                    setShareSuccess(true);
                    setTimeout(() => setShareSuccess(false), 2000);
                  } else {
                    // Fallback: Copy to clipboard and show instructions
                    await navigator.clipboard.writeText(routeDetails);
                    
                    // Show a more helpful message
                    alert(`📋 Complete route details copied to clipboard!\n\nYou can now paste this in:\n• WhatsApp\n• Telegram\n• Email\n• Any messaging app\n\nIncludes: Journey steps, fare breakdown, timings, and travel tips! 🚀`);
                    
                    setShareSuccess(true);
                    setTimeout(() => setShareSuccess(false), 3000);
                  }
                } catch (error) {
                  console.error('Failed to share route:', error);
                  
                  // Final fallback: Copy basic route info
                  try {
                    const basicRoute = `🌱 Yatri Route: ${origin} → ${destination}\n🕐 ${getCurrentTime()} → ${getArrivalTime()}\n⏱️ ${formatTime(route.duration)} | 💰 ₹${route.cost} | 🔄 ${route.transfers} transfers\n\nGet eco-friendly routes at: ${window.location.origin}`;
                    await navigator.clipboard.writeText(basicRoute);
                    alert('📋 Basic route info copied to clipboard! You can paste it in any app to share.');
                  } catch (clipboardError) {
                    alert(`❌ Unable to share automatically. Here's your route:\n\n${origin} → ${destination}\nDeparture: ${getCurrentTime()}\nArrival: ${getArrivalTime()}\nDuration: ${formatTime(route.duration)}\nCost: ₹${route.cost}\nTransfers: ${route.transfers}\n\nYou can copy this manually to share!`);
                  }
                }
              }}
              className={`flex-1 ${shareSuccess ? 'bg-green-500' : 'bg-green-500 hover:bg-green-600'} text-white py-2 sm:py-3 px-3 sm:px-4 rounded-lg font-medium transition-all duration-200 text-sm sm:text-base`}
            >
              {shareSuccess ? '✅ Shared!' : '📤 Share Route'}
            </button>

            <button
              onClick={() => setFeedbackOpen(true)}
              className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 sm:py-3 px-3 sm:px-4 rounded-lg font-medium transition-colors text-sm sm:text-base"
            >
              💬 Feedback
            </button>
          </div>
        </div>
      </div>

      {/* Feedback Form Modal */}
      {feedbackOpen && (
        <FeedbackForm
          route={{
            from: origin,
            to: destination,
            duration: route.duration ? `${route.duration} minutes` : 'Unknown',
            cost: route.cost || 0,
            route_type: route.route_type || 'Unknown'
          }}
          onClose={() => setFeedbackOpen(false)}
        />
      )}
    </div>
  );
};

export default RouteDetailModal;