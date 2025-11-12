# SkillForge AI - Shell Application

L'application Shell est le conteneur principal du frontend SkillForge AI, utilisant une **architecture monolithique modulaire** avec code splitting.

## 🏗️ Architecture

### Structure des Modules

```
apps/frontend/shell/src/
├── modules/                    # Modules métier
│   ├── auth/                   # Module d'authentification
│   │   ├── pages/              # LoginPage, RegisterPage, ForgotPasswordPage
│   │   ├── components/         # RegisterForm
│   │   ├── hooks/              # useLogin, useRegister, usePasswordReset
│   │   └── index.ts
│   ├── learner/                # Module apprenant
│   │   ├── pages/              # LearnerDashboard
│   │   └── index.ts
│   ├── company/                # Module entreprise
│   │   ├── pages/              # CompanyDashboard, ProjectsList
│   │   ├── domain/entities/    # Project (business logic)
│   │   └── index.ts
│   └── admin/                  # Module administration
│       ├── pages/              # AdminDashboard
│       └── index.ts
│
├── presentation/               # Composants partagés
│   ├── components/             # ErrorBoundary, LoadingSpinner, Navigation
│   ├── layouts/                # AppLayout
│   ├── pages/                  # Dashboard, LandingPage
│   ├── router/                 # app-router.tsx (React Router v6)
│   └── styles/                 # global.css
│
├── infrastructure/             # Services partagés
├── domain/                     # Entités communes
└── application/                # Use cases partagés
```

## 🚀 Démarrage Rapide

### Installation

```bash
# À la racine du monorepo
pnpm install

# Ou spécifiquement pour shell
cd apps/frontend/shell
pnpm install
```

### Développement

```bash
# Démarrer le serveur de développement
pnpm dev

# L'application sera disponible sur http://localhost:3000
```

### Build Production

```bash
# Construire pour la production
pnpm build

# Prévisualiser le build
pnpm preview
```

### Tests

```bash
# Lancer les tests
pnpm test

# Tests avec UI
pnpm test:ui

# Tests avec coverage
pnpm test:coverage
```

## 📋 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `pnpm dev` | Démarre le serveur Vite en mode développement |
| `pnpm build` | Build production (dist/) |
| `pnpm preview` | Prévisualise le build production |
| `pnpm test` | Lance vitest en mode watch |
| `pnpm test:run` | Lance les tests une fois |
| `pnpm test:coverage` | Génère le rapport de couverture |
| `pnpm lint` | Vérifie le code avec ESLint |
| `pnpm lint:fix` | Corrige automatiquement les erreurs ESLint |
| `pnpm type-check` | Vérifie les types TypeScript |
| `pnpm format` | Formate le code avec Prettier |
| `pnpm format:check` | Vérifie le formatage |

## 🎯 Routing

### Routes Publiques
- `/` - Landing page
- `/auth/login` - Page de connexion
- `/auth/register` - Page d'inscription
- `/auth/forgot-password` - Mot de passe oublié

### Routes Protégées
- `/dashboard` - Dashboard principal
- `/learner/dashboard` - Dashboard apprenant
- `/company/dashboard` - Dashboard entreprise
- `/company/projects` - Liste des projets
- `/admin/users` - Gestion des utilisateurs (admin uniquement)

### Gardes de Routes

```typescript
// Route protégée simple
<ProtectedRoute>
  <YourPage />
</ProtectedRoute>

// Route avec permissions
<ProtectedRoute requiredPermissions={['read:admin', 'write:admin']}>
  <AdminPage />
</ProtectedRoute>

// Route publique (redirige si authentifié)
<PublicRoute redirectPath="/dashboard">
  <LoginPage />
</PublicRoute>
```

## 🔌 Lazy Loading

Tous les modules sont chargés de façon lazy pour optimiser les performances:

```typescript
const LoginPage = lazy(() =>
  import('@/modules/auth/pages/LoginPage')
    .then(m => ({ default: m.LoginPage }))
);
```

## 📦 Code Splitting

Le build produit automatiquement des chunks optimisés:
- `vendor.js` - React, React DOM, React Router
- `index.js` - Code de l'application
- Chunks dynamiques pour chaque module lazy-loadé

## 🛠️ Configuration

### Path Aliases

```typescript
'@/*' → 'src/*'
'@/modules/*' → 'src/modules/*'
'@/presentation/*' → 'src/presentation/*'
'@/infrastructure/*' → 'src/infrastructure/*'
'@/domain/*' → 'src/domain/*'
'@/application/*' → 'src/application/*'
```

