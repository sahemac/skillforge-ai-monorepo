# ok je valide, si tel est donc le cas actualise la...

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du livrable. |
| project_id | UUID | NOT NULL, FOREIGN KEY REFERENCES projects(id) | Projet pour lequel ce livrable est soumis. |
| user_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) | Apprenant qui a soumis le livrable. |
| type | deliverable_type_enum | NOT NULL | (Ajout) Type de livrable ('FILE_UPLOAD', 'GIT_REPO_URL', 'EXTERNAL_URL'). |
| file_path_or_url | TEXT | NOT NULL | Chemin vers le fichier sur GCS ou URL du dépôt/lien. |
| notes | TEXT | NULL | Notes optionnelles de l'apprenant sur sa soumission. |
| submitted_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la soumission. |

