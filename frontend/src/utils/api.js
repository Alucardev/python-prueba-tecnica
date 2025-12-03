/**
 * Utilidades para llamadas a la API con manejo de errores 401
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001'

/**
 * Obtiene el token de autenticación del localStorage
 */
export const getAuthToken = () => {
  return localStorage.getItem('authToken')
}

/**
 * Elimina el token de autenticación
 */
export const clearAuthToken = () => {
  localStorage.removeItem('authToken')
}

/**
 * Maneja errores de respuesta, especialmente 401
 */
export const handleApiError = (response, onUnauthorized) => {
  if (response.status === 401) {
    clearAuthToken()
    if (onUnauthorized) {
      onUnauthorized()
    }
    // Disparar evento personalizado para que App.jsx lo capture
    window.dispatchEvent(new CustomEvent('unauthorized'))
    return true
  }
  return false
}

/**
 * Realiza una petición fetch con manejo automático de 401
 */
export const apiFetch = async (url, options = {}, onUnauthorized) => {
  const token = getAuthToken()
  
  const headers = {
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  })
  
  // Manejar error 401
  if (handleApiError(response, onUnauthorized)) {
    throw new Error('Unauthorized')
  }
  
  return response
}

/**
 * Realiza una petición POST con JSON
 */
export const apiPost = async (url, data, onUnauthorized) => {
  return apiFetch(
    url,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    },
    onUnauthorized
  )
}

/**
 * Realiza una petición POST con FormData (para uploads)
 */
export const apiPostFormData = async (url, formData, onUnauthorized) => {
  const token = getAuthToken()
  
  const headers = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_URL}${url}`, {
    method: 'POST',
    headers,
    body: formData,
  })
  
  if (handleApiError(response, onUnauthorized)) {
    throw new Error('Unauthorized')
  }
  
  return response
}

/**
 * Realiza una petición GET
 */
export const apiGet = async (url, onUnauthorized) => {
  return apiFetch(url, { method: 'GET' }, onUnauthorized)
}

export { API_URL }

