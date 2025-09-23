"""
Deliverable schemas for SkillForge AI Project Service
Conformes aux spécifications officielles de la documentation
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
from uuid import UUID

from app.models.project import DeliverableType, DeliverableStatus


# Base deliverable schemas
class DeliverableBase(BaseModel):
    """Base deliverable schema according to official documentation."""
    type: DeliverableType = Field(..., description="Type de livrable (FILE_UPLOAD, GIT_REPO_URL, EXTERNAL_URL)")
    file_path_or_url: str = Field(..., min_length=1, description="Chemin vers le fichier sur GCS ou URL du dépôt/lien")
    notes: Optional[str] = Field(None, max_length=2000, description="Notes optionnelles de l'apprenant sur sa soumission")
    milestone_id: Optional[UUID] = Field(None, description="Milestone associé (optionnel)")
    
    @field_validator('file_path_or_url')
    @classmethod
    def validate_file_path_or_url(cls, v, info):
        """Valide le chemin/URL selon le type de livrable."""
        values = info.data if hasattr(info, 'data') else {}
        deliverable_type = values.get('type')
        
        if deliverable_type == DeliverableType.GIT_REPO_URL:
            # Validation basique pour les URLs Git
            if not (v.startswith('https://github.com/') or 
                   v.startswith('https://gitlab.com/') or
                   v.startswith('https://bitbucket.org/') or
                   v.endswith('.git')):
                raise ValueError('URL de dépôt Git invalide')
        elif deliverable_type == DeliverableType.EXTERNAL_URL:
            # Validation URL externe
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('URL externe invalide')
        elif deliverable_type == DeliverableType.FILE_UPLOAD:
            # Validation chemin GCS
            if not (v.startswith('gs://') or v.startswith('/projects/')):
                raise ValueError('Chemin de fichier GCS invalide')
        
        return v


class DeliverableCreate(DeliverableBase):
    """Schema pour créer un nouveau livrable."""
    project_id: UUID = Field(..., description="ID du projet")
    
    # Métadonnées optionnelles pour FILE_UPLOAD
    original_filename: Optional[str] = Field(None, max_length=255, description="Nom de fichier original")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="Taille du fichier en octets")
    mime_type: Optional[str] = Field(None, max_length=100, description="Type MIME du fichier")


class DeliverableUpdate(BaseModel):
    """Schema pour mettre à jour un livrable."""
    type: Optional[DeliverableType] = None
    file_path_or_url: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    milestone_id: Optional[UUID] = None
    
    # Métadonnées de fichier
    original_filename: Optional[str] = Field(None, max_length=255)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)


class DeliverableReview(BaseModel):
    """Schema pour réviser un livrable."""
    status: DeliverableStatus = Field(..., description="Nouveau statut du livrable")
    review_notes: Optional[str] = Field(None, max_length=2000, description="Notes de révision")
    
    @field_validator('status')
    @classmethod
    def validate_review_status(cls, v):
        """Seuls certains statuts sont permis lors d'une révision."""
        allowed_statuses = {
            DeliverableStatus.APPROVED,
            DeliverableStatus.REJECTED,
            DeliverableStatus.REVISION_REQUESTED,
            DeliverableStatus.UNDER_REVIEW
        }
        if v not in allowed_statuses:
            raise ValueError(f'Statut de révision invalide. Autorisés: {[s.value for s in allowed_statuses]}')
        return v


class DeliverableResponse(DeliverableBase):
    """Schema de réponse pour un livrable."""
    id: UUID
    project_id: UUID
    user_id: UUID
    status: DeliverableStatus
    version: str
    
    # Timestamps
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Révision
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    # Versions
    previous_version_id: Optional[UUID] = None
    
    # Métadonnées de fichier
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Statistiques
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None
    
    # Métadonnées additionnelles
    deliverable_metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class DeliverableListResponse(BaseModel):
    """Schema de réponse pour la liste des livrables."""
    deliverables: list[DeliverableResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class DeliverableStatsResponse(BaseModel):
    """Schema de réponse pour les statistiques des livrables."""
    total_deliverables: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_project: Dict[str, int]
    total_downloads: int
    average_review_time_hours: Optional[float] = None


# Schémas pour le workflow de soumission
class DeliverableSubmission(BaseModel):
    """Schema pour la soumission d'un livrable."""
    deliverable_id: UUID
    submission_notes: Optional[str] = Field(None, max_length=1000, description="Notes de soumission")


class DeliverableVersionCreate(BaseModel):
    """Schema pour créer une nouvelle version d'un livrable."""
    base_deliverable_id: UUID = Field(..., description="ID du livrable de base")
    file_path_or_url: str = Field(..., description="Nouveau chemin/URL")
    notes: Optional[str] = Field(None, max_length=2000, description="Notes sur cette nouvelle version")
    version_notes: Optional[str] = Field(None, max_length=1000, description="Notes spécifiques à la version")


# Schémas pour les interactions avec les attachments
class DeliverableAttachmentResponse(BaseModel):
    """Schema pour les fichiers attachés aux livrables."""
    id: UUID
    deliverable_id: UUID
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    uploaded_by: UUID
    upload_source: str
    is_public: bool
    download_count: int
    created_at: datetime
    file_metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


# Utilitaires de validation
class DeliverableValidation(BaseModel):
    """Utilitaires de validation pour les livrables."""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
        """Valide l'extension du fichier."""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return extension in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_mb: int) -> bool:
        """Valide la taille du fichier."""
        max_size_bytes = max_size_mb * 1024 * 1024
        return size_bytes <= max_size_bytes
    
    @staticmethod
    def get_allowed_extensions_by_type(deliverable_type: DeliverableType) -> list[str]:
        """Retourne les extensions autorisées par type de livrable."""
        if deliverable_type == DeliverableType.FILE_UPLOAD:
            return [
                'pdf', 'doc', 'docx', 'txt', 'md',  # Documents
                'zip', 'tar', 'gz', 'rar',          # Archives
                'jpg', 'jpeg', 'png', 'gif', 'svg', # Images
                'mp4', 'avi', 'mov', 'mkv',         # Vidéos
                'py', 'js', 'ts', 'java', 'cpp',    # Code
                'json', 'xml', 'csv', 'xlsx'        # Données
            ]
        return []