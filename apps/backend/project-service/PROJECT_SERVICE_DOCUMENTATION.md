# Project Service - Documentation Complète

## 📌 Vue d'ensemble

Le **Project Service** est un microservice central de l'écosystème SkillForge AI qui gère l'intégralité du cycle de vie des projets d'apprentissage et de développement des compétences. Il permet aux entreprises et aux apprenants de créer, gérer et suivre des projets collaboratifs avec une granularité fine des permissions et un tracking complet.

## 🎯 Objectifs du Service

1. **Gestion centralisée des projets** : Création, modification, suppression et archivage
2. **Collaboration d'équipe** : Gestion des membres, rôles et permissions
3. **Suivi des tâches** : Système de tâches hiérarchiques avec dépendances
4. **Jalons et livrables** : Tracking des milestones et objectifs
5. **Budget et ressources** : Gestion financière et allocation des ressources
6. **Intégration écosystème** : Communication avec les autres services

## 🏗️ Architecture Technique

### Stack Technologique
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel/SQLAlchemy
- **Base de données**: PostgreSQL avec asyncpg
- **Cache**: Redis pour sessions et données fréquentes
- **Queue**: Celery pour tâches asynchrones
- **API**: RESTful avec documentation OpenAPI
- **Authentification**: JWT via user-service

### Structure du Service

```
project-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── projects.py
│   │       │   ├── members.py
│   │       │   ├── tasks.py
│   │       │   ├── milestones.py
│   │       │   ├── comments.py
│   │       │   └── attachments.py
│   │       └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── project.py
│   │   ├── member.py
│   │   ├── task.py
│   │   └── milestone.py
│   ├── schemas/
│   │   ├── project.py
│   │   ├── member.py
│   │   ├── task.py
│   │   └── milestone.py
│   ├── crud/
│   │   └── base.py
│   └── main.py
├── alembic/
├── tests/
├── requirements.txt
└── Dockerfile
```

## 📊 Modèles de Données

### 1. Project (Projet Principal)
```python
class Project(SQLModel, table=True):
    __tablename__ = "projects"
    
    # Identifiants
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(unique=True, index=True)
    
    # Description et métadonnées
    description: Optional[str]
    objectives: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Relations
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    created_by: UUID = Field(foreign_key="users.id", index=True)
    
    # Timeline
    start_date: datetime
    end_date: Optional[datetime]
    estimated_hours: Optional[int]
    actual_hours: int = Field(default=0)
    
    # Budget
    budget: Optional[Decimal] = Field(max_digits=12, decimal_places=2)
    spent: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR", max_length=3)
    
    # Statut
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM)
    visibility: ProjectVisibility = Field(default=ProjectVisibility.INTERNAL)
    
    # Progression
    progress: int = Field(default=0, ge=0, le=100)
    health_status: HealthStatus = Field(default=HealthStatus.ON_TRACK)
    
    # Métadonnées
    settings: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    metadata: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Audit
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime]
```

### 2. ProjectMember (Membres du Projet)
```python
class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_members"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    user_id: UUID = Field(index=True)
    
    # Rôle et permissions
    role: ProjectRole = Field(default=ProjectRole.MEMBER)
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Engagement
    allocation_percentage: int = Field(default=100, ge=0, le=100)
    hourly_rate: Optional[Decimal] = Field(max_digits=8, decimal_places=2)
    
    # Timeline
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime]
    
    # Statistiques
    tasks_assigned: int = Field(default=0)
    tasks_completed: int = Field(default=0)
    contribution_score: int = Field(default=0)
    
    # Statut
    is_active: bool = Field(default=True)
    last_activity: Optional[datetime]
```

### 3. ProjectTask (Tâches)
```python
class ProjectTask(SQLModel, table=True):
    __tablename__ = "project_tasks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    parent_task_id: Optional[UUID] = Field(foreign_key="project_tasks.id")
    
    # Informations de base
    title: str = Field(max_length=255, index=True)
    description: Optional[str]
    task_number: int  # Auto-incrementé par projet
    
    # Assignation
    assigned_to: Optional[UUID] = Field(index=True)
    assigned_by: UUID
    
    # Timeline
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Effort
    estimated_hours: Optional[float]
    actual_hours: float = Field(default=0)
    
    # Statut et priorité
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    
    # Dépendances
    dependencies: List[UUID] = Field(default_factory=list, sa_column=Column(JSON))
    blocks: List[UUID] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Labels et catégories
    labels: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    category: Optional[str]
    
    # Checklist
    checklist: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    progress: int = Field(default=0, ge=0, le=100)
    
    # Métadonnées
    attachments_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    watchers: List[UUID] = Field(default_factory=list, sa_column=Column(JSON))
```

