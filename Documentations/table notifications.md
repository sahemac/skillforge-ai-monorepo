# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de la notification. |
| user_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) | Utilisateur destinataire de la notification. |
| content | TEXT | NOT NULL | Texte de la notification. |
| status | notification_status_enum | NOT NULL, DEFAULT 'UNREAD' | Statut de la notification (lue ou non lue). |
| link_url | TEXT | NULL | URL de redirection lorsque l'utilisateur clique sur la notification. |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la création de la notification. |

