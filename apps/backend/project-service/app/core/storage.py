"""
Google Cloud Storage service for SkillForge AI Project Service
Gestion des uploads et downloads de fichiers livrables
"""

import os
import hashlib
import uuid
from typing import BinaryIO, Optional, AsyncGenerator
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from fastapi import UploadFile, HTTPException, status
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import aiofiles

from app.core.config import get_settings

settings = get_settings()


class GCSService:
    """Service Google Cloud Storage pour les livrables."""
    
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.project_id = settings.GCP_PROJECT_ID
        self._client = None
        self._bucket = None
    
    @property
    def client(self):
        """Client GCS lazy-loaded."""
        if self._client is None:
            try:
                self._client = storage.Client(project=self.project_id)
            except DefaultCredentialsError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="GCS credentials not configured"
                )
        return self._client
    
    @property
    def bucket(self):
        """Bucket GCS lazy-loaded."""
        if self._bucket is None:
            try:
                self._bucket = self.client.bucket(self.bucket_name)
                # Vérifier que le bucket existe
                if not self._bucket.exists():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"GCS bucket '{self.bucket_name}' not found"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"GCS bucket access error: {str(e)}"
                )
        return self._bucket
    
    def generate_file_path(self, prefix: str, filename: str, user_id: str) -> str:
        """Génère un chemin unique pour le fichier."""
        # Nettoyer le nom de fichier
        safe_filename = self._sanitize_filename(filename)
        
        # Générer un UUID pour éviter les collisions
        unique_id = str(uuid.uuid4())
        
        # Timestamp pour organisation
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        
        return f"{prefix}/{timestamp}/{user_id}/{unique_id}_{safe_filename}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Nettoie le nom de fichier pour GCS."""
        # Supprimer les caractères dangereux
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limiter la longueur
        if len(safe_name) > 100:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:90] + ext
        
        return safe_name
    
    async def upload_file(
        self, 
        file: UploadFile, 
        file_path: str,
        content_type: Optional[str] = None
    ) -> dict:
        """Upload un fichier vers GCS de manière asynchrone."""
        
        try:
            # Lire le contenu du fichier
            content = await file.read()
            await file.seek(0)  # Reset pour d'autres lectures si nécessaire
            
            # Calculer le hash SHA-256
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Créer le blob GCS
            blob = self.bucket.blob(file_path)
            
            # Configurer les métadonnées
            blob.metadata = {
                'original_filename': file.filename,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'file_hash_sha256': file_hash,
                'content_type': content_type or file.content_type
            }
            
            # Upload de manière synchrone (GCS client n'est pas async)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: blob.upload_from_string(
                    content,
                    content_type=content_type or file.content_type
                )
            )
            
            return {
                'file_path': f"gs://{self.bucket_name}/{file_path}",
                'file_size': len(content),
                'file_hash': file_hash,
                'content_type': content_type or file.content_type,
                'upload_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def download_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """Download un fichier depuis GCS de manière asynchrone."""
        
        try:
            # Extraire le path du blob depuis l'URL GCS
            if file_path.startswith('gs://'):
                # Format: gs://bucket-name/path/to/file
                path_parts = file_path.replace('gs://', '').split('/', 1)
                if len(path_parts) != 2 or path_parts[0] != self.bucket_name:
                    raise ValueError("Invalid GCS path format")
                blob_path = path_parts[1]
            else:
                blob_path = file_path
            
            blob = self.bucket.blob(blob_path)
            
            # Vérifier que le fichier existe
            if not await asyncio.get_event_loop().run_in_executor(None, blob.exists):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found in storage"
                )
            
            # Download par chunks pour éviter de charger tout en mémoire
            loop = asyncio.get_event_loop()
            
            def download_chunks():
                """Download le fichier par chunks."""
                chunk_size = 8192  # 8KB chunks
                start = 0
                
                while True:
                    end = start + chunk_size - 1
                    
                    try:
                        chunk = blob.download_as_bytes(start=start, end=end)
                        if not chunk:
                            break
                        yield chunk
                        start += chunk_size
                    except Exception:
                        # Fin du fichier atteinte
                        break
            
            # Streamer les chunks de manière asynchrone
            for chunk in await loop.run_in_executor(None, lambda: list(download_chunks())):
                yield chunk
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """Supprime un fichier de GCS."""
        
        try:
            # Extraire le path du blob
            if file_path.startswith('gs://'):
                path_parts = file_path.replace('gs://', '').split('/', 1)
                if len(path_parts) != 2 or path_parts[0] != self.bucket_name:
                    raise ValueError("Invalid GCS path format")
                blob_path = path_parts[1]
            else:
                blob_path = file_path
            
            blob = self.bucket.blob(blob_path)
            
            # Supprimer de manière asynchrone
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.delete)
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    async def get_file_metadata(self, file_path: str) -> dict:
        """Récupère les métadonnées d'un fichier."""
        
        try:
            # Extraire le path du blob
            if file_path.startswith('gs://'):
                path_parts = file_path.replace('gs://', '').split('/', 1)
                if len(path_parts) != 2 or path_parts[0] != self.bucket_name:
                    raise ValueError("Invalid GCS path format")
                blob_path = path_parts[1]
            else:
                blob_path = file_path
            
            blob = self.bucket.blob(blob_path)
            
            # Recharger les métadonnées
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.reload)
            
            return {
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'metadata': blob.metadata or {},
                'md5_hash': blob.md5_hash,
                'crc32c': blob.crc32c
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file metadata: {str(e)}"
            )
    
    def generate_signed_url(
        self, 
        file_path: str, 
        expiration_hours: int = 24,
        method: str = "GET"
    ) -> str:
        """Génère une URL signée pour accès temporaire."""
        
        try:
            # Extraire le path du blob
            if file_path.startswith('gs://'):
                path_parts = file_path.replace('gs://', '').split('/', 1)
                if len(path_parts) != 2 or path_parts[0] != self.bucket_name:
                    raise ValueError("Invalid GCS path format")
                blob_path = path_parts[1]
            else:
                blob_path = file_path
            
            blob = self.bucket.blob(blob_path)
            
            # Générer l'URL signée
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method=method,
                version="v4"
            )
            
            return signed_url
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate signed URL: {str(e)}"
            )


# Instance globale du service
gcs_service = GCSService()


# Fonctions utilitaires publiques
async def upload_file_to_gcs(
    file: UploadFile, 
    prefix: str,
    user_id: str = "anonymous"
) -> str:
    """Upload un fichier vers GCS et retourne le chemin."""
    
    # Validation basique du fichier
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    if file.size and file.size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 100MB limit"
        )
    
    # Générer le chemin de fichier
    file_path = gcs_service.generate_file_path(prefix, file.filename, user_id)
    
    # Upload le fichier
    result = await gcs_service.upload_file(file, file_path)
    
    return result['file_path']


async def download_file_from_gcs(file_path: str) -> AsyncGenerator[bytes, None]:
    """Download un fichier depuis GCS."""
    async for chunk in gcs_service.download_file(file_path):
        yield chunk


async def delete_file_from_gcs(file_path: str) -> bool:
    """Supprime un fichier de GCS."""
    return await gcs_service.delete_file(file_path)


async def get_file_metadata_from_gcs(file_path: str) -> dict:
    """Récupère les métadonnées d'un fichier."""
    return await gcs_service.get_file_metadata(file_path)


def generate_signed_download_url(file_path: str, expiration_hours: int = 24) -> str:
    """Génère une URL de téléchargement signée."""
    return gcs_service.generate_signed_url(file_path, expiration_hours, "GET")