### 4. ProjectMilestone (Jalons)
```python
class ProjectMilestone(SQLModel, table=True):
    __tablename__ = "project_milestones"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    
    # Informations
    title: str = Field(max_length=255)
    description: Optional[str]
    
    # Timeline
    target_date: datetime
    completed_at: Optional[datetime]
    
    # Critères de succès
    success_criteria: List[Dict] = Field(sa_column=Column(JSON))
    deliverables: List[Dict] = Field(sa_column=Column(JSON))
    
    # Budget
    budget_allocated: Optional[Decimal]
    budget_used: Decimal = Field(default=0)
    
    # Statut
    status: MilestoneStatus = Field(default=MilestoneStatus.PENDING)
    completion_percentage: int = Field(default=0, ge=0, le=100)
    
    # Risques
    risks: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
```

## 🔐 Système de Permissions

### Rôles Hiérarchiques

#### 1. **OWNER** (Propriétaire)
- Contrôle total du projet
- Peut supprimer le projet
- Peut transférer la propriété
- Gère les paramètres critiques

#### 2. **MANAGER** (Gestionnaire)
- Gère les membres et leurs rôles
- Modifie les paramètres du projet
- Approuve les jalons
- Accède aux données financières

#### 3. **LEAD** (Chef d'équipe)
- Assigne et réassigne les tâches
- Crée et modifie les jalons
- Gère les priorités
- Valide les livrables

#### 4. **MEMBER** (Membre)
- Crée et modifie ses propres tâches
- Commente sur toutes les tâches
- Voit toutes les informations du projet
- Met à jour le statut de ses tâches

#### 5. **CONTRIBUTOR** (Contributeur)
- Accès limité aux tâches assignées
- Peut commenter ses tâches
- Voit uniquement ses parties du projet

#### 6. **VIEWER** (Observateur)
- Accès en lecture seule
- Peut voir les informations publiques
- Pas de modification possible

### Matrice de Permissions

| Action | Owner | Manager | Lead | Member | Contributor | Viewer |
|--------|-------|---------|------|--------|-------------|---------|
| Voir projet | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Modifier projet | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Supprimer projet | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gérer membres | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer tâches | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| Assigner tâches | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Gérer budget | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Voir analytics | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

## 🎮 Cas d'Usage (Use Cases)

### 1. Entreprise - Formation Interne
**Scénario**: Une entreprise lance un projet de formation pour 50 employés

```python
# Création du projet
project = {
    "name": "Formation Python Avancé Q1 2024",
    "company_id": "acme-corp-id",
    "objectives": [
        "Former 50 développeurs au Python avancé",
        "Certification de 80% des participants",
        "Création de 10 projets internes"
    ],
    "budget": 50000,
    "start_date": "2024-01-15",
    "end_date": "2024-03-31"
}

# Ajout des membres
members = [
    {"user_id": "trainer-1", "role": "LEAD"},
    {"user_id": "dev-1", "role": "MEMBER"},
    # ... 48 autres développeurs
]

# Création des jalons
milestones = [
    {
        "title": "Module 1: Fondamentaux",
        "target_date": "2024-01-31",
        "success_criteria": ["90% présence", "Tests passés"]
    },
    {
        "title": "Module 2: Patterns Avancés",
        "target_date": "2024-02-29"
    },
    {
        "title": "Projets Finaux",
        "target_date": "2024-03-31"
    }
]
```

### 2. Freelance - Projet Client
**Scénario**: Un freelance gère un projet de développement web

