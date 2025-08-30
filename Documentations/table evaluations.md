# vas y

| Nom de la Colonne | Type de Données | Contraintes | Description |
| --- | --- | --- | --- |
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Identifiant unique de l'évaluation. |
| deliverable_id | UUID | NOT NULL, UNIQUE, FOREIGN KEY REFERENCES deliverables(id) | Livrable évalué. La contrainte UNIQUE garantit la relation 1-to-1. |
| overall_score | NUMERIC(4, 2) | NOT NULL | Note globale sur 10.00, avec 2 décimales. |
| feedback_data | JSONB | NOT NULL | Objet JSON contenant l'évaluation détaillée (forces, faiblesses, etc.). |
| evaluated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Timestamp de la fin de l'évaluation. |

