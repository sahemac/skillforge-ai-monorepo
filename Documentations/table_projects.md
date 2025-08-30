# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du projet. |
| owner_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) | ID de l'utilisateur (entreprise) propriétaire du projet. |
| title | VARCHAR(255) | NOT NULL | Titre du projet. |
| description | TEXT | NOT NULL | Description complète et brief du projet. |
| status | project_status_enum | NOT NULL, DEFAULT 'DRAFT' | Statut actuel du projet. |
| embedding | vector(384) | NULL | Vecteur sémantique de la description pour la recherche de similarité. |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la création du projet. |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la dernière mise à jour. |
| completed_at | TIMESTAMPTZ | NULL | Timestamp de la complétion du projet. |