```python
project = {
    "name": "Site E-commerce ClientX",
    "visibility": "PRIVATE",
    "budget": 15000,
    "objectives": [
        "Site responsive",
        "Intégration paiement",
        "Panel admin"
    ],
    "estimated_hours": 200
}

# Tâches avec dépendances
tasks = [
    {
        "title": "Design UI/UX",
        "estimated_hours": 40,
        "priority": "HIGH"
    },
    {
        "title": "Backend API",
        "estimated_hours": 60,
        "dependencies": ["design-task-id"]
    },
    {
        "title": "Frontend React",
        "estimated_hours": 50,
        "dependencies": ["backend-task-id"]
    }
]
```

### 3. École - Projet Étudiant
**Scénario**: Projet de fin d'études collaboratif

```python
project = {
    "name": "Application Mobile - Gestion Campus",
    "company_id": "university-id",
    "visibility": "PUBLIC",
    "tags": ["mobile", "flutter", "firebase"],
    "estimated_hours": 500
}

# Équipe étudiante
team = [
    {"user_id": "student-1", "role": "LEAD", "allocation": 100},
    {"user_id": "student-2", "role": "MEMBER", "allocation": 75},
    {"user_id": "student-3", "role": "MEMBER", "allocation": 75},
    {"user_id": "professor", "role": "MANAGER", "allocation": 10}
]

# Suivi hebdomadaire
weekly_tasks = [
    {"title": "Sprint Planning", "recurring": "WEEKLY"},
    {"title": "Code Review", "recurring": "WEEKLY"},
    {"title": "Demo Professor", "recurring": "BIWEEKLY"}
]
```

### 4. Startup - Développement Produit
**Scénario**: MVP pour une startup tech

```python
project = {
    "name": "MVP SaaS Platform v1.0",
    "priority": "CRITICAL",
    "health_status": "AT_RISK",
    "budget": 100000,
    "objectives": [
        "Launch MVP in 3 months",
        "1000 beta users",
        "Core features operational"
    ]
}

# Phases du projet
phases = [
    {
        "name": "Discovery",
        "tasks": ["Market Research", "User Interviews", "Tech Stack"],
        "duration_weeks": 2
    },
    {
        "name": "Development",
        "tasks": ["Backend", "Frontend", "Mobile", "Testing"],
        "duration_weeks": 8
    },
    {
        "name": "Launch",
        "tasks": ["Marketing", "Onboarding", "Support"],
        "duration_weeks": 2
    }
]
```

## 📡 API Endpoints

### Projects
```yaml
GET    /api/v1/projects                 # Liste des projets (avec filtres)
POST   /api/v1/projects                 # Créer un projet
GET    /api/v1/projects/{id}            # Détails d'un projet
PUT    /api/v1/projects/{id}            # Modifier un projet
DELETE /api/v1/projects/{id}            # Supprimer un projet
POST   /api/v1/projects/{id}/archive    # Archiver un projet
POST   /api/v1/projects/{id}/duplicate  # Dupliquer un projet
GET    /api/v1/projects/{id}/stats      # Statistiques du projet
```

### Members
```yaml
GET    /api/v1/projects/{id}/members           # Liste des membres
POST   /api/v1/projects/{id}/members           # Ajouter un membre
PUT    /api/v1/projects/{id}/members/{user_id} # Modifier rôle/permissions
DELETE /api/v1/projects/{id}/members/{user_id} # Retirer un membre
POST   /api/v1/projects/{id}/invite            # Inviter par email
```

### Tasks
```yaml
GET    /api/v1/projects/{id}/tasks             # Liste des tâches
POST   /api/v1/projects/{id}/tasks             # Créer une tâche
GET    /api/v1/tasks/{id}                      # Détails d'une tâche
PUT    /api/v1/tasks/{id}                      # Modifier une tâche
DELETE /api/v1/tasks/{id}                      # Supprimer une tâche
POST   /api/v1/tasks/{id}/assign               # Assigner la tâche
POST   /api/v1/tasks/{id}/complete             # Marquer comme complète
GET    /api/v1/tasks/{id}/time-entries         # Temps passé
```

### Milestones
```yaml
GET    /api/v1/projects/{id}/milestones        # Liste des jalons
POST   /api/v1/projects/{id}/milestones        # Créer un jalon
PUT    /api/v1/milestones/{id}                 # Modifier un jalon
DELETE /api/v1/milestones/{id}                 # Supprimer un jalon
POST   /api/v1/milestones/{id}/complete        # Marquer comme atteint
```

## 📈 Métriques et KPIs

