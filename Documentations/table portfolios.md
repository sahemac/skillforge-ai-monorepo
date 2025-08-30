# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du portfolio. |
| user_id | UUID | NOT NULL, UNIQUE, FOREIGN KEY REFERENCES users(id) | Apprenant propriétaire du portfolio. Contrainte UNIQUE pour la relation 1-to-1. |
| public_url_slug | VARCHAR(100) | NOT NULL, UNIQUE | Partie de l'URL lisible par l'homme (ex: "jean-dupont-ai"). |
| is_public | BOOLEAN | NOT NULL, DEFAULT false | Contrôle la visibilité publique du portfolio. |

