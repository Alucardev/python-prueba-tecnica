import { useState } from 'react'

function DocumentUpload({ apiUrl, authToken }) {
  // authToken se mantiene para compatibilidad pero ya no se usa directamente
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (selectedFile) => {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Tipo de archivo no permitido. Formatos aceptados: PDF, JPG, PNG')
      return
    }
    setFile(selectedFile)
    setError('')
    setResult(null)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Selecciona un archivo')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const { apiPostFormData } = await import('../utils/api')
      const response = await apiPostFormData('/documents/upload', formData)

      const data = await response.json()

      if (response.ok) {
        setResult(data)
        setFile(null)
      } else {
        setError(data.message || 'Error al subir el archivo')
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-1">Subir Documento</h2>
        <p className="text-sm text-gray-600">Selecciona o arrastra un documento para analizar</p>
      </div>

      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('fileInput').click()}
        className={`border-2 border-dashed rounded-md p-12 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <input
          id="fileInput"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
          className="hidden"
        />
        {file ? (
          <div>
            <p className="text-base font-medium text-blue-600">📄 {file.name}</p>
            <p className="text-sm text-gray-500 mt-2">
              Tamaño: {(file.size / 1024).toFixed(2)} KB
            </p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-3 text-gray-400">📎</div>
            <p className="text-base font-medium text-gray-700 mb-1">
              Arrastra un archivo aquí o haz clic para seleccionar
            </p>
            <p className="text-sm text-gray-500">
              Formatos aceptados: PDF, JPG, PNG
            </p>
          </div>
        )}
      </div>

      {/* Upload Button */}
      <div className="text-center">
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {loading ? 'Analizando documento...' : 'Analizar Documento'}
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-sm text-gray-600">Analizando documento con AWS Textract...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Resultados del Análisis</h3>
          <div className="space-y-3">
            <div>
              <span className="font-medium text-gray-700">Clasificación:</span>{' '}
              <span className="text-blue-600 font-semibold">{result.classification}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Estado:</span>{' '}
              <span className="text-gray-600">{result.status}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Archivo:</span>{' '}
              <span className="text-gray-600">{result.filename}</span>
            </div>
            {result.extracted_data && (
              <div className="mt-4">
                <span className="font-medium text-gray-700 block mb-2">Datos Extraídos:</span>
                <pre className="bg-white border border-gray-200 p-4 rounded-md overflow-x-auto text-sm text-gray-800">
                  {JSON.stringify(result.extracted_data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentUpload

