# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de la compétence. |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Nom de la compétence (ex: 'Python', 'FastAPI'). |

