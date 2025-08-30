# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| project_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES projects(id) | ID du projet. |
| skill_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES skills(id) | ID de la compétence. |

