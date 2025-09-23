"""
Deliverable API endpoints for SkillForge AI Project Service
Gestion complète des livrables selon les spécifications officielles
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.project import ProjectDeliverable, Project, ProjectMember, ProjectRole
from app.schemas.deliverable import (
    DeliverableCreate, DeliverableUpdate, DeliverableResponse,
    DeliverableListResponse, DeliverableStatsResponse,
    DeliverableReview, DeliverableSubmission, DeliverableVersionCreate,
    DeliverableValidation
)
from app.models.project import DeliverableStatus, DeliverableType
from app.core.storage import upload_file_to_gcs, download_file_from_gcs
from app.core.permissions import (
    check_project_permission, has_project_access, get_accessible_projects,
    PermissionType
)

router = APIRouter(prefix="/deliverables", tags=["deliverables"])


# Utilitaires de permission
async def check_deliverable_access(
    deliverable_id: UUID,
    user_id: UUID,
    session: Session,
    required_role: Optional[ProjectRole] = None
) -> ProjectDeliverable:
    """Vérifie l'accès à un livrable et retourne le livrable."""
    
    # Récupérer le livrable avec son projet
    query = select(ProjectDeliverable).options(
        selectinload(ProjectDeliverable.project)
    ).where(ProjectDeliverable.id == deliverable_id)
    
    deliverable = session.exec(query).first()
    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livrable introuvable"
        )
    
    # Vérifier l'accès au projet
    project_access = await has_project_access(
        project_id=deliverable.project_id,
        user_id=user_id,
        session=session,
        required_role=required_role
    )
    
    if not project_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à ce livrable"
        )
    
    return deliverable


