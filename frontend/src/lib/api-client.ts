// Demo Mode: Simplified API client without authentication
let API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

// Validate and fix API_URL
if (!API_URL || 
    API_URL.trim() === '' || 
    API_URL.includes(':8000') || 
    (!API_URL.startsWith('http://') && !API_URL.startsWith('https://'))) {
  API_URL = 'http://localhost:8002'
}

// Ensure API_URL doesn't end with a slash
API_URL = API_URL.trim().replace(/\/+$/, '')

const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').trim()

/**
 * A simplified API client for Demo Mode.
 * @param endpoint The API endpoint to call, e.g., '/api/test' or '/api/admin/dashboard'.
 *                 The endpoint should include the '/api' prefix.
 * @param options Standard fetch options (method, body, etc.).
 */
async function apiClient(endpoint: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers || {})

  // Demo Mode: No authentication token needed

  // Construct the full URL: http://localhost:8002/app1/api/test
  const fullUrl = `${API_URL}${BASE_PATH}${endpoint}`

  const response = await fetch(fullUrl, { ...options, headers })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: response.statusText,
    }))
    throw new Error(errorData.detail || 'An API error occurred.')
  }

  // Handle responses with no content
  if (response.status === 204) {
    return null
  }

  return response.json()
}

export default apiClient
