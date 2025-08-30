# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| portfolio_item_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES portfolio_items(id) | ID de l'entrée de portfolio. |
| skill_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES skills(id) | ID de la compétence associée. |

