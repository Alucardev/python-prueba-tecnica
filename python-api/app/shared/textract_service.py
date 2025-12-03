"""
Servicio para análisis de documentos con AWS Textract.
"""
import json
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

from app.config import settings
from app.exceptions.custom_exceptions import ExternalServiceError


class TextractService:
    """Servicio para análisis de documentos con AWS Textract."""

    def __init__(self):
        """Inicializa el cliente de Textract."""
        self.client = boto3.client(
            "textract",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def analyze_document(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """
        Analiza un documento usando AWS Textract.

        Args:
            s3_bucket: Nombre del bucket de S3
            s3_key: Clave del archivo en S3

        Returns:
            Resultado del análisis de Textract

        Raises:
            ExternalServiceError: Si hay error al analizar el documento
        """
        try:
            response = self.client.analyze_document(
                Document={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}},
                FeatureTypes=["FORMS", "TABLES"],
            )
            return response
        except ClientError as e:
            raise ExternalServiceError(
                f"Error al analizar documento con Textract: {str(e)}", service="AWS Textract"
            )

    def detect_document_text(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """
        Detecta texto en un documento usando AWS Textract.

        Args:
            s3_bucket: Nombre del bucket de S3
            s3_key: Clave del archivo en S3

        Returns:
            Resultado de detección de texto

        Raises:
            ExternalServiceError: Si hay error al detectar texto
        """
        try:
            response = self.client.detect_document_text(
                Document={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}}
            )
            return response
        except ClientError as e:
            raise ExternalServiceError(
                f"Error al detectar texto con Textract: {str(e)}", service="AWS Textract"
            )

    def classify_document(self, text_content: str) -> str:
        """
        Clasifica un documento basándose en su contenido de texto.

        Args:
            text_content: Contenido de texto extraído del documento

        Returns:
            Clasificación: "Factura" o "Información"
        """
        text_lower = text_content.lower()

        # Palabras clave que indican que es una factura
        invoice_keywords = [
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

        # Contar coincidencias
        matches = sum(1 for keyword in invoice_keywords if keyword in text_lower)

        # Si hay al menos 3 coincidencias, es probable que sea una factura
        if matches >= 3:
            return "Factura"
        return "Información"

    def extract_invoice_data(self, textract_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae datos de una factura del resultado de Textract.

        Args:
            textract_response: Respuesta de Textract

        Returns:
            Diccionario con datos extraídos de la factura
        """
        blocks = textract_response.get("Blocks", [])
        text = self._extract_text_from_blocks(blocks)
        key_value_pairs = self._extract_key_value_pairs(blocks)

        # Extraer información de la factura
        invoice_data = {
            "cliente": {
                "nombre": self._find_value(key_value_pairs, ["cliente", "customer", "nombre cliente"]),
                "direccion": self._find_value(key_value_pairs, ["dirección cliente", "customer address", "direccion"]),
            },
            "proveedor": {
                "nombre": self._find_value(key_value_pairs, ["proveedor", "supplier", "empresa", "company"]),
                "direccion": self._find_value(key_value_pairs, ["dirección proveedor", "supplier address"]),
            },
            "numero_factura": self._find_value(key_value_pairs, ["número", "numero", "nº", "n°", "invoice number", "factura"]),
            "fecha": self._find_value(key_value_pairs, ["fecha", "date", "fecha de emisión"]),
            "productos": self._extract_products(blocks, text),
            "total": self._find_value(key_value_pairs, ["total", "total a pagar", "amount due"]),
        }

        return invoice_data

    def extract_information_data(self, text_content: str) -> Dict[str, Any]:
        """
        Extrae datos de un documento de información usando OpenAI o análisis simple.

        Args:
            text_content: Contenido de texto del documento

        Returns:
            Diccionario con datos extraídos
        """
        # Análisis simple de sentimiento
        sentiment = self._analyze_sentiment(text_content)

        # Generar resumen (primeros 200 caracteres)
        summary = text_content[:200] + "..." if len(text_content) > 200 else text_content

        return {
            "descripcion": summary,
            "resumen": summary,
            "sentimiento": sentiment,
            "longitud_texto": len(text_content),
        }

    def _extract_text_from_blocks(self, blocks: list) -> str:
        """Extrae texto de los bloques de Textract."""
        text_blocks = [block.get("Text", "") for block in blocks if block.get("BlockType") == "LINE"]
        return " ".join(text_blocks)

    def _extract_key_value_pairs(self, blocks: list) -> Dict[str, str]:
        """Extrae pares clave-valor de los bloques de Textract."""
        key_value_pairs = {}
        key_blocks = {}
        value_blocks = {}

        # Primero, identificar todos los bloques KEY y VALUE
        for block in blocks:
            block_type = block.get("BlockType")
            block_id = block.get("Id")

            if block_type == "KEY_VALUE_SET":
                entity_types = block.get("EntityTypes", [])
                if "KEY" in entity_types:
                    # Buscar el texto de la clave en los bloques relacionados
                    if "Relationships" in block:
                        for relationship in block["Relationships"]:
                            if relationship["Type"] == "CHILD":
                                for child_id in relationship["Ids"]:
                                    child_text = self._get_text_from_block(blocks, child_id)
                                    if child_text:
                                        key_blocks[block_id] = child_text
                elif "VALUE" in entity_types:
                    # Buscar el texto del valor
                    if "Relationships" in block:
                        for relationship in block["Relationships"]:
                            if relationship["Type"] == "CHILD":
                                for child_id in relationship["Ids"]:
                                    child_text = self._get_text_from_block(blocks, child_id)
                                    if child_text:
                                        value_blocks[block_id] = child_text
                    elif "Text" in block:
                        value_blocks[block_id] = block.get("Text", "")

        # Mapear claves a valores usando las relaciones
        for block in blocks:
            if block.get("BlockType") == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
                key_id = block.get("Id")
                key_text = key_blocks.get(key_id, "")
                
                if "Relationships" in block:
                    for relationship in block["Relationships"]:
                        if relationship["Type"] == "VALUE":
                            for value_id in relationship["Ids"]:
                                value_text = value_blocks.get(value_id, "")
                                if key_text and value_text:
                                    key_value_pairs[key_text.lower()] = value_text

        return key_value_pairs

    def _get_text_from_block(self, blocks: list, block_id: str) -> Optional[str]:
        """Obtiene el texto de un bloque por su ID."""
        for block in blocks:
            if block.get("Id") == block_id:
                return block.get("Text", "")
        return None

    def _find_value(self, key_value_pairs: Dict[str, str], keywords: list) -> Optional[str]:
        """Busca un valor en los pares clave-valor usando palabras clave."""
        for keyword in keywords:
            for key, value in key_value_pairs.items():
                if keyword.lower() in key.lower():
                    return value
        return None

    def _extract_products(self, blocks: list, text: str) -> list:
        """Extrae productos de la factura."""
        products = []
        # Buscar tablas que puedan contener productos
        tables = [block for block in blocks if block.get("BlockType") == "TABLE"]

        for table in tables[:1]:  # Solo la primera tabla
            # Simplificado: buscar líneas que contengan números y palabras
            # En producción, se debería parsear mejor la estructura de la tabla
            pass

        return products

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analiza el sentimiento del texto (simple, sin OpenAI).

        Args:
            text: Texto a analizar

        Returns:
            Sentimiento: "positivo", "negativo" o "neutral"
        """
        text_lower = text.lower()

        # Palabras positivas
        positive_words = [
            "bueno",
            "excelente",
            "perfecto",
            "gracias",
            "aprobado",
            "éxito",
            "feliz",
            "satisfecho",
        ]

        # Palabras negativas
        negative_words = [
            "malo",
            "error",
            "problema",
            "rechazado",
            "fallo",
            "triste",
            "insatisfecho",
            "queja",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positivo"
        elif negative_count > positive_count:
            return "negativo"
        return "neutral"


__all__ = ["TextractService"]

