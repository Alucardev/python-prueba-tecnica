import { useState, useEffect } from 'react'
import DocumentUpload from './components/DocumentUpload'
import EventHistory from './components/EventHistory'
import Login from './components/Login'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001'

function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'))
  const [currentUser, setCurrentUser] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    if (authToken) {
      // Verificar si el token es válido
      // En producción, hacer una llamada a la API para validar
    }
  }, [authToken])

  // Escuchar eventos de 401 (no autorizado)
  useEffect(() => {
    const handleUnauthorized = () => {
      setAuthToken(null)
      setCurrentUser(null)
    }

    window.addEventListener('unauthorized', handleUnauthorized)
    
    return () => {
      window.removeEventListener('unauthorized', handleUnauthorized)
    }
  }, [])

  const handleLogin = (token) => {
    setAuthToken(token)
    localStorage.setItem('authToken', token)
  }

  const handleLogout = () => {
    setAuthToken(null)
    setCurrentUser(null)
    localStorage.removeItem('authToken')
  }

  if (!authToken) {
    return <Login onLogin={handleLogin} apiUrl={API_URL} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg mb-6 rounded-lg px-6 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-white mb-1">Análisis de Documentos con IA</h1>
              <p className="text-sm text-blue-100">Sube documentos PDF, JPG o PNG para análisis automático con AWS Textract</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-white hover:bg-gray-50 text-blue-600 rounded-md transition-colors text-sm font-medium shadow-sm"
            >
              Cerrar Sesión
            </button>
          </div>
        </header>

        {/* Tabs Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-6 py-3 font-medium text-sm transition-colors ${
                activeTab === 'upload'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
              }`}
            >
              Subir Documento
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-3 font-medium text-sm transition-colors ${
                activeTab === 'history'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
              }`}
            >
              Historial de Eventos
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'upload' && (
              <DocumentUpload apiUrl={API_URL} authToken={authToken} />
            )}
            {activeTab === 'history' && (
              <EventHistory apiUrl={API_URL} authToken={authToken} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
