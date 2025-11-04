import React, { useState } from 'react';
import { useForm, ValidationError } from '@formspree/react';

const FeedbackForm = ({ route, onClose }) => {
  const [state, handleSubmit] = useForm("xvgwppvl");
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [selectedIssue, setSelectedIssue] = useState('');
  const [customFeedback, setCustomFeedback] = useState('');

  const issueTypes = [
    { value: '', label: 'Select issue type' },
    { value: 'route_incorrect', label: '❌ Route not correct', description: 'The suggested route is wrong' },
    { value: 'suggest_better', label: '💡 Suggest better route', description: 'I know a faster/cheaper way' },
    { value: 'missing_transport', label: '🚌 Missing transport option', description: 'Missing bus/train/metro option' },
    { value: 'timing_wrong', label: '⏰ Timing issues', description: 'Departure/arrival times are incorrect' },
    { value: 'cost_wrong', label: '💰 Cost information wrong', description: 'Fare prices are not accurate' },
    { value: 'accessibility', label: '♿ Accessibility concerns', description: 'Route not accessible for disabled persons' },
    { value: 'safety', label: '🛡️ Safety concerns', description: 'Route passes through unsafe areas' },
    { value: 'other', label: '📝 Other feedback', description: 'General suggestions or comments' }
  ];

  const handleRatingClick = (value) => {
    setRating(value);
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    
    // Prepare form data with all feedback information
    const formData = new FormData();
    formData.append('email', e.target.email?.value || '');
    formData.append('rating', rating);
    formData.append('issue_type', selectedIssue);
    formData.append('feedback', customFeedback);
    formData.append('route_from', route?.from || '');
    formData.append('route_to', route?.to || '');
    formData.append('route_duration', route?.duration || '');
    formData.append('route_cost', route?.cost || '');
    formData.append('route_type', route?.route_type || '');
    
    // Submit to Formspree
    await handleSubmit(formData);
  };

  if (state.succeeded) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="mb-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Thank You!</h3>
            <p className="text-gray-600">Your feedback has been submitted successfully. We appreciate your help in improving our service!</p>
          </div>
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.418 8-9 8a9.013 9.013 0 01-5.314-1.676l-2.686.67.67-2.686A9.013 9.013 0 013 12c0-4.418 4.418-8 9-8s8 3.582 8 8z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Route Feedback</h2>
              <p className="text-sm text-gray-500">Help us improve your journey experience</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Route Summary */}
        {route && (
          <div className="p-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Route Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-500">From:</span>
                <p className="font-medium text-gray-900">{route.from || 'Unknown'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">To:</span>
                <p className="font-medium text-gray-900">{route.to || 'Unknown'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Duration:</span>
                <p className="font-medium text-green-600">{route.duration || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Cost:</span>
                <p className="font-medium text-blue-600">₹{route.cost || '0'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Feedback Form */}
        <form onSubmit={handleFormSubmit} className="p-6 space-y-6">
          {/* Star Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              ⭐ Rate this route (1-5 stars)
            </label>
            <div className="flex items-center space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => handleRatingClick(star)}
                  onMouseEnter={() => setHoveredRating(star)}
                  onMouseLeave={() => setHoveredRating(0)}
                  className="p-1 transition-transform hover:scale-110 focus:outline-none"
                >
                  <svg
                    className={`w-8 h-8 transition-colors ${
                      star <= (hoveredRating || rating)
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300'
                    }`}
                    fill={star <= (hoveredRating || rating) ? 'currentColor' : 'none'}
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                    />
                  </svg>
                </button>
              ))}
              <span className="ml-3 text-sm text-gray-500">
                {rating === 0 && 'Click to rate'}
                {rating === 1 && '😞 Poor'}
                {rating === 2 && '😐 Fair'}
                {rating === 3 && '🙂 Good'}
                {rating === 4 && '😊 Very Good'}
                {rating === 5 && '🤩 Excellent'}
              </span>
            </div>
          </div>

          {/* Issue Type Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              📋 What kind of feedback do you have?
            </label>
            <select
              value={selectedIssue}
              onChange={(e) => setSelectedIssue(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              {issueTypes.map((issue) => (
                <option key={issue.value} value={issue.value}>
                  {issue.label}
                </option>
              ))}
            </select>
            {selectedIssue && issueTypes.find(issue => issue.value === selectedIssue)?.description && (
              <p className="mt-2 text-sm text-gray-500 italic">
                {issueTypes.find(issue => issue.value === selectedIssue)?.description}
              </p>
            )}
          </div>

          {/* Custom Feedback */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              💭 Your detailed feedback
            </label>
            <textarea
              id="message"
              name="message"
              rows={4}
              value={customFeedback}
              onChange={(e) => setCustomFeedback(e.target.value)}
              placeholder="Tell us what's wrong or how we can improve this route..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
            />
            <ValidationError prefix="Message" field="message" errors={state.errors} />
          </div>

          {/* Email (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              📧 Email (optional - for follow-up)
            </label>
            <input
              id="email"
              type="email"
              name="email"
              placeholder="your.email@example.com (for follow-up)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            <ValidationError prefix="Email" field="email" errors={state.errors} />
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={state.submitting || rating === 0}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {state.submitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Submitting...
                </span>
              ) : (
                'Submit Feedback'
              )}
            </button>
          </div>

          {/* Error Display */}
          {state.errors && state.errors.length > 0 && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="text-red-800 font-medium mb-2">Please fix the following errors:</h4>
              <ul className="text-red-700 text-sm space-y-1">
                {state.errors.map((error, index) => (
                  <li key={index}>• {error.message}</li>
                ))}
              </ul>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;