# Endpoints CRUD
@router.get("/", response_model=DeliverableListResponse)
async def list_deliverables(
    project_id: Optional[UUID] = Query(None, description="Filtrer par projet"),
    user_id: Optional[UUID] = Query(None, description="Filtrer par utilisateur"),
    status: Optional[DeliverableStatus] = Query(None, description="Filtrer par statut"),
    type: Optional[DeliverableType] = Query(None, description="Filtrer par type"),
    milestone_id: Optional[UUID] = Query(None, description="Filtrer par milestone"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(20, ge=1, le=100, description="Éléments par page"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Liste les livrables avec pagination et filtres."""
    
    # Construire la requête de base
    query = select(ProjectDeliverable)
    
    # Appliquer les filtres
    conditions = []
    
    if project_id:
        # Vérifier l'accès au projet
        await check_project_permission(project_id, current_user["id"], session)
        conditions.append(ProjectDeliverable.project_id == project_id)
    
    if user_id:
        conditions.append(ProjectDeliverable.user_id == user_id)
    
    if status:
        conditions.append(ProjectDeliverable.status == status)
    
    if type:
        conditions.append(ProjectDeliverable.type == type)
    
    if milestone_id:
        conditions.append(ProjectDeliverable.milestone_id == milestone_id)
    
    # Si aucun projet spécifique, filtrer par projets accessibles
    if not project_id:
        accessible_projects = await get_accessible_projects(current_user["id"], session)
        conditions.append(ProjectDeliverable.project_id.in_(accessible_projects))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Pagination
    offset = (page - 1) * per_page
    
    # Compter le total
    count_query = select(func.count(ProjectDeliverable.id)).where(and_(*conditions) if conditions else True)
    total = session.exec(count_query).one()
    
    # Récupérer les résultats paginés
    query = query.offset(offset).limit(per_page).order_by(ProjectDeliverable.submitted_at.desc())
    deliverables = session.exec(query).all()
    
    return DeliverableListResponse(
        deliverables=[DeliverableResponse.model_validate(d) for d in deliverables],
        total=total,
        page=page,
        per_page=per_page,
        has_next=(offset + per_page) < total,
        has_prev=page > 1
    )


@router.get("/{deliverable_id}", response_model=DeliverableResponse)
async def get_deliverable(
    deliverable_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Récupère un livrable par son ID."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    return DeliverableResponse.model_validate(deliverable)


@router.post("/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED)
async def create_deliverable(
    deliverable_data: DeliverableCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crée un nouveau livrable."""
    
    # Vérifier l'accès au projet
    await check_project_permission(
        deliverable_data.project_id, 
        current_user["id"], 
        session, 
        PermissionType.SUBMIT_DELIVERABLES
    )
    
    # Créer le livrable
    deliverable = ProjectDeliverable(
        **deliverable_data.model_dump(),
        user_id=current_user["id"],
        status=DeliverableStatus.DRAFT
    )
    
    session.add(deliverable)
    session.commit()
    session.refresh(deliverable)
    
    return DeliverableResponse.model_validate(deliverable)


@router.put("/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: UUID,
    deliverable_data: DeliverableUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Met à jour un livrable."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    # Seul le propriétaire peut modifier (ou admin du projet)
    if (deliverable.user_id != current_user["id"] and 
        not await has_project_role(deliverable.project_id, current_user["id"], 
                                  [ProjectRole.OWNER, ProjectRole.MANAGER], session)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire du livrable peut le modifier"
        )
    
    # Mettre à jour les champs modifiés
    update_data = deliverable_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deliverable, field, value)
    
    deliverable.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(deliverable)
    
    return DeliverableResponse.model_validate(deliverable)


@router.delete("/{deliverable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deliverable(
    deliverable_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Supprime un livrable (soft delete)."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    # Seul le propriétaire peut supprimer (ou admin du projet)
    if (deliverable.user_id != current_user["id"] and 
        not await has_project_role(deliverable.project_id, current_user["id"], 
                                  [ProjectRole.OWNER, ProjectRole.MANAGER], session)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire du livrable peut le supprimer"
        )
    
    # Soft delete
    deliverable.is_active = False
    deliverable.deleted_at = datetime.utcnow()
    session.commit()


# Gestion des fichiers
@router.post("/{deliverable_id}/upload", response_model=DeliverableResponse)
async def upload_deliverable_file(
    deliverable_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload un fichier pour un livrable."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    # Vérifier que c'est un livrable de type FILE_UPLOAD
    if deliverable.type != DeliverableType.FILE_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload de fichier uniquement pour les livrables de type FILE_UPLOAD"
        )
    
    # Valider le fichier
    if not DeliverableValidation.validate_file_extension(
        file.filename, 
        DeliverableValidation.get_allowed_extensions_by_type(DeliverableType.FILE_UPLOAD)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type de fichier non autorisé"
        )
    
    if not DeliverableValidation.validate_file_size(file.size, 100):  # 100MB max
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux (max 100MB)"
        )
    
    # Upload vers GCS
    try:
        file_path = await upload_file_to_gcs(
            file, 
            f"deliverables/{deliverable.project_id}/{deliverable_id}/"
        )
        
        # Mettre à jour le livrable
        deliverable.file_path_or_url = file_path
        deliverable.original_filename = file.filename
        deliverable.file_size_bytes = file.size
        deliverable.mime_type = file.content_type
        deliverable.updated_at = datetime.utcnow()
        
        session.commit()
        session.refresh(deliverable)
        
        return DeliverableResponse.model_validate(deliverable)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.get("/{deliverable_id}/download")
async def download_deliverable_file(
    deliverable_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Télécharge le fichier d'un livrable."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    if deliverable.type != DeliverableType.FILE_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Téléchargement uniquement pour les fichiers uploadés"
        )
    
    try:
        # Télécharger depuis GCS
        file_stream = await download_file_from_gcs(deliverable.file_path_or_url)
        
        # Mettre à jour les statistiques
        deliverable.download_count += 1
        deliverable.last_downloaded_at = datetime.utcnow()
        session.commit()
        
        return StreamingResponse(
            file_stream,
            media_type=deliverable.mime_type or 'application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename={deliverable.original_filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du téléchargement: {str(e)}"
        )


# Workflow de révision
@router.post("/{deliverable_id}/submit", response_model=DeliverableResponse)
async def submit_deliverable(
    deliverable_id: UUID,
    submission: DeliverableSubmission,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Soumet un livrable pour révision."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session
    )
    
    # Seul le propriétaire peut soumettre
    if deliverable.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut soumettre le livrable"
        )
    
    if deliverable.status != DeliverableStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les livrables en brouillon peuvent être soumis"
        )
    
    # Mettre à jour le statut
    deliverable.status = DeliverableStatus.SUBMITTED
    deliverable.submitted_at = datetime.utcnow()
    if submission.submission_notes:
        deliverable.notes = submission.submission_notes
    
    session.commit()
    session.refresh(deliverable)
    
    return DeliverableResponse.model_validate(deliverable)


@router.post("/{deliverable_id}/review", response_model=DeliverableResponse)
async def review_deliverable(
    deliverable_id: UUID,
    review: DeliverableReview,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Révise un livrable soumis."""
    
    deliverable = await check_deliverable_access(
        deliverable_id, current_user["id"], session, 
        required_role=ProjectRole.MANAGER
    )
    
    if deliverable.status not in [DeliverableStatus.SUBMITTED, DeliverableStatus.UNDER_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les livrables soumis peuvent être révisés"
        )
    
    # Mettre à jour la révision
    deliverable.status = review.status
    deliverable.reviewed_by = current_user["id"]
    deliverable.reviewed_at = datetime.utcnow()
    deliverable.review_notes = review.review_notes
    
    session.commit()
    session.refresh(deliverable)
    
    return DeliverableResponse.model_validate(deliverable)


# Versioning
@router.post("/{deliverable_id}/versions", response_model=DeliverableResponse)
async def create_deliverable_version(
    deliverable_id: UUID,
    version_data: DeliverableVersionCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Crée une nouvelle version d'un livrable."""
    
    base_deliverable = await check_deliverable_access(
        version_data.base_deliverable_id, current_user["id"], session
    )
    
    # Seul le propriétaire peut créer une version
    if base_deliverable.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut créer une nouvelle version"
        )
    
    # Calculer le nouveau numéro de version
    current_version = float(base_deliverable.version)
    new_version = f"{current_version + 0.1:.1f}"
    
    # Créer la nouvelle version
    new_deliverable = ProjectDeliverable(
        project_id=base_deliverable.project_id,
        user_id=current_user["id"],
        milestone_id=base_deliverable.milestone_id,
        type=base_deliverable.type,
        file_path_or_url=version_data.file_path_or_url,
        notes=version_data.notes,
        version=new_version,
        previous_version_id=base_deliverable.id,
        status=DeliverableStatus.DRAFT
    )
    
    session.add(new_deliverable)
    session.commit()
    session.refresh(new_deliverable)
    
    return DeliverableResponse.model_validate(new_deliverable)


# Statistiques
@router.get("/stats/overview", response_model=DeliverableStatsResponse)
async def get_deliverable_stats(
    project_id: Optional[UUID] = Query(None, description="Statistiques pour un projet"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retourne les statistiques des livrables."""
    
    # Construire la requête de base
    base_query = select(ProjectDeliverable)
    
    if project_id:
        await check_project_permission(project_id, current_user["id"], session)
        base_query = base_query.where(ProjectDeliverable.project_id == project_id)
    else:
        # Filtrer par projets accessibles
        accessible_projects = await get_accessible_projects(current_user["id"], session)
        base_query = base_query.where(ProjectDeliverable.project_id.in_(accessible_projects))
    
    # Total des livrables
    total_deliverables = session.exec(
        select(func.count(ProjectDeliverable.id)).where(base_query.whereclause)
    ).one()
    
    # Par statut
    status_stats = session.exec(
        select(ProjectDeliverable.status, func.count(ProjectDeliverable.id))
        .where(base_query.whereclause)
        .group_by(ProjectDeliverable.status)
    ).all()
    
    # Par type
    type_stats = session.exec(
        select(ProjectDeliverable.type, func.count(ProjectDeliverable.id))
        .where(base_query.whereclause)
        .group_by(ProjectDeliverable.type)
    ).all()
    
    # Total des téléchargements
    total_downloads = session.exec(
        select(func.sum(ProjectDeliverable.download_count))
        .where(base_query.whereclause)
    ).one() or 0
    
    return DeliverableStatsResponse(
        total_deliverables=total_deliverables,
        by_status={status.value: count for status, count in status_stats},
        by_type={type_.value: count for type_, count in type_stats},
        by_project={},  # À implémenter si nécessaire
        total_downloads=total_downloads
    )


# Utilitaires privées
async def get_accessible_projects(user_id: UUID, session: Session) -> List[UUID]:
    """Retourne la liste des projets accessibles par l'utilisateur."""
    # À implémenter selon la logique de permissions
    query = select(ProjectMember.project_id).where(ProjectMember.user_id == user_id)
    return [project_id for project_id, in session.exec(query).all()]


async def has_project_role(
    project_id: UUID, 
    user_id: UUID, 
    required_roles: List[ProjectRole], 
    session: Session
) -> bool:
    """Vérifie si l'utilisateur a l'un des rôles requis sur le projet."""
    query = select(ProjectMember).where(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(required_roles)
        )
    )
    return session.exec(query).first() is not None