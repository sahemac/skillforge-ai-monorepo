| Nom du Topic (Canal) | Service Émetteur | Services Consommateurs | Description du Payload JSON |
| --- | --- | --- | --- |
| user.account.created | user-service | notification-service | { "user_id": "uuid", "email": "string", "full_name": "string", "role": "string" }. Envoyé pour déclencher l'e-mail de bienvenue. |
| user.password.reset_requested | user-service | notification-service | { "user_id": "uuid", "email": "string", "reset_token": "string" }. Envoyé pour déclencher l'e-mail avec le lien de réinitialisation. |
| project.project.submitted | project-service | notification-service | { "project_id": "uuid", "project_title": "string", "company_name": "string" }. Envoyé pour notifier les administrateurs qu'un nouveau projet est en attente de validation. |
| project.deliverable.submitted | project-service | evaluation-agent, notification-service | { "deliverable_id": "uuid", "project_id": "uuid", "user_id": "uuid", "file_path_in_gcs": "string" }. L'événement principal qui déclenche le pipeline d'évaluation et notifie l'entreprise. |
| evaluation.result.generated | evaluation-service | notification-service, portfolio-agent | { "evaluation_id": "uuid", "deliverable_id": "uuid", "user_id": "uuid", "project_id": "uuid", "overall_score": "float" }. Indique qu'une évaluation est terminée et prête à être consultée. Déclenche la notification à l'apprenant et potentiellement une mise à jour du portfolio. |
| messaging.message.received | messaging-service | notification-service | { "message_id": "uuid", "conversation_id": "uuid", "sender_id": "uuid", "recipient_id": "uuid", "project_id": "uuid" }. Permet de notifier un utilisateur qu'il a reçu un nouveau message. |

