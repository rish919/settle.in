/**
 * settle — API Client
 *
 * Centralized module for all backend API calls.
 * When the backend URL changes (e.g. production), only this file needs updating.
 */

const API_BASE = 'http://127.0.0.1:8000/api';

/**
 * Fetch all cities, with optional filters.
 *
 * @param {Object} filters
 * @param {string} [filters.search] - Filter by city name.
 * @param {number} [filters.maxRent] - Maximum average rent.
 * @param {number} [filters.minSafety] - Minimum safety score.
 * @returns {Promise<{count: number, cities: Array}>}
 */
export async function fetchCities({ search, maxRent, minSafety } = {}) {
  const params = new URLSearchParams();

  if (search) params.append('search', search);
  if (maxRent) params.append('max_rent', maxRent);
  if (minSafety) params.append('min_safety', minSafety);

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/cities?${queryString}` : `${API_BASE}/cities`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch a single city by ID.
 *
 * @param {string} cityId - Unique city identifier.
 * @returns {Promise<Object>} City data.
 */
export async function fetchCityById(cityId) {
  const response = await fetch(`${API_BASE}/cities/${cityId}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Check backend health.
 *
 * @returns {Promise<Object>} Health status.
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch a single locality by ID.
 *
 * @param {string} cityId - Unique city identifier.
 * @param {string} localityId - Unique locality identifier.
 * @returns {Promise<Object>} Locality data.
 */
export async function fetchLocalityById(cityId, localityId) {
  const response = await fetch(`${API_BASE}/cities/${cityId}/localities/${localityId}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch a comparison between two cities or localities.
 * 
 * @param {string} type - 'city' or 'locality'
 * @param {string} id1 - ID of first location
 * @param {string} id2 - ID of second location
 * @param {string} [cityId1] - City ID for first locality
 * @param {string} [cityId2] - City ID for second locality
 * @returns {Promise<Object>} The comparison data.
 */
export async function fetchComparison(type, id1, id2, cityId1, cityId2) {
  const params = new URLSearchParams();
  params.append('type', type);
  params.append('id1', id1);
  params.append('id2', id2);
  
  if (type === 'locality') {
    if (cityId1) params.append('city_id1', cityId1);
    if (cityId2) params.append('city_id2', cityId2);
  }

  const response = await fetch(`${API_BASE}/compare?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch locality recommendations based on user preferences.
 * 
 * @param {Object} preferences - e.g., {max_rent: 40000, safety_weight: 8, ...}
 * @returns {Promise<Array>} Array of recommended localities.
 */
export async function fetchRecommendations(preferences) {
  const response = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(preferences)
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}
