import React, { useState, useEffect } from 'react';

const UserProfile = ({ onProfileUpdate }) => {
  const [profile, setProfile] = useState({
    name: '',
    preferredMode: 'balanced',
    walkingTolerance: 500,
    maxTransfers: 2,
    timePreference: 'fastest'
  });

  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // Load profiles on component mount
  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/profiles');
      const data = await response.json();
      setProfiles(data.profiles || []);
    } catch (error) {
      console.error('Error loading profiles:', error);
    }
  };

  const handleInputChange = (field, value) => {
    const updatedProfile = { ...profile, [field]: value };
    setProfile(updatedProfile);
    onProfileUpdate(updatedProfile);
  };

  const handleProfileSelect = (profileName) => {
    if (profileName === '') {
      setProfile({
        name: '',
        preferredMode: 'balanced',
        walkingTolerance: 500,
        maxTransfers: 2,
        timePreference: 'fastest'
      });
    } else {
      const selected = profiles.find(p => p.name === profileName);
      if (selected) {
        setProfile(selected);
        onProfileUpdate(selected);
      }
    }
    setSelectedProfile(profileName);
    setIsEditing(false);
  };

  const saveProfile = async () => {
    if (!profile.name.trim()) {
      alert('Please enter a profile name');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/profiles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      });

      if (response.ok) {
        await loadProfiles();
        setSelectedProfile(profile.name);
        setIsEditing(false);
        alert('Profile saved successfully!');
      } else {
        alert('Error saving profile');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile');
    }
  };

  const deleteProfile = async (profileName) => {
    if (!confirm(`Delete profile "${profileName}"?`)) return;

    try {
      const response = await fetch(`http://localhost:5000/api/profiles?name=${encodeURIComponent(profileName)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadProfiles();
        if (selectedProfile === profileName) {
          setSelectedProfile('');
          handleProfileSelect('');
        }
        alert('Profile deleted successfully!');
      } else {
        alert('Error deleting profile');
      }
    } catch (error) {
      console.error('Error deleting profile:', error);
      alert('Error deleting profile');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">👤</span>
        Travel Preferences
      </h2>

      {/* Profile Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Load Saved Profile
        </label>
        <div className="flex gap-2">
          <select
            value={selectedProfile}
            onChange={(e) => handleProfileSelect(e.target.value)}
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">New Profile</option>
            {Array.isArray(profiles) && profiles.map((p) => (
              <option key={p.name} value={p.name}>
                {p.name}
              </option>
            ))}
          </select>
          {selectedProfile && (
            <button
              onClick={() => deleteProfile(selectedProfile)}
              className="px-3 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50"
              title="Delete Profile"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      {/* Profile Name */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Profile Name
        </label>
        <input
          type="text"
          value={profile.name}
          onChange={(e) => handleInputChange('name', e.target.value)}
          placeholder="Enter profile name"
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Preferred Mode */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Travel Mode
        </label>
        <select
          value={profile.preferredMode}
          onChange={(e) => handleInputChange('preferredMode', e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="fastest">🏃 Fastest Route</option>
          <option value="balanced">⚖️ Balanced</option>
          <option value="comfortable">🛋️ Most Comfortable</option>
          <option value="cheapest">💰 Cheapest</option>
        </select>
      </div>

      {/* Walking Tolerance */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Walking Distance: {profile.walkingTolerance}m
        </label>
        <input
          type="range"
          min="100"
          max="2000"
          step="100"
          value={profile.walkingTolerance}
          onChange={(e) => handleInputChange('walkingTolerance', parseInt(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>100m</span>
          <span>2km</span>
        </div>
      </div>

      {/* Max Transfers */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Transfers
        </label>
        <select
          value={profile.maxTransfers}
          onChange={(e) => handleInputChange('maxTransfers', parseInt(e.target.value))}
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value={0}>Direct routes only</option>
          <option value={1}>Up to 1 transfer</option>
          <option value={2}>Up to 2 transfers</option>
          <option value={3}>Up to 3 transfers</option>
        </select>
      </div>

      {/* Time Preference */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Time Preference
        </label>
        <select
          value={profile.timePreference}
          onChange={(e) => handleInputChange('timePreference', e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="fastest">⚡ Fastest arrival</option>
          <option value="earliest">🌅 Earliest departure</option>
          <option value="latest">🌙 Latest departure</option>
        </select>
      </div>

      {/* Save Profile Button */}
      {profile.name.trim() && (
        <button
          onClick={saveProfile}
          className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors"
        >
          💾 Save Profile
        </button>
      )}

      {/* Profile Summary */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Current Preferences:</h3>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Mode: {profile.preferredMode}</div>
          <div>Walking: {profile.walkingTolerance}m max</div>
          <div>Transfers: {profile.maxTransfers} max</div>
          <div>Time: {profile.timePreference}</div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;