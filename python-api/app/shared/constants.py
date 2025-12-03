"""
Constantes de la aplicación.
Centraliza todos los valores mágicos y strings hardcodeados.
"""

from enum import Enum


class DocumentClassification(str, Enum):
    """Clasificaciones de documentos."""
    FACTURA = "Factura"
    INFORMACION = "Información"
    PROCESSING = "processing"


class DocumentStatus(str, Enum):
    """Estados de documentos."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class FileUploadStatus(str, Enum):
    """Estados de carga de archivos."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    ERROR = "error"


class EventType(str, Enum):
    """Tipos de eventos del sistema."""
    USER_LOGIN = "user_login"
    DOCUMENT_UPLOAD = "document_upload"
    AI_ANALYSIS = "ai_analysis"


class FileType(str, Enum):
    """Tipos de archivos permitidos."""
    PDF = "PDF"
    JPG = "JPG"
    JPEG = "JPEG"
    PNG = "PNG"
    UNKNOWN = "UNKNOWN"


class ValidationSeverity(str, Enum):
    """Severidad de validaciones."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Palabras clave para clasificación de documentos
INVOICE_KEYWORDS = [
    "factura",
    "invoice",
    "total",
    "subtotal",
    "iva",
    "impuesto",
    "cliente",
    "proveedor",
    "supplier",
    "customer",
    "producto",
    "cantidad",
    "precio",
    "número de factura",
    "invoice number",
    "fecha de emisión",
    "fecha de vencimiento",
]

# Palabras para análisis de sentimiento
POSITIVE_WORDS = [
    "bueno",
    "excelente",
    "perfecto",
    "gracias",
    "aprobado",
    "éxito",
    "feliz",
    "satisfecho",
]

NEGATIVE_WORDS = [
    "malo",
    "error",
    "problema",
    "rechazado",
    "fallo",
    "triste",
    "insatisfecho",
    "queja",
]

# Configuración de clasificación
INVOICE_KEYWORD_THRESHOLD = 3  # Mínimo de keywords para clasificar como factura

# Límites de resumen
SUMMARY_MAX_LENGTH = 200

