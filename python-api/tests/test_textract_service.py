"""
Tests para el servicio de AWS Textract.
"""
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from app.shared.textract_service import TextractService
from app.exceptions.custom_exceptions import ExternalServiceError


class TestTextractService:
    """Tests para el servicio de Textract."""
    
    def test_classify_document_invoice_3_keywords(self):
        """Test de clasificación como Factura con 3 keywords."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "FACTURA Total: 100.00 Cliente: Test Proveedor: Test"
            result = textract_service.classify_document(text)
            
            assert result == "Factura"
    
    def test_classify_document_information(self):
        """Test de clasificación como Información."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "Este es un documento de información general"
            result = textract_service.classify_document(text)
            
            assert result == "Información"
    
    def test_extract_invoice_data_all_fields(self):
        """Test de extracción de todos los campos de factura."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            mock_response = {
                "Blocks": [
                    {"BlockType": "LINE", "Text": "Cliente: Juan Pérez"},
                    {"BlockType": "LINE", "Text": "Total: 100.00"},
                    {"BlockType": "KEY_VALUE_SET", "EntityTypes": ["KEY"], "Id": "key1",
                     "Relationships": [{"Type": "CHILD", "Ids": ["child1"]}]},
                    {"BlockType": "WORD", "Id": "child1", "Text": "Cliente"},
                    {"BlockType": "KEY_VALUE_SET", "EntityTypes": ["VALUE"], "Id": "value1",
                     "Relationships": [{"Type": "CHILD", "Ids": ["child2"]}]},
                    {"BlockType": "WORD", "Id": "child2", "Text": "Juan Pérez"},
                ]
            }
            
            result = textract_service.extract_invoice_data(mock_response)
            
            assert "cliente" in result
            assert "proveedor" in result
            assert "numero_factura" in result
            assert "fecha" in result
            assert "productos" in result
            assert "total" in result
    
    def test_extract_invoice_data_empty_blocks(self):
        """Test de extracción con blocks vacío."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            mock_response = {"Blocks": []}
            
            result = textract_service.extract_invoice_data(mock_response)
            
            assert result is not None
            assert "cliente" in result
    
    def test_extract_information_data_description(self):
        """Test de extracción de descripción de información."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "Este es un documento de información general sobre el sistema."
            result = textract_service.extract_information_data(text)
            
            assert "descripcion" in result
            assert result["descripcion"] is not None
    
    def test_extract_information_data_sentiment_positive(self):
        """Test de extracción con sentimiento positivo."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "Excelente trabajo, muy bueno, perfecto, gracias"
            result = textract_service.extract_information_data(text)
            
            assert result["sentimiento"] == "positivo"
    
    def test_extract_information_data_sentiment_negative(self):
        """Test de extracción con sentimiento negativo."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "Malo, error, problema, rechazado, fallo"
            result = textract_service.extract_information_data(text)
            
            assert result["sentimiento"] == "negativo"
    
    def test_extract_information_data_sentiment_neutral(self):
        """Test de extracción con sentimiento neutral."""
        with patch('app.shared.textract_service.boto3.client'):
            textract_service = TextractService()
            
            text = "Este es un documento informativo sin emociones"
            result = textract_service.extract_information_data(text)
            
            assert result["sentimiento"] == "neutral"
    
    def test_analyze_document_success(self):
        """Test de análisis exitoso de documento."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.return_value = {"Blocks": []}
        
        with patch('app.shared.textract_service.boto3.client', return_value=mock_textract):
            textract_service = TextractService()
            textract_service.client = mock_textract
            result = textract_service.analyze_document("bucket", "key")
            
            assert result is not None
            mock_textract.analyze_document.assert_called_once()
    
    def test_analyze_document_bucket_not_found(self):
        """Test de análisis con bucket inexistente."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            "AnalyzeDocument"
        )
        
        with patch('app.shared.textract_service.boto3.client', return_value=mock_textract):
            textract_service = TextractService()
            textract_service.client = mock_textract
            
            with pytest.raises(ExternalServiceError) as exc_info:
                textract_service.analyze_document("nonexistent-bucket", "key")
            
            assert "Textract" in str(exc_info.value.message)
    
    @patch('app.shared.textract_service.boto3.client')
    def test_analyze_document_key_not_found(self, mock_boto_client):
        """Test de análisis con s3_key inexistente."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.side_effect = ClientError(
            {"Error": {"Code": "InvalidS3ObjectException", "Message": "Not found"}},
            "AnalyzeDocument"
        )
        mock_boto_client.return_value = mock_textract
        
        textract_service = TextractService()
        
        with pytest.raises(ExternalServiceError):
            textract_service.analyze_document("bucket", "nonexistent-key")
    
    @patch('app.shared.textract_service.boto3.client')
    def test_analyze_document_access_denied(self, mock_boto_client):
        """Test de análisis con error AccessDenied."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "AnalyzeDocument"
        )
        mock_boto_client.return_value = mock_textract
        
        textract_service = TextractService()
        
        with pytest.raises(ExternalServiceError):
            textract_service.analyze_document("bucket", "key")
    
    @patch('app.shared.textract_service.boto3.client')
    def test_analyze_document_invalid_parameter(self, mock_boto_client):
        """Test de análisis con InvalidParameter."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.side_effect = ClientError(
            {"Error": {"Code": "InvalidParameterException", "Message": "Invalid"}},
            "AnalyzeDocument"
        )
        mock_boto_client.return_value = mock_textract
        
        textract_service = TextractService()
        
        with pytest.raises(ExternalServiceError):
            textract_service.analyze_document("bucket", "key")
    
    def test_analyze_document_feature_types(self):
        """Test de verificación de FeatureTypes correctos."""
        mock_textract = MagicMock()
        mock_textract.analyze_document.return_value = {"Blocks": []}
        
        with patch('app.shared.textract_service.boto3.client', return_value=mock_textract):
            textract_service = TextractService()
            textract_service.client = mock_textract
            textract_service.analyze_document("bucket", "key")
            
            call_args = mock_textract.analyze_document.call_args
            assert "FeatureTypes" in call_args.kwargs
            assert "FORMS" in call_args.kwargs["FeatureTypes"]
            assert "TABLES" in call_args.kwargs["FeatureTypes"]
    
    def test_detect_document_text_success(self):
        """Test de detección exitosa de texto."""
        mock_textract = MagicMock()
        mock_textract.detect_document_text.return_value = {"Blocks": []}
        
        with patch('app.shared.textract_service.boto3.client', return_value=mock_textract):
            textract_service = TextractService()
            textract_service.client = mock_textract
            result = textract_service.detect_document_text("bucket", "key")
            
            assert result is not None
            mock_textract.detect_document_text.assert_called_once()
    
    def test_detect_document_text_error(self):
        """Test de detección con error de Textract."""
        mock_textract = MagicMock()
        mock_textract.detect_document_text.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DetectDocumentText"
        )
        
        with patch('app.shared.textract_service.boto3.client', return_value=mock_textract):
            textract_service = TextractService()
            textract_service.client = mock_textract
            
            with pytest.raises(ExternalServiceError):
                textract_service.detect_document_text("bucket", "key")

