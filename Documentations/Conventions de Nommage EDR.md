# vas-y

| Type d'Objet | Convention | Justification | Exemple(s) |
| --- | --- | --- | --- |
| Tables | snake_case, au pluriel | Convention standard pour PostgreSQL, facilite la lecture et la distinction entre les tables et les autres objets. | users, projects, project_assignments |
| Colonnes | snake_case | Cohérence avec le nommage des tables. | first_name, created_at, project_title |
| Clés Primaires (PK) | Toujours nommées id | Standard simple et universel. Le type est toujours UUID. | id UUID PRIMARY KEY |
| Clés Étrangères (FK) | {nom_table_singulier}_id | Explicite et sans ambiguïté sur la table et la colonne référencées. | user_id, project_id, deliverable_id |
| Index | ix_{nom_table}_{nom_colonnes} | Le préfixe ix_ identifie immédiatement l'objet comme un index. Le reste du nom est descriptif. | ix_users_email, ix_messages_conversation_id |
| Contraintes d'Unicité | uq_{nom_table}_{nom_colonnes} | Le préfixe uq_ identifie immédiatement l'objet comme une contrainte d'unicité. | uq_users_email |
| Types Énumérés | {nom_table}_{nom_colonne}_enum | Permet d'identifier clairement à quelle colonne et quelle table le type est principalement associé. | project_status_enum |

