# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de la conversation. |
| project_id | UUID | NOT NULL, FOREIGN KEY REFERENCES projects(id) | Projet auquel la conversation est rattachée. |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la création de la conversation. |

