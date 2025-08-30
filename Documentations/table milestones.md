# ok je valide, si tel est donc le cas actualise la...

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du jalon. |
| project_id | UUID | NOT NULL, FOREIGN KEY REFERENCES projects(id) | Projet auquel ce jalon appartient. |
| title | VARCHAR(255) | NOT NULL | Titre du jalon (ex: "Étape 1: Analyse des données"). |
| description | TEXT | NULL | Description détaillée de ce qui est attendu pour ce jalon. |
| due_date | TIMESTAMPTZ | NULL | Date d'échéance indicative pour ce jalon. |
| status | milestone_status_enum | NOT NULL, DEFAULT 'PENDING' | Statut du jalon (ex: 'PENDING', 'COMPLETED'). |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | Ordre d'affichage des jalons dans un projet. |

