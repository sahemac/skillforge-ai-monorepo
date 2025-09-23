"""
Permission management for SkillForge AI Project Service
Gestion des permissions granulaires pour les projets et livrables
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

from fastapi import HTTPException, status
from sqlmodel import Session, select, and_

from app.models.project import (
    Project, ProjectMember, ProjectRole, 
    ProjectDeliverable, ProjectTask, ProjectMilestone
)


class PermissionType(str, Enum):
    """Types de permissions disponibles."""
    # Permissions de base
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # Permissions spécifiques aux projets
    MANAGE_PROJECT = "manage_project"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_TASKS = "manage_tasks"
    MANAGE_MILESTONES = "manage_milestones"
    
    # Permissions pour les livrables
    VIEW_DELIVERABLES = "view_deliverables"
    SUBMIT_DELIVERABLES = "submit_deliverables"
    REVIEW_DELIVERABLES = "review_deliverables"
    APPROVE_DELIVERABLES = "approve_deliverables"
    
    # Permissions administratives
    ADMIN = "admin"


class ProjectPermissionService:
    """Service de gestion des permissions projet."""
    
    # Mapping des rôles vers les permissions
    ROLE_PERMISSIONS = {
        ProjectRole.VIEWER: [
            PermissionType.READ,
            PermissionType.VIEW_DELIVERABLES
        ],
        ProjectRole.CONTRIBUTOR: [
            PermissionType.READ,
            PermissionType.VIEW_DELIVERABLES,
            PermissionType.SUBMIT_DELIVERABLES
        ],
        ProjectRole.MEMBER: [
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.VIEW_DELIVERABLES,
            PermissionType.SUBMIT_DELIVERABLES,
            PermissionType.MANAGE_TASKS
        ],
        ProjectRole.LEAD: [
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.DELETE,
            PermissionType.VIEW_DELIVERABLES,
            PermissionType.SUBMIT_DELIVERABLES,
            PermissionType.REVIEW_DELIVERABLES,
            PermissionType.MANAGE_TASKS,
            PermissionType.MANAGE_MILESTONES
        ],
        ProjectRole.MANAGER: [
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.DELETE,
            PermissionType.MANAGE_PROJECT,
            PermissionType.MANAGE_MEMBERS,
            PermissionType.MANAGE_TASKS,
            PermissionType.MANAGE_MILESTONES,
            PermissionType.VIEW_DELIVERABLES,
            PermissionType.SUBMIT_DELIVERABLES,
            PermissionType.REVIEW_DELIVERABLES,
            PermissionType.APPROVE_DELIVERABLES
        ],
        ProjectRole.OWNER: [
            PermissionType.ADMIN,  # Toutes les permissions
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.DELETE,
            PermissionType.MANAGE_PROJECT,
            PermissionType.MANAGE_MEMBERS,
            PermissionType.MANAGE_TASKS,
            PermissionType.MANAGE_MILESTONES,
            PermissionType.VIEW_DELIVERABLES,
            PermissionType.SUBMIT_DELIVERABLES,
            PermissionType.REVIEW_DELIVERABLES,
            PermissionType.APPROVE_DELIVERABLES
        ]
    }
    
    @classmethod
    def get_user_project_role(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        session: Session
    ) -> Optional[ProjectRole]:
        """Récupère le rôle de l'utilisateur sur un projet."""
        
        query = select(ProjectMember.role).where(
            and_(
                ProjectMember.user_id == user_id,
                ProjectMember.project_id == project_id,
                ProjectMember.is_active == True
            )
        )
        
        result = session.exec(query).first()
        return result
    
    @classmethod
    def get_user_permissions(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        session: Session
    ) -> List[PermissionType]:
        """Récupère toutes les permissions de l'utilisateur sur un projet."""
        
        role = cls.get_user_project_role(user_id, project_id, session)
        if not role:
            return []
        
        return cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def has_permission(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        permission: PermissionType, 
        session: Session
    ) -> bool:
        """Vérifie si l'utilisateur a une permission spécifique."""
        
        permissions = cls.get_user_permissions(user_id, project_id, session)
        
        # Si l'utilisateur a ADMIN, il a toutes les permissions
        if PermissionType.ADMIN in permissions:
            return True
        
        return permission in permissions
    
    @classmethod
    def has_any_permission(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        permissions: List[PermissionType], 
        session: Session
    ) -> bool:
        """Vérifie si l'utilisateur a au moins une des permissions."""
        
        user_permissions = cls.get_user_permissions(user_id, project_id, session)
        
        # Si l'utilisateur a ADMIN, il a toutes les permissions
        if PermissionType.ADMIN in user_permissions:
            return True
        
        return any(perm in user_permissions for perm in permissions)
    
    @classmethod
    def has_all_permissions(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        permissions: List[PermissionType], 
        session: Session
    ) -> bool:
        """Vérifie si l'utilisateur a toutes les permissions."""
        
        user_permissions = cls.get_user_permissions(user_id, project_id, session)
        
        # Si l'utilisateur a ADMIN, il a toutes les permissions
        if PermissionType.ADMIN in user_permissions:
            return True
        
        return all(perm in user_permissions for perm in permissions)
    
    @classmethod
    def require_permission(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        permission: PermissionType, 
        session: Session,
        error_message: Optional[str] = None
    ):
        """Vérifie la permission et lève une exception si pas autorisé."""
        
        if not cls.has_permission(user_id, project_id, permission, session):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message or f"Permission '{permission.value}' required"
            )
    
    @classmethod
    def require_role(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        required_roles: List[ProjectRole], 
        session: Session,
        error_message: Optional[str] = None
    ):
        """Vérifie que l'utilisateur a l'un des rôles requis."""
        
        user_role = cls.get_user_project_role(user_id, project_id, session)
        
        if not user_role or user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message or f"One of these roles required: {[r.value for r in required_roles]}"
            )
    
    @classmethod
    def can_access_project(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        session: Session
    ) -> bool:
        """Vérifie si l'utilisateur peut accéder au projet."""
        
        # Vérifier si l'utilisateur est membre du projet
        query = select(ProjectMember).where(
            and_(
                ProjectMember.user_id == user_id,
                ProjectMember.project_id == project_id,
                ProjectMember.is_active == True
            )
        )
        
        member = session.exec(query).first()
        if member:
            return True
        
        # Vérifier si le projet est public
        query = select(Project.is_public).where(Project.id == project_id)
        is_public = session.exec(query).first()
        
        return bool(is_public)
    
    @classmethod
    def can_manage_deliverable(
        cls, 
        user_id: UUID, 
        deliverable_id: UUID, 
        action: str,
        session: Session
    ) -> bool:
        """Vérifie si l'utilisateur peut gérer un livrable."""
        
        # Récupérer le livrable et son projet
        query = select(ProjectDeliverable).where(ProjectDeliverable.id == deliverable_id)
        deliverable = session.exec(query).first()
        
        if not deliverable:
            return False
        
        project_id = deliverable.project_id
        
        # Vérifications selon l'action
        if action == "view":
            return cls.has_permission(user_id, project_id, PermissionType.VIEW_DELIVERABLES, session)
        
        elif action == "submit":
            # Seul le propriétaire peut soumettre
            return (deliverable.user_id == user_id and 
                   cls.has_permission(user_id, project_id, PermissionType.SUBMIT_DELIVERABLES, session))
        
        elif action == "review":
            return cls.has_permission(user_id, project_id, PermissionType.REVIEW_DELIVERABLES, session)
        
        elif action == "approve":
            return cls.has_permission(user_id, project_id, PermissionType.APPROVE_DELIVERABLES, session)
        
        elif action == "edit":
            # Propriétaire ou gestionnaire
            return (deliverable.user_id == user_id or 
                   cls.has_permission(user_id, project_id, PermissionType.MANAGE_PROJECT, session))
        
        elif action == "delete":
            # Propriétaire ou gestionnaire
            return (deliverable.user_id == user_id or 
                   cls.has_permission(user_id, project_id, PermissionType.MANAGE_PROJECT, session))
        
        return False
    
    @classmethod
    def get_accessible_projects(
        cls, 
        user_id: UUID, 
        session: Session
    ) -> List[UUID]:
        """Retourne la liste des projets accessibles par l'utilisateur."""
        
        # Projets où l'utilisateur est membre
        member_query = select(ProjectMember.project_id).where(
            and_(
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True
            )
        )
        member_projects = session.exec(member_query).all()
        
        # Projets publics
        public_query = select(Project.id).where(Project.is_public == True)
        public_projects = session.exec(public_query).all()
        
        # Combiner et dédupliquer
        all_projects = list(set(member_projects + public_projects))
        
        return all_projects
    
    @classmethod
    def get_user_project_summary(
        cls, 
        user_id: UUID, 
        project_id: UUID, 
        session: Session
    ) -> Dict[str, Any]:
        """Retourne un résumé des permissions de l'utilisateur sur un projet."""
        
        role = cls.get_user_project_role(user_id, project_id, session)
        permissions = cls.get_user_permissions(user_id, project_id, session)
        can_access = cls.can_access_project(user_id, project_id, session)
        
        return {
            "user_id": str(user_id),
            "project_id": str(project_id),
            "role": role.value if role else None,
            "permissions": [p.value for p in permissions],
            "can_access": can_access,
            "is_member": role is not None,
            "is_admin": PermissionType.ADMIN in permissions
        }


