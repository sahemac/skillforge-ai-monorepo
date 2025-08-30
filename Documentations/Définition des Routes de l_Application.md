| Chemin (Path) | Composant Page Associé | Accès Requis | Description |
| --- | --- | --- | --- |
| Routes Publiques |  |  |  |
| / | HomePage.tsx | Public | Page d'accueil, redirige vers /login si non authentifié, ou /dashboard si authentifié. |
| /login | LoginPage.tsx | Public | Formulaire de connexion. |
| /register | RegisterPage.tsx | Public | Formulaire d'inscription pour les apprenants et les entreprises. |
| /password-reset | PasswordResetPage.tsx | Public | Formulaire pour demander la réinitialisation du mot de passe. |
| /portfolios/:publicUrl | PublicPortfolioPage.tsx | Public | Page d'affichage d'un portfolio public. |
|  |  |  |  |
| Routes Communes (Authentifié) |  |  |  |
| /settings | SettingsPage.tsx | Authentifié | Page de gestion des paramètres du compte (profil, mot de passe). |
|  |  |  |  |
| Parcours Apprenant |  |  |  |
| /dashboard | LearnerDashboardPage.tsx | Rôle: apprenant | Tableau de bord principal de l'apprenant. |
| /projects | ProjectListPage.tsx | Rôle: apprenant | Page de recherche et de consultation de la liste des projets disponibles. |
| /projects/:projectId | ProjectDetailPage.tsx | Rôle: apprenant | Page de détail d'un projet, avec gestion des jalons et soumission des livrables. |
| /my-portfolio | MyPortfolioEditPage.tsx | Rôle: apprenant | Interface de gestion et de prévisualisation de son propre portfolio. |
|  |  |  |  |
| Parcours Entreprise |  |  |  |
| /company/dashboard | CompanyDashboardPage.tsx | Rôle: entreprise | Tableau de bord principal de l'entreprise pour suivre ses projets. |
| /company/projects/new | NewProjectPage.tsx | Rôle: entreprise | Formulaire de création d'un nouveau projet. |
| /company/projects/:projectId | CompanyProjectDetailPage.tsx | Rôle: entreprise | Page de détail d'un projet soumis, avec suivi des livrables et des évaluations. |
|  |  |  |  |
| Parcours Administrateur |  |  |  |
| /admin/dashboard | AdminDashboardPage.tsx | Rôle: admin | Tableau de bord principal de l'administrateur. |
| /admin/users | AdminUserManagementPage.tsx | Rôle: admin | Interface de gestion des utilisateurs. |
| /admin/projects | AdminProjectManagementPage.tsx | Rôle: admin | Interface de gestion et de validation des projets. |
|  |  |  |  |
| Route Erreur |  |  |  |
| * | NotFoundPage.tsx | Public | Page affichée pour toute URL ne correspondant à aucune route définie. |

