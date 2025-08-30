# ok je valide, si tel est donc le cas actualise la...

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du profil entreprise. |
| user_id | UUID | NOT NULL, UNIQUE, FOREIGN KEY REFERENCES users(id) | Utilisateur (personne de contact) associé à cette entreprise. |
| website_url | TEXT | NULL | URL du site web de l'entreprise. |
| siret_number | VARCHAR(14) | NULL | Numéro SIRET pour la vérification (marché français). |
| address | TEXT | NULL | Adresse postale de l'entreprise. |
| validation_status | company_validation_status_enum | NOT NULL, DEFAULT 'PENDING' | Statut de la validation du compte par les admins. |

