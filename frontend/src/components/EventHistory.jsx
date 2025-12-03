import { useState, useEffect } from 'react'

function EventHistory({ apiUrl, authToken }) {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    event_type: '',
    description: '',
    start_date: '',
    end_date: '',
  })

  useEffect(() => {
    loadEvents()
  }, []) // Solo cargar al montar el componente

  // Función para formatear el tipo de evento de forma más legible
  const formatEventType = (eventType) => {
    const typeMap = {
      'user_login': 'Interacción del Usuario',
      'document_upload': 'Carga de Documento',
      'ai_analysis': 'Análisis con IA',
    }
    return typeMap[eventType] || eventType
  }

  const loadEvents = async () => {
    setLoading(true)
    setError('')

    try {
      const { apiGet } = await import('../utils/api')
      let url = `/documents/events/history?`
      if (filters.event_type) url += `event_type=${filters.event_type}&`
      if (filters.description) url += `description=${filters.description}&`
      if (filters.start_date) url += `start_date=${filters.start_date}&`
      if (filters.end_date) url += `end_date=${filters.end_date}&`

      const response = await apiGet(url)

      const data = await response.json()

      if (response.ok) {
        setEvents(data.events || [])
      } else {
        setError(data.message || 'Error al cargar eventos')
      }
    } catch (err) {
      if (err.message === 'Unauthorized') {
        // El evento 'unauthorized' ya fue disparado por api.js
        return
      }
      setError('Error de conexión: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value })
  }

  const handleExport = async () => {
    try {
      const { apiGet } = await import('../utils/api')
      let url = `/documents/events/export?`
      if (filters.event_type) url += `event_type=${filters.event_type}&`
      if (filters.description) url += `description=${filters.description}&`
      if (filters.start_date) url += `start_date=${filters.start_date}&`
      if (filters.end_date) url += `end_date=${filters.end_date}&`

      const response = await apiGet(url)

      if (response.ok) {
        const blob = await response.blob()
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `eventos_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(downloadUrl)
      } else {
        setError('Error al exportar eventos')
      }
    } catch (err) {
      if (err.message === 'Unauthorized') {
        // El evento 'unauthorized' ya fue disparado por api.js
        return
      }
      setError('Error de conexión: ' + err.message)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent"></div>
        <p className="mt-4 text-sm text-gray-600">Cargando eventos...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-1">Historial de Eventos</h2>
          <p className="text-sm text-gray-600">Registro completo de actividades del sistema</p>
        </div>
        <button
          onClick={handleExport}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors shadow-sm text-sm flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Exportar a Excel
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Filtros de Búsqueda</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Tipo de Evento</label>
            <select
              value={filters.event_type}
              onChange={(e) => handleFilterChange('event_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm bg-white"
            >
              <option value="">Todos los tipos</option>
              <option value="user_login">Interacción del Usuario (Login)</option>
              <option value="document_upload">Carga de Documento</option>
              <option value="ai_analysis">Análisis con IA</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Buscar en Descripción</label>
            <input
              type="text"
              placeholder="Buscar..."
              value={filters.description}
              onChange={(e) => handleFilterChange('description', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm bg-white"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Fecha Inicio</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm bg-white"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Fecha Fin</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm bg-white"
            />
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <button
            onClick={loadEvents}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-md font-medium transition-colors shadow-sm text-sm"
          >
            Aplicar Filtros
          </button>
          <button
            onClick={() => {
              setFilters({ event_type: '', description: '', start_date: '', end_date: '' })
              setTimeout(loadEvents, 100)
            }}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-5 py-2 rounded-md font-medium transition-colors text-sm"
          >
            Limpiar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      {events.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-md border border-gray-200">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-600 font-medium">No hay eventos disponibles</p>
          <p className="text-sm text-gray-500 mt-1">Intenta ajustar los filtros de búsqueda</p>
        </div>
      ) : (
        <>
          <div className="mb-4 text-sm text-gray-600">
            Mostrando {events.length} evento{events.length !== 1 ? 's' : ''}
          </div>
        <div className="overflow-x-auto border border-gray-200 rounded-md">
          <table className="min-w-full bg-white divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Tipo de Evento
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Descripción
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Documento ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Fecha y Hora
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-blue-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {event.id}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-md ${
                      event.event_type === 'user_login'
                        ? 'bg-purple-100 text-purple-700'
                        : event.event_type === 'document_upload'
                        ? 'bg-blue-100 text-blue-700'
                        : event.event_type === 'ai_analysis'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {formatEventType(event.event_type)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {event.description}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {event.document_id || '-'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {new Date(event.created_at).toLocaleString('es-ES')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      )}
    </div>
  )
}

export default EventHistory