### Métriques Projet
- **Completion Rate**: Pourcentage de tâches complétées
- **Velocity**: Tâches complétées par sprint
- **Budget Burn Rate**: Dépense vs budget prévu
- **Time Variance**: Temps réel vs estimé
- **Team Productivity**: Output par membre

### Métriques Équipe
- **Member Engagement**: Activité par membre
- **Task Distribution**: Répartition des tâches
- **Skill Coverage**: Compétences couvertes
- **Communication Index**: Nombre de commentaires/interactions

### Métriques Qualité
- **Defect Rate**: Bugs par livrable
- **Rework Percentage**: Tâches à refaire
- **Client Satisfaction**: Score de satisfaction
- **Delivery Accuracy**: Respect des deadlines

## 🔄 Intégrations

### Services Internes
1. **User Service**: Authentification et profils
2. **Company Service**: Données entreprise
3. **Notification Service**: Alertes et notifications
4. **Analytics Service**: Rapports et dashboards
5. **Storage Service**: Fichiers et documents
6. **Chat Service**: Communication temps réel

### Services Externes
1. **Slack/Teams**: Notifications
2. **GitHub/GitLab**: Synchronisation code
3. **Jira/Trello**: Import/Export
4. **Google Calendar**: Synchronisation événements
5. **Stripe**: Facturation projets

## 🚀 Roadmap Évolution

### Phase 1 (Q1 2024) - Foundation
- ✅ CRUD complet projets
- ✅ Système de permissions
- ✅ Gestion des tâches
- ✅ API REST documentée

### Phase 2 (Q2 2024) - Collaboration
- ⏳ Temps réel (WebSockets)
- ⏳ Commentaires threadés
- ⏳ Notifications push
- ⏳ Mentions @user

### Phase 3 (Q3 2024) - Intelligence
- 📅 IA pour estimation temps
- 📅 Suggestions d'assignation
- 📅 Détection risques projet
- 📅 Optimisation ressources

### Phase 4 (Q4 2024) - Scale
- 📅 Multi-tenancy complet
- 📅 Sharding base de données
- 📅 Cache distribué
- 📅 API GraphQL

## 🛡️ Sécurité

### Mesures Implémentées
- **Authentication**: JWT avec refresh tokens
- **Authorization**: RBAC (Role-Based Access Control)
- **Encryption**: Données sensibles chiffrées (AES-256)
- **Audit Trail**: Logs de toutes les actions
- **Rate Limiting**: Protection contre abus
- **Input Validation**: Sanitization stricte
- **SQL Injection**: Requêtes paramétrées
- **XSS Protection**: Content Security Policy

### Conformité
- **RGPD**: Droit à l'oubli, portabilité
- **ISO 27001**: Standards sécurité
- **SOC 2**: Audit de sécurité

## 📚 Documentation Technique

### Installation Locale
```bash
# Clone repository
git clone https://github.com/skillforge/project-service
cd project-service

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Dépendances
pip install -r requirements.txt

# Variables environnement
cp .env.example .env
# Éditer .env avec vos configs

# Migrations base de données
alembic upgrade head

# Lancer le service
uvicorn app.main:app --reload --port 8003
```

### Tests
```bash
# Tests unitaires
pytest tests/unit -v

# Tests intégration
pytest tests/integration -v

# Coverage
pytest --cov=app --cov-report=html

# Tests de charge
locust -f tests/load/locustfile.py
```

### Déploiement Production
```bash
# Build Docker
docker build -t project-service:latest .

# Push to registry
docker tag project-service:latest gcr.io/skillforge/project-service:v1.0.0
docker push gcr.io/skillforge/project-service:v1.0.0

# Deploy to Cloud Run
gcloud run deploy project-service \
  --image gcr.io/skillforge/project-service:v1.0.0 \
  --platform managed \
  --region europe-west1
```

## 📞 Support et Contact

- **Documentation API**: https://api.skillforge.ai/project-service/docs
- **Issues GitHub**: https://github.com/skillforge/project-service/issues
- **Email Support**: support@skillforge.ai
- **Slack Channel**: #project-service

## 📄 Licence

Copyright © 2024 SkillForge AI. Tous droits réservés.

---

*Document généré le : 2025-09-23*
*Version : 1.0.0*
*Auteur : Architecture Team - SkillForge AI*