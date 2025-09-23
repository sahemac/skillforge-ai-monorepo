-- ===================================================================
-- SkillForge AI - Project Service Database Schema
-- Version: 1.0.0
-- Generated: 2025-09-23
-- ===================================================================

-- Extensions PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Énumérations (Types ENUM)
DO $$ BEGIN
    -- Statuts des projets
    CREATE TYPE project_status AS ENUM (
        'draft', 'planning', 'active', 'on_hold', 
        'completed', 'cancelled', 'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Priorités des projets
    CREATE TYPE project_priority AS ENUM (
        'low', 'medium', 'high', 'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Visibilité des projets
    CREATE TYPE project_visibility AS ENUM (
        'public', 'internal', 'private'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- État de santé du projet
    CREATE TYPE health_status AS ENUM (
        'on_track', 'at_risk', 'delayed', 'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Rôles dans les projets
    CREATE TYPE project_role AS ENUM (
        'owner', 'manager', 'lead', 'member', 'contributor', 'viewer'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Statuts des tâches
    CREATE TYPE task_status AS ENUM (
        'todo', 'in_progress', 'review', 'done', 'blocked', 'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Priorités des tâches
    CREATE TYPE task_priority AS ENUM (
        'lowest', 'low', 'medium', 'high', 'highest'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Statuts des jalons
    CREATE TYPE milestone_status AS ENUM (
        'pending', 'in_progress', 'completed', 'delayed', 'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Niveau de risque
    CREATE TYPE risk_level AS ENUM (
        'low', 'medium', 'high', 'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ===================================================================
-- Table principale : PROJECTS
-- ===================================================================
CREATE TABLE IF NOT EXISTS projects (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    
    -- Description et métadonnées
    description TEXT,
    objectives JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    
    -- Relations externes
    company_id UUID NOT NULL,  -- Référence vers company-service
    created_by UUID NOT NULL,  -- Référence vers user-service
    
    -- Timeline
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    estimated_hours INTEGER,
    actual_hours INTEGER DEFAULT 0,
    
    -- Budget
    budget DECIMAL(12,2),
    spent DECIMAL(12,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Statut
    status project_status DEFAULT 'draft',
    priority project_priority DEFAULT 'medium',
    visibility project_visibility DEFAULT 'internal',
    
    -- Progression
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    health_status health_status DEFAULT 'on_track',
    
    -- Configuration
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Audit trail
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- Contraintes
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date),
    CONSTRAINT valid_budget CHECK (budget IS NULL OR budget >= 0),
    CONSTRAINT valid_spent CHECK (spent >= 0)
);

-- ===================================================================
-- Table : PROJECT_MEMBERS (Membres du projet)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_members (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,  -- Référence vers user-service
    
    -- Rôle et permissions
    role project_role DEFAULT 'member',
    permissions JSONB DEFAULT '[]',
    
    -- Engagement
    allocation_percentage INTEGER DEFAULT 100 CHECK (allocation_percentage >= 0 AND allocation_percentage <= 100),
    hourly_rate DECIMAL(8,2),
    
    -- Timeline
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    
    -- Statistiques
    tasks_assigned INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    contribution_score INTEGER DEFAULT 0,
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMPTZ,
    
    -- Métadonnées
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Contraintes
    UNIQUE(project_id, user_id),
    CHECK (left_at IS NULL OR left_at >= joined_at)
);

-- ===================================================================
-- Table : PROJECT_TASKS (Tâches du projet)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_tasks (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES project_tasks(id) ON DELETE SET NULL,
    
    -- Informations de base
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_number INTEGER NOT NULL,  -- Auto-incrementé par projet
    
    -- Assignation
    assigned_to UUID,  -- Référence vers user-service
    assigned_by UUID NOT NULL,
    
    -- Timeline
    start_date TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Effort
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2) DEFAULT 0.00,
    
    -- Statut et priorité
    status task_status DEFAULT 'todo',
    priority task_priority DEFAULT 'medium',
    
    -- Relations
    dependencies JSONB DEFAULT '[]',  -- Array of task UUIDs
    blocks JSONB DEFAULT '[]',        -- Array of task UUIDs blocked by this task
    
    -- Catégorisation
    labels JSONB DEFAULT '[]',
    category VARCHAR(100),
    
    -- Checklist et progression
    checklist JSONB DEFAULT '[]',
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- Métadonnées
    attachments_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    watchers JSONB DEFAULT '[]',  -- Array of user UUIDs
    
    -- Audit
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- Contraintes
    UNIQUE(project_id, task_number),
    CHECK (due_date IS NULL OR start_date IS NULL OR due_date >= start_date),
    CHECK (completed_at IS NULL OR completed_at >= created_at),
    CHECK (estimated_hours IS NULL OR estimated_hours >= 0),
    CHECK (actual_hours >= 0)
);

-- ===================================================================
-- Table : PROJECT_MILESTONES (Jalons du projet)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_milestones (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Informations
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Timeline
    target_date TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    
    -- Critères et livrables
    success_criteria JSONB DEFAULT '[]',
    deliverables JSONB DEFAULT '[]',
    
    -- Budget
    budget_allocated DECIMAL(10,2),
    budget_used DECIMAL(10,2) DEFAULT 0.00,
    
    -- Statut
    status milestone_status DEFAULT 'pending',
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    
    -- Gestion des risques
    risks JSONB DEFAULT '[]',
    risk_level risk_level DEFAULT 'low',
    
    -- Audit
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes
    CHECK (completed_at IS NULL OR completed_at >= created_at),
    CHECK (target_date >= created_at),
    CHECK (budget_allocated IS NULL OR budget_allocated >= 0),
    CHECK (budget_used >= 0)
);

-- ===================================================================
-- Table : PROJECT_COMMENTS (Commentaires)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_comments (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id UUID REFERENCES project_tasks(id) ON DELETE CASCADE,
    milestone_id UUID REFERENCES project_milestones(id) ON DELETE CASCADE,
    parent_comment_id UUID REFERENCES project_comments(id) ON DELETE CASCADE,
    
    -- Contenu
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text', -- text, markdown, html
    
    -- Auteur
    author_id UUID NOT NULL,  -- Référence vers user-service
    
    -- Mentions et notifications
    mentions JSONB DEFAULT '[]',  -- Array of mentioned user UUIDs
    
    -- Statut
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes
    CHECK (
        (task_id IS NOT NULL AND milestone_id IS NULL) OR
        (task_id IS NULL AND milestone_id IS NOT NULL) OR
        (task_id IS NULL AND milestone_id IS NULL)  -- Commentaire général sur le projet
    )
);

-- ===================================================================
-- Table : PROJECT_ATTACHMENTS (Fichiers joints)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_attachments (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id UUID REFERENCES project_tasks(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES project_comments(id) ON DELETE CASCADE,
    
    -- Informations fichier
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64),  -- SHA-256 for deduplication
    
    -- Métadonnées
    description TEXT,
    tags JSONB DEFAULT '[]',
    
    -- Upload info
    uploaded_by UUID NOT NULL,  -- Référence vers user-service
    storage_provider VARCHAR(50) DEFAULT 'gcs',  -- gcs, s3, local
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes
    CHECK (file_size > 0),
    CHECK (
        (task_id IS NOT NULL AND comment_id IS NULL) OR
        (task_id IS NULL AND comment_id IS NOT NULL) OR
        (task_id IS NULL AND comment_id IS NULL)  -- Fichier général du projet
    )
);

-- ===================================================================
-- Table : PROJECT_TIME_ENTRIES (Suivi du temps)
-- ===================================================================
CREATE TABLE IF NOT EXISTS project_time_entries (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id UUID REFERENCES project_tasks(id) ON DELETE SET NULL,
    user_id UUID NOT NULL,  -- Référence vers user-service
    
    -- Temps
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER,  -- Calculé automatiquement
    
    -- Description
    description TEXT,
    activity_type VARCHAR(50),  -- development, meeting, review, etc.
    
    -- Facturation
    is_billable BOOLEAN DEFAULT TRUE,
    hourly_rate DECIMAL(8,2),
    
    -- Statut
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes
    CHECK (end_time IS NULL OR end_time > start_time),
    CHECK (duration_minutes IS NULL OR duration_minutes > 0)
);

-- ===================================================================
-- INDEXES pour optimisation des performances
-- ===================================================================

-- Projects
CREATE INDEX IF NOT EXISTS idx_projects_company_id ON projects(company_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority);
CREATE INDEX IF NOT EXISTS idx_projects_health_status ON projects(health_status);
CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_projects_company_status ON projects(company_id, status);
CREATE INDEX IF NOT EXISTS idx_projects_company_active ON projects(company_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_projects_dates ON projects(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_projects_search ON projects USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Project Members
CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON project_members(project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_user_id ON project_members(user_id);
CREATE INDEX IF NOT EXISTS idx_project_members_role ON project_members(role);
CREATE INDEX IF NOT EXISTS idx_project_members_active ON project_members(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_project_members_user_projects ON project_members(user_id, project_id) WHERE is_active = TRUE;

-- Project Tasks
CREATE INDEX IF NOT EXISTS idx_project_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_assigned_to ON project_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_project_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_project_tasks_priority ON project_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_project_tasks_parent ON project_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_due_date ON project_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_project_tasks_project_status ON project_tasks(project_id, status);
CREATE INDEX IF NOT EXISTS idx_project_tasks_assigned_status ON project_tasks(assigned_to, status) WHERE assigned_to IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_project_tasks_active ON project_tasks(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_project_tasks_search ON project_tasks USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Project Milestones
CREATE INDEX IF NOT EXISTS idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX IF NOT EXISTS idx_project_milestones_status ON project_milestones(status);
CREATE INDEX IF NOT EXISTS idx_project_milestones_target_date ON project_milestones(target_date);
CREATE INDEX IF NOT EXISTS idx_project_milestones_project_date ON project_milestones(project_id, target_date);

-- Project Comments
CREATE INDEX IF NOT EXISTS idx_project_comments_project_id ON project_comments(project_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_task_id ON project_comments(task_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_milestone_id ON project_comments(milestone_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_author ON project_comments(author_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_parent ON project_comments(parent_comment_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_created ON project_comments(created_at DESC);

-- Project Attachments
CREATE INDEX IF NOT EXISTS idx_project_attachments_project_id ON project_attachments(project_id);
CREATE INDEX IF NOT EXISTS idx_project_attachments_task_id ON project_attachments(task_id);
CREATE INDEX IF NOT EXISTS idx_project_attachments_hash ON project_attachments(file_hash);
CREATE INDEX IF NOT EXISTS idx_project_attachments_uploader ON project_attachments(uploaded_by);

-- Project Time Entries
CREATE INDEX IF NOT EXISTS idx_time_entries_project_id ON project_time_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_time_entries_task_id ON project_time_entries(task_id);
CREATE INDEX IF NOT EXISTS idx_time_entries_user_id ON project_time_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_time_entries_start_time ON project_time_entries(start_time);
CREATE INDEX IF NOT EXISTS idx_time_entries_user_date ON project_time_entries(user_id, start_time::date);
CREATE INDEX IF NOT EXISTS idx_time_entries_billable ON project_time_entries(is_billable, is_approved);

-- ===================================================================
-- TRIGGERS pour audit et business logic
-- ===================================================================

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Application des triggers updated_at
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_tasks_updated_at BEFORE UPDATE ON project_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_comments_updated_at BEFORE UPDATE ON project_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_time_entries_updated_at BEFORE UPDATE ON project_time_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour calculer la durée des time entries
CREATE OR REPLACE FUNCTION calculate_time_entry_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.start_time IS NOT NULL AND NEW.end_time IS NOT NULL THEN
        NEW.duration_minutes = EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time)) / 60;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_duration_trigger 
    BEFORE INSERT OR UPDATE ON project_time_entries 
    FOR EACH ROW EXECUTE FUNCTION calculate_time_entry_duration();

-- Trigger pour mettre à jour les statistiques des membres
CREATE OR REPLACE FUNCTION update_member_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Mise à jour des stats lors de changement de statut de tâche
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        -- Si la tâche passe à "done", incrémenter tasks_completed
        IF NEW.status = 'done' AND OLD.status != 'done' THEN
            UPDATE project_members 
            SET tasks_completed = tasks_completed + 1,
                last_activity = NOW()
            WHERE project_id = NEW.project_id 
            AND user_id = NEW.assigned_to;
        END IF;
        
        -- Si la tâche n'est plus "done", décrémenter tasks_completed
        IF OLD.status = 'done' AND NEW.status != 'done' THEN
            UPDATE project_members 
            SET tasks_completed = GREATEST(tasks_completed - 1, 0),
                last_activity = NOW()
            WHERE project_id = NEW.project_id 
            AND user_id = NEW.assigned_to;
        END IF;
    END IF;
    
    -- Lors de l'assignation d'une tâche
    IF TG_OP = 'UPDATE' AND (OLD.assigned_to IS NULL OR OLD.assigned_to != NEW.assigned_to) AND NEW.assigned_to IS NOT NULL THEN
        UPDATE project_members 
        SET tasks_assigned = tasks_assigned + 1,
            last_activity = NOW()
        WHERE project_id = NEW.project_id 
        AND user_id = NEW.assigned_to;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_member_stats_trigger 
    AFTER UPDATE ON project_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_member_stats();

-- ===================================================================
-- VUES pour les requêtes fréquentes
-- ===================================================================

-- Vue pour les projets avec statistiques
CREATE OR REPLACE VIEW project_stats AS
SELECT 
    p.id,
    p.name,
    p.status,
    p.priority,
    p.progress,
    p.health_status,
    p.start_date,
    p.end_date,
    p.budget,
    p.spent,
    p.company_id,
    p.created_by,
    
    -- Statistiques des tâches
    COUNT(pt.id) as total_tasks,
    COUNT(pt.id) FILTER (WHERE pt.status = 'done') as completed_tasks,
    COUNT(pt.id) FILTER (WHERE pt.status = 'in_progress') as in_progress_tasks,
    COUNT(pt.id) FILTER (WHERE pt.status = 'blocked') as blocked_tasks,
    
    -- Statistiques des membres
    COUNT(DISTINCT pm.user_id) FILTER (WHERE pm.is_active = true) as active_members,
    
    -- Statistiques temporelles
    COALESCE(SUM(pt.actual_hours), 0) as total_hours_logged,
    COALESCE(SUM(pt.estimated_hours), 0) as total_hours_estimated,
    
    -- Jalons
    COUNT(pms.id) as total_milestones,
    COUNT(pms.id) FILTER (WHERE pms.status = 'completed') as completed_milestones,
    
    p.created_at,
    p.updated_at
FROM projects p
LEFT JOIN project_tasks pt ON p.id = pt.project_id AND pt.is_active = true
LEFT JOIN project_members pm ON p.id = pm.project_id
LEFT JOIN project_milestones pms ON p.id = pms.project_id AND pms.is_active = true
WHERE p.is_active = true
GROUP BY p.id;

-- Vue pour les tâches avec détails
CREATE OR REPLACE VIEW task_details AS
SELECT 
    pt.id,
    pt.title,
    pt.description,
    pt.task_number,
    pt.status,
    pt.priority,
    pt.progress,
    pt.assigned_to,
    pt.assigned_by,
    pt.start_date,
    pt.due_date,
    pt.completed_at,
    pt.estimated_hours,
    pt.actual_hours,
    pt.project_id,
    pt.parent_task_id,
    
    -- Projet associé
    p.name as project_name,
    p.status as project_status,
    
    -- Statistiques
    pt.comments_count,
    pt.attachments_count,
    
    -- Calculs
    CASE 
        WHEN pt.due_date IS NOT NULL AND pt.due_date < NOW() AND pt.status NOT IN ('done', 'cancelled')
        THEN true 
        ELSE false 
    END as is_overdue,
    
    CASE 
        WHEN pt.estimated_hours IS NOT NULL AND pt.estimated_hours > 0
        THEN (pt.actual_hours / pt.estimated_hours) * 100
        ELSE NULL
    END as time_efficiency_percentage,
    
    pt.created_at,
    pt.updated_at
FROM project_tasks pt
JOIN projects p ON pt.project_id = p.id
WHERE pt.is_active = true AND p.is_active = true;

-- ===================================================================
-- PERMISSIONS ET SÉCURITÉ
-- ===================================================================

-- Fonction pour vérifier les permissions
CREATE OR REPLACE FUNCTION check_project_permission(
    user_uuid UUID,
    proj_id UUID,
    required_permission VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    user_role project_role;
    user_permissions JSONB;
BEGIN
    -- Récupérer le rôle et permissions de l'utilisateur
    SELECT role, permissions INTO user_role, user_permissions
    FROM project_members 
    WHERE project_id = proj_id 
    AND user_id = user_uuid 
    AND is_active = true;
    
    -- Si pas membre du projet
    IF user_role IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Vérifications par rôle
    CASE user_role
        WHEN 'owner' THEN RETURN TRUE;  -- Owner a tous les droits
        WHEN 'manager' THEN 
            RETURN required_permission IN ('read', 'write', 'manage_members', 'manage_budget');
        WHEN 'lead' THEN 
            RETURN required_permission IN ('read', 'write', 'assign_tasks', 'manage_milestones');
        WHEN 'member' THEN 
            RETURN required_permission IN ('read', 'write', 'comment');
        WHEN 'contributor' THEN 
            RETURN required_permission IN ('read', 'comment');
        WHEN 'viewer' THEN 
            RETURN required_permission = 'read';
        ELSE 
            RETURN FALSE;
    END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================================================
-- DONNÉES D'EXEMPLE (à supprimer en production)
-- ===================================================================

-- Insertion de données de test (commentée pour production)
/*
-- Projet exemple
INSERT INTO projects (id, name, slug, description, company_id, created_by, start_date, end_date, budget) 
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Formation Python Avancé Q1 2024',
    'formation-python-q1-2024',
    'Formation intensive Python pour les développeurs de l''équipe',
    '550e8400-e29b-41d4-a716-446655440001', -- company_id
    '550e8400-e29b-41d4-a716-446655440002', -- created_by
    '2024-01-15 09:00:00+00',
    '2024-03-31 17:00:00+00',
    50000.00
);

-- Membres du projet exemple
INSERT INTO project_members (project_id, user_id, role, allocation_percentage)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440002', 'owner', 50),
    ('550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440003', 'lead', 100),
    ('550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440004', 'member', 75);
*/

-- ===================================================================
-- FIN DU SCHÉMA
-- ===================================================================

-- Commentaires finaux
COMMENT ON DATABASE current_database() IS 'SkillForge AI - Project Service Database';
COMMENT ON TABLE projects IS 'Table principale des projets avec toutes leurs métadonnées';
COMMENT ON TABLE project_members IS 'Membres des projets avec leurs rôles et permissions';
COMMENT ON TABLE project_tasks IS 'Tâches des projets avec hiérarchie et dépendances';
COMMENT ON TABLE project_milestones IS 'Jalons et livrables des projets';
COMMENT ON TABLE project_comments IS 'Système de commentaires threadés';
COMMENT ON TABLE project_attachments IS 'Fichiers joints aux projets et tâches';
COMMENT ON TABLE project_time_entries IS 'Suivi du temps passé sur les projets et tâches';

-- Analyse et optimisation
ANALYZE projects;
ANALYZE project_members;
ANALYZE project_tasks;
ANALYZE project_milestones;
ANALYZE project_comments;
ANALYZE project_attachments;
ANALYZE project_time_entries;