# Fonctions utilitaires publiques
async def check_project_permission(
    project_id: UUID,
    user_id: UUID,
    session: Session,
    permission: PermissionType = PermissionType.READ
):
    """Vérifie la permission sur un projet et lève une exception si refusée."""
    ProjectPermissionService.require_permission(
        user_id, project_id, permission, session
    )


async def has_project_access(
    project_id: UUID,
    user_id: UUID,
    session: Session,
    required_role: Optional[ProjectRole] = None
) -> bool:
    """Vérifie si l'utilisateur a accès au projet."""
    
    if required_role:
        try:
            ProjectPermissionService.require_role(
                user_id, project_id, [required_role], session
            )
            return True
        except HTTPException:
            return False
    
    return ProjectPermissionService.can_access_project(user_id, project_id, session)


async def get_accessible_projects(user_id: UUID, session: Session) -> List[UUID]:
    """Retourne la liste des projets accessibles par l'utilisateur."""
    return ProjectPermissionService.get_accessible_projects(user_id, session)


async def check_deliverable_permission(
    deliverable_id: UUID,
    user_id: UUID,
    action: str,
    session: Session
):
    """Vérifie la permission sur un livrable."""
    
    if not ProjectPermissionService.can_manage_deliverable(
        user_id, deliverable_id, action, session
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action '{action}' not permitted on this deliverable"
        )


# Service global
permission_service = ProjectPermissionService()