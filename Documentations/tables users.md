# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de l'utilisateur. |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Adresse e-mail de l'utilisateur, utilisée pour la connexion. |
| hashed_password | VARCHAR(255) | NOT NULL | Mot de passe de l'utilisateur après avoir été haché par bcrypt. |
| full_name | VARCHAR(255) | NOT NULL | Nom complet de l'utilisateur ou nom de la personne de contact. |
| role | user_role_enum | NOT NULL | Rôle de l'utilisateur dans la plateforme ('apprenant', 'entreprise', 'admin'). |
| avatar_url | TEXT | NULL | URL vers l'image de profil stockée sur GCS. |
| bio | TEXT | NULL | Courte biographie de l'utilisateur. |
| company_name | VARCHAR(255) | NULL | Nom de l'entreprise (uniquement pour le rôle 'entreprise'). |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Permet de désactiver un compte sans le supprimer (soft delete). |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la création du compte. |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la dernière mise à jour du compte. |

