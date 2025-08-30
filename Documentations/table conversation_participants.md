# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| conversation_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES conversations(id) | ID de la conversation. |
| user_id | UUID | PRIMARY KEY, FOREIGN KEY REFERENCES users(id) | ID de l'utilisateur participant. |

