# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de l'entrée du portfolio. |
| portfolio_id | UUID | NOT NULL, FOREIGN KEY REFERENCES portfolios(id) | Portfolio auquel cette entrée appartient. |
| project_id | UUID | NOT NULL, FOREIGN KEY REFERENCES projects(id) | Projet mis en avant. |
| summary | TEXT | NULL | Résumé du projet, généré par l'IA ou personnalisé. |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | Ordre d'affichage des projets dans le portfolio. |

