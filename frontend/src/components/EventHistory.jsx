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
  }, [])

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
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-1">Historial de Eventos</h2>
          <p className="text-sm text-gray-600">Registro de actividades del sistema</p>
        </div>
        <button
          onClick={handleExport}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors shadow-sm text-sm"
        >
          Exportar a Excel
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        <input
          type="text"
          placeholder="Tipo de evento"
          value={filters.event_type}
          onChange={(e) => handleFilterChange('event_type', e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
        />
        <input
          type="text"
          placeholder="Buscar en descripción"
          value={filters.description}
          onChange={(e) => handleFilterChange('description', e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
        />
        <input
          type="date"
          placeholder="Fecha inicio"
          value={filters.start_date}
          onChange={(e) => handleFilterChange('start_date', e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
        />
        <input
          type="date"
          placeholder="Fecha fin"
          value={filters.end_date}
          onChange={(e) => handleFilterChange('end_date', e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
        />
      </div>

      <button
        onClick={loadEvents}
        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-md font-medium transition-colors shadow-sm text-sm"
      >
        Filtrar
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      {events.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-md border border-gray-200">
          <p className="text-gray-600">No hay eventos disponibles</p>
        </div>
      ) : (
        <div className="overflow-x-auto border border-gray-200 rounded-md">
          <table className="min-w-full bg-white divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Descripción
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Documento ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Fecha
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
                    <span className="px-2.5 py-1 text-xs font-medium rounded-md bg-blue-100 text-blue-700">
                      {event.event_type}
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
      )}
    </div>
  )
}

export default EventHistory

