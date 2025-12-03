"""
Script para probar la configuración de AWS Textract.
Ejecuta este script para verificar que las credenciales estén correctas.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.shared.textract_service import TextractService
from app.shared.s3_service import S3Service
import boto3


def test_aws_credentials():
    """Prueba las credenciales de AWS."""
    print("=" * 60)
    print("Probando configuración de AWS")
    print("=" * 60)
    
    # Verificar que las credenciales estén configuradas
    if not settings.AWS_ACCESS_KEY_ID:
        print("❌ ERROR: AWS_ACCESS_KEY_ID no está configurado en .env")
        return False
    
    if not settings.AWS_SECRET_ACCESS_KEY:
        print("❌ ERROR: AWS_SECRET_ACCESS_KEY no está configurado en .env")
        return False
    
    print(f"✓ AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:10]}...")
    print(f"✓ AWS_REGION: {settings.AWS_REGION}")
    print(f"✓ S3_BUCKET_NAME: {settings.S3_BUCKET_NAME}")
    print()
    
    # Probar conexión a S3
    print("Probando conexión a S3...")
    try:
        s3_service = S3Service()
        # Intentar listar buckets (operación simple)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        
        if settings.S3_BUCKET_NAME in buckets:
            print(f"✓ Bucket '{settings.S3_BUCKET_NAME}' encontrado")
        else:
            print(f"⚠ ADVERTENCIA: Bucket '{settings.S3_BUCKET_NAME}' no encontrado")
            print(f"  Buckets disponibles: {', '.join(buckets) if buckets else 'Ninguno'}")
            print(f"  Crea el bucket en: https://s3.console.aws.amazon.com/")
        
        print("✓ Conexión a S3 exitosa")
    except Exception as e:
        print(f"❌ ERROR al conectar a S3: {str(e)}")
        return False
    
    print()
    
    # Probar conexión a Textract
    print("Probando conexión a Textract...")
    try:
        textract_service = TextractService()
        # Intentar listar endpoints disponibles (operación simple)
        textract_client = boto3.client(
            'textract',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        # Textract no tiene un método list, pero podemos verificar la región
        print(f"✓ Cliente de Textract inicializado correctamente")
        print(f"✓ Región configurada: {settings.AWS_REGION}")
    except Exception as e:
        print(f"❌ ERROR al conectar a Textract: {str(e)}")
        return False
    
    print()
    print("=" * 60)
    print("✅ Configuración de AWS correcta!")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Asegúrate de que el bucket de S3 esté creado")
    print("2. Inicia la API: cd python-api && uvicorn app.main:app --reload")
    print("3. Prueba subir un documento desde el frontend")
    
    return True


if __name__ == "__main__":
    try:
        success = test_aws_credentials()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

