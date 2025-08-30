# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique du message. |
| conversation_id | UUID | NOT NULL, FOREIGN KEY REFERENCES conversations(id) | Conversation à laquelle le message appartient. |
| sender_id | UUID | NOT NULL, FOREIGN KEY REFERENCES users(id) | Utilisateur qui a envoyé le message. |
| content | TEXT | NOT NULL | Contenu textuel du message. |
| attachment_url | TEXT | NULL | URL vers une éventuelle pièce jointe sur GCS. |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de l'envoi du message. |