### Variables d'Environnement

```bash
# .env.example
VITE_API_URL=http://localhost:8001
VITE_APP_NAME=SkillForge AI
```

## 📚 Dépendances Principales

### Production
- **React 19.1.1** - Library UI
- **React Router 6.20.1** - Routing
- **Redux Toolkit 2.0.1** - State management
- **TanStack Query 5.8.4** - Server state
- **Zod 3.22.4** - Validation schemas
- **Axios 1.6.2** - HTTP client

### Développement
- **Vite 7.1.2** - Build tool
- **TypeScript 5.8.3** - Type safety
- **Vitest 2.1.1** - Testing framework
- **Testing Library 16.0.1** - Testing utilities
- **ESLint 9.33.0** - Linting
- **Prettier 3.6.2** - Code formatting

## 🎨 Styling

- **TailwindCSS** - Utility-first CSS
- **Global styles** - `src/presentation/styles/global.css`
- **Component styles** - Co-localisés avec les composants

## 🧪 Testing

### Exemple de Test

```typescript
import { render, screen } from '@testing-library/react';
import { LoginPage } from '@/modules/auth/pages/LoginPage';

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
});
```

### Configuration

- **Framework**: Vitest
- **Environment**: jsdom
- **Coverage**: v8
- **Setup**: `src/test/setup.ts`

## 📖 Bonnes Pratiques

### 1. Organisation des Modules

Chaque module doit suivre cette structure:

```
module-name/
├── pages/              # Pages du module
├── components/         # Composants UI du module
├── hooks/              # Hooks métier du module
├── domain/             # Entités et value objects (si applicable)
├── services/           # Services spécifiques (si applicable)
└── index.ts            # Exports publics
```

### 2. Imports

```typescript
// ✅ Bon - Utilise les path aliases
import { LoginPage } from '@/modules/auth/pages/LoginPage';

// ❌ Mauvais - Import relatif profond
import { LoginPage } from '../../../modules/auth/pages/LoginPage';
```

### 3. Lazy Loading

Toujours utiliser lazy loading pour les pages:

```typescript
// ✅ Bon
const DashboardPage = lazy(() => import('@/modules/learner/pages/Dashboard'));

// ❌ Mauvais - Import direct
import { DashboardPage } from '@/modules/learner/pages/Dashboard';
```

### 4. State Management

- **Redux** - État global partagé entre modules
- **React Query** - État serveur (cache, requêtes)
- **Local State** - État local aux composants

## 🔍 Debugging

### Vite Dev Server

```bash
# Mode debug
DEBUG=vite:* pnpm dev

# Build avec source maps
pnpm build --sourcemap
```

### React DevTools

Installé automatiquement en mode développement.

## 🚢 Déploiement

### Build

```bash
pnpm build
```

Produit le dossier `dist/` prêt pour le déploiement.

### Docker

```dockerfile
# Exemple Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📊 Performance

### Métriques Build

- **Bundle size**: ~175 KB (gzip: ~52 KB)
- **Build time**: ~2s
- **Initial load**: Code splitting automatique

### Optimisations

- ✅ Code splitting par route
- ✅ Lazy loading des modules
- ✅ Tree shaking
- ✅ Minification (esbuild)
- ✅ CSS code splitting

## 🤝 Contribution

### Workflow

1. Créer une branche feature: `git checkout -b feature/my-feature`
2. Développer et tester: `pnpm test`
3. Linter: `pnpm lint:fix`
4. Commit: `git commit -m "feat: my feature"`
5. Push: `git push origin feature/my-feature`
6. Créer une PR

### Conventions

- **Commits**: Suivre [Conventional Commits](https://www.conventionalcommits.org/)
- **Code**: ESLint + Prettier
- **Types**: TypeScript strict mode

## 📝 Migration Notes

### De Module Federation → Monolith

Cette application a été migrée de Module Federation vers une architecture monolithique modulaire.

**Avantages:**
- ✅ Build 52% plus léger
- ✅ Temps de chargement 88% plus rapide
- ✅ Maintenance simplifiée
- ✅ Debugging plus facile

Pour plus de détails, voir la [documentation complète](../../../Documentations/ANALYSE_CRITIQUE_FRONTEND_BACKEND_USER_SERVICE.md#11-module-federation-vs-monolithe--analyse-comparative-détaillée).

## 📞 Support

Pour toute question ou problème:
- Documentation complète: `Documentations/`
- Issues GitHub: https://github.com/sahemac/skillforge-ai-monorepo/issues

---

🤖 Généré avec [Claude Code](https://claude.com/claude-code)
