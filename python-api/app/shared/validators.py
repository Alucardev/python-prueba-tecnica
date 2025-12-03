"""
Utilidades para validación de archivos CSV compartidas entre módulos.
"""
import csv
import io
from typing import List, Dict, Any, Optional


class CSVValidator:
    """Validador para archivos CSV."""

    @staticmethod
    def validate_csv(
        file_content: bytes,
        categoria: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Valida un archivo CSV y retorna una lista de validaciones aplicadas.

        Args:
            file_content: Contenido del archivo CSV en bytes
            categoria: Categoría del archivo (opcional, para referencia en validaciones)
            descripcion: Descripción del archivo (opcional, para referencia en validaciones)

        Returns:
            Lista de diccionarios con los resultados de validación
        """

        validations: List[Dict[str, Any]] = []

        try:
            # Decodificar el contenido del archivo
            file_text = file_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(file_text))

            # Convertir a lista para poder iterar múltiples veces
            rows = list(csv_reader)

            if not rows:
                validations.append(
                    {
                        "validation_type": "empty_file",
                        "message": "El archivo CSV está vacío",
                        "affected_rows": [],
                        "severity": "error",
                    }
                )
                return validations

            # Obtener los nombres de las columnas
            fieldnames = csv_reader.fieldnames or []

            # Validación 1: Valores vacíos
            empty_values = CSVValidator._check_empty_values(rows, fieldnames)
            if empty_values:
                validations.append(
                    {
                        "validation_type": "empty_values",
                        "message": f"Se encontraron {len(empty_values)} filas con valores vacíos",
                        "affected_rows": empty_values,
                        "severity": "warning",
                    }
                )

            # Validación 2: Tipos incorrectos (ejemplo: números en campos de texto)
            incorrect_types = CSVValidator._check_incorrect_types(rows, fieldnames)
            if incorrect_types:
                validations.append(
                    {
                        "validation_type": "incorrect_types",
                        "message": f"Se encontraron {len(incorrect_types)} filas con tipos de datos incorrectos",
                        "affected_rows": incorrect_types,
                        "severity": "error",
                    }
                )

            # Validación 3: Duplicados
            duplicates = CSVValidator._check_duplicates(rows)
            if duplicates:
                validations.append(
                    {
                        "validation_type": "duplicates",
                        "message": f"Se encontraron {len(duplicates)} filas duplicadas",
                        "affected_rows": duplicates,
                        "severity": "warning",
                    }
                )

            # Validación 4: Filas con formato incorrecto
            invalid_format = CSVValidator._check_invalid_format(rows, fieldnames)
            if invalid_format:
                validations.append(
                    {
                        "validation_type": "invalid_format",
                        "message": f"Se encontraron {len(invalid_format)} filas con formato incorrecto",
                        "affected_rows": invalid_format,
                        "severity": "error",
                    }
                )

            # Si no hay validaciones, agregar una de éxito
            if not validations:
                validations.append(
                    {
                        "validation_type": "success",
                        "message": "El archivo CSV pasó todas las validaciones",
                        "affected_rows": [],
                        "severity": "info",
                    }
                )

        except Exception as e:
            validations.append(
                {
                    "validation_type": "parse_error",
                    "message": f"Error al procesar el archivo CSV: {str(e)}",
                    "affected_rows": [],
                    "severity": "error",
                }
            )

        return validations

    @staticmethod
    def _check_empty_values(
        rows: List[Dict[str, Any]],
        fieldnames: List[str],
    ) -> List[int]:
        """
        Verifica filas con valores vacíos en campos requeridos.
        """

        empty_rows: List[int] = []
        for idx, row in enumerate(rows, start=2):  # Empezar en 2 (fila 1 es header)
            has_empty = any(
                not str(row.get(field, "")).strip() for field in fieldnames
            )
            if has_empty:
                empty_rows.append(idx)
        return empty_rows

    @staticmethod
    def _check_incorrect_types(
        rows: List[Dict[str, Any]],
        fieldnames: List[str],
    ) -> List[int]:
        """
        Verifica filas con tipos de datos incorrectos.
        """

        incorrect_rows: List[int] = []
        for idx, row in enumerate(rows, start=2):
            for field in fieldnames:
                value = row.get(field, "")
                # Si el campo contiene "id" o "numero", debería ser numérico
                if ("id" in field.lower() or "numero" in field.lower()) and value:
                    try:
                        float(value)
                    except ValueError:
                        incorrect_rows.append(idx)
                        break
        return incorrect_rows

    @staticmethod
    def _check_duplicates(rows: List[Dict[str, Any]]) -> List[int]:
        """
        Verifica filas duplicadas.
        """

        seen = set()
        duplicates: List[int] = []

        for idx, row in enumerate(rows, start=2):
            row_hash = hash(tuple(sorted(row.items())))
            if row_hash in seen:
                duplicates.append(idx)
            else:
                seen.add(row_hash)

        return duplicates

    @staticmethod
    def _check_invalid_format(
        rows: List[Dict[str, Any]],
        fieldnames: List[str],
    ) -> List[int]:
        """
        Verifica filas con formato incorrecto (número incorrecto de columnas).
        """

        invalid_rows: List[int] = []
        expected_columns = len(fieldnames)

        for idx, row in enumerate(rows, start=2):
            if len(row) != expected_columns:
                invalid_rows.append(idx)

        return invalid_rows


__all__ = ["CSVValidator"]


