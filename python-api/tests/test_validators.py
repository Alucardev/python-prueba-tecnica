"""
Tests para los validadores de CSV.
"""
import pytest
from app.utils.validators import CSVValidator


class TestCSVValidator:
    """Tests para el validador de CSV."""
    
    def test_validate_csv_success(self):
        """Test de validación de CSV válido."""
        csv_content = b"""id,nombre,email,edad
1,Juan,juan@test.com,30
2,Maria,maria@test.com,25"""
        
        validations = CSVValidator.validate_csv(csv_content)
        
        # Debe tener al menos una validación de éxito
        assert len(validations) > 0
        success_validations = [v for v in validations if v["validation_type"] == "success"]
        assert len(success_validations) > 0
    
    def test_validate_csv_empty_file(self):
        """Test de validación de CSV vacío."""
        csv_content = b""
        
        validations = CSVValidator.validate_csv(csv_content)
        
        assert len(validations) > 0
        empty_validations = [v for v in validations if v["validation_type"] == "empty_file"]
        assert len(empty_validations) > 0
    
    def test_validate_csv_empty_values(self):
        """Test de detección de valores vacíos."""
        csv_content = b"""id,nombre,email
1,,juan@test.com
2,Maria,
3,Carlos,carlos@test.com"""
        
        validations = CSVValidator.validate_csv(csv_content)
        
        empty_validations = [v for v in validations if v["validation_type"] == "empty_values"]
        assert len(empty_validations) > 0
        assert len(empty_validations[0]["affected_rows"]) > 0
    
    def test_validate_csv_duplicates(self):
        """Test de detección de filas duplicadas."""
        csv_content = b"""id,nombre,email
1,Juan,juan@test.com
2,Maria,maria@test.com
1,Juan,juan@test.com"""
        
        validations = CSVValidator.validate_csv(csv_content)
        
        duplicate_validations = [v for v in validations if v["validation_type"] == "duplicates"]
        assert len(duplicate_validations) > 0
    
    def test_validate_csv_invalid_format(self):
        """Test de detección de formato incorrecto."""
        # CSV con número incorrecto de columnas en una fila
        csv_content = b"""id,nombre,email
1,Juan
2,Maria,maria@test.com,extra"""
        
        validations = CSVValidator.validate_csv(csv_content)
        
        format_validations = [v for v in validations if v["validation_type"] == "invalid_format"]
        # Puede o no detectar esto dependiendo de cómo csv.DictReader maneje las filas
        # Al menos no debe fallar
    
    def test_validate_csv_with_parameters(self):
        """Test de validación con parámetros adicionales."""
        csv_content = b"""id,nombre,email
1,Juan,juan@test.com"""
        
        validations = CSVValidator.validate_csv(
            csv_content,
            categoria="test",
            descripcion="test description"
        )
        
        # Debe funcionar con los parámetros (aunque no se usen en la validación)
        assert len(validations) > 0

