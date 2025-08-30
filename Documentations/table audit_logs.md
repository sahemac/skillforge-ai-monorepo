# ok je valide, si tel est donc le cas actualise la...

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de l'entrée de log. |
| actor_id | UUID | NULL, FOREIGN KEY REFERENCES users(id) | ID de l'utilisateur qui a effectué l'action (NULL si action système). |
| action_type | VARCHAR(100) | NOT NULL | Type d'action effectuée (ex: 'USER_BANNED', 'PROJECT_VALIDATED'). |
| target_entity | VARCHAR(100) | NULL | Entité cible de l'action (ex: 'USER', 'PROJECT'). |
| target_id | UUID | NULL | ID de l'entité cible. |
| details | JSONB | NULL | Objet JSON contenant des détails additionnels sur l'action. |
| timestamp | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp exact de l'action. |

