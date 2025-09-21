# SkillForge AI - Enterprise Micro-Frontend Architecture

## Overview

This document describes the complete enterprise-grade micro-frontend architecture implemented for SkillForge AI. The architecture follows Clean Architecture principles, Domain-Driven Design (DDD), and Module Federation for scalable, maintainable frontend applications.

## Architecture Components

### 1. Monorepo Structure

```
skillforge-ai-monorepo/
├── packages/                    # Shared packages
│   ├── core/                    # Domain logic (DDD)
│   ├── ui-kit/                  # Design system
│   ├── api-client/              # API SDK
│   └── shared/                  # Utilities
├── apps/frontend/               # Micro-frontends
│   ├── shell/                   # Main container (Module Federation Host)
│   ├── auth/                    # Authentication micro-frontend
│   ├── learner/                 # Learner portal
│   ├── company/                 # Company portal
│   └── admin/                   # Admin panel
└── tsconfig.json               # Root TypeScript configuration
```

### 2. Shared Packages

#### @skillforge-ai/core
- **Purpose**: Domain logic with DDD patterns
- **Contains**: Entities, Value Objects, Aggregates, Domain Services
- **Key Features**:
  - BaseEntity and ValueObject base classes
  - User entity with business logic
  - Email value object with validation
  - Strict TypeScript implementation

#### @skillforge-ai/ui-kit
- **Purpose**: Design system and reusable React components
- **Contains**: Buttons, Forms, Layout components, Theme tokens
- **Technologies**: React, Tailwind CSS, Radix UI, Storybook

#### @skillforge-ai/api-client
- **Purpose**: Type-safe SDK for backend services
- **Contains**: API clients, Request/Response types, Interceptors
- **Technologies**: Axios, Zod for validation, RxJS for reactive programming

#### @skillforge-ai/shared
- **Purpose**: Common utilities and helpers
- **Contains**: Date utilities, Validation helpers, Constants, Types

### 3. Micro-Frontend Applications

#### Shell App (Host)
- **Port**: 3000
- **Role**: Main container application (Module Federation Host)
- **Responsibilities**:
  - Navigation and routing
  - Authentication state management
  - Error boundaries
  - Loading micro-frontends dynamically

#### Auth Micro-Frontend (Remote)
- **Port**: 3001
- **Role**: Authentication and user management
- **Clean Architecture Implementation**:
  ```
  src/
  ├── domain/
  │   ├── entities/          # AuthSession
  │   ├── value-objects/     # Password
  │   └── repositories/      # IAuthRepository (interface)
  ├── application/
  │   └── use-cases/         # LoginUseCase, RegisterUseCase
  ├── infrastructure/
  │   ├── adapters/          # AuthRepositoryImpl
  │   └── api/               # AuthApiClient
  └── presentation/
      ├── components/        # UI components
      ├── pages/             # Login, Register pages
      ├── hooks/             # React hooks for use cases
      └── forms/             # Form components
  ```

#### Learner Micro-Frontend (Remote)
- **Port**: 3002
- **Role**: Learning dashboard and features
- **Status**: Placeholder (ready for implementation)

#### Company Micro-Frontend (Remote)
- **Port**: 3003
- **Role**: Company portal and team management
- **Status**: Placeholder (ready for implementation)

#### Admin Micro-Frontend (Remote)
- **Port**: 3004
- **Role**: Administrative panel and tools
- **Status**: Placeholder (ready for implementation)

## Clean Architecture Implementation

### Layer Structure

1. **Domain Layer** (Innermost)
   - Entities: Business objects with identity
   - Value Objects: Immutable objects without identity
   - Aggregates: Cluster of domain objects
   - Domain Services: Business logic that doesn't belong to entities

2. **Application Layer**
   - Use Cases: Application-specific business rules
   - Ports: Interfaces for external dependencies
   - DTOs: Data transfer objects

3. **Infrastructure Layer**
   - Adapters: Implementations of ports
   - API Clients: External service communication
   - Storage: Local storage, session management

4. **Presentation Layer** (Outermost)
   - Components: React UI components
   - Pages: Route-level components
   - Hooks: React hooks connecting to use cases
   - Forms: Form handling and validation

### Dependency Injection

Each micro-frontend implements a simple dependency injection pattern:
- Use cases receive repository interfaces as constructor parameters
- React hooks create and configure use cases
- Infrastructure adapters implement domain repository interfaces

## Module Federation Configuration

### Host Configuration (Shell)
```typescript
// vite.config.ts
federation({
  name: 'shell',
  remotes: {
    auth: 'http://localhost:3001/assets/remoteEntry.js',
    learner: 'http://localhost:3002/assets/remoteEntry.js',
    company: 'http://localhost:3003/assets/remoteEntry.js',
    admin: 'http://localhost:3004/assets/remoteEntry.js',
  },
  shared: {
    react: { singleton: true },
    'react-dom': { singleton: true },
    'react-router-dom': { singleton: true },
    '@skillforge-ai/core': { singleton: true },
    '@skillforge-ai/ui-kit': { singleton: true },
    '@skillforge-ai/api-client': { singleton: true },
    '@skillforge-ai/shared': { singleton: true },
  },
})
```

### Remote Configuration (Auth)
```typescript
// vite.config.ts
federation({
  name: 'auth',
  filename: 'remoteEntry.js',
  exposes: {
    './App': './src/app.tsx',
  },
  shared: {
    // Same shared dependencies
  },
})
```

## TypeScript Configuration

### Path Aliases
All applications use consistent path aliases:
- `@/*`: Local source files
- `@/domain/*`: Domain layer
- `@/application/*`: Application layer
- `@/infrastructure/*`: Infrastructure layer
- `@/presentation/*`: Presentation layer
- `@skillforge-ai/*`: Shared packages

### Project References
TypeScript project references ensure proper compilation order and type checking across the monorepo.

## Development Workflow

### Getting Started
1. Install dependencies: `npm install` (at root)
2. Start shell app: `npm run dev` (in apps/frontend/shell)
3. Start auth micro-frontend: `npm run dev` (in apps/frontend/auth)
4. Access application at http://localhost:3000

### Adding New Features
1. Define domain entities and value objects in `@skillforge-ai/core`
2. Create use cases in application layer
3. Implement repository adapters in infrastructure layer
4. Build React components in presentation layer
5. Connect with hooks following the dependency injection pattern

## Key Benefits

### Scalability
- Independent deployment of micro-frontends
- Team autonomy with clear boundaries
- Shared code through packages reduces duplication

### Maintainability
- Clean Architecture ensures separation of concerns
- DDD provides rich domain models
- TypeScript ensures type safety across boundaries

### Performance
- Module Federation enables code splitting
- Shared dependencies prevent duplication
- Lazy loading of micro-frontends

### Developer Experience
- Consistent patterns across all applications
- Strong typing with TypeScript
- Hot reloading during development
- Clear project structure

## Security Considerations

### Authentication
- JWT tokens stored securely
- Automatic token refresh
- Cross-micro-frontend session management

### Module Federation
- CORS configuration for remote loading
- Content Security Policy headers
- Trusted remote sources only

## Testing Strategy

### Unit Tests
- Domain entities and value objects
- Use cases with mocked repositories
- React components with React Testing Library

### Integration Tests
- API adapters with real/mocked backends
- End-to-end user flows

### E2E Tests
- Cross-micro-frontend navigation
- Authentication flows
- Critical user journeys

## Future Enhancements

1. **Service Worker Integration**: Offline support and caching
2. **Micro-Frontend Registry**: Dynamic discovery and loading
3. **Shared State Management**: Cross-application state synchronization
4. **Performance Monitoring**: Real-time metrics and alerts
5. **A/B Testing Framework**: Feature flag integration

## Conclusion

This enterprise micro-frontend architecture provides a solid foundation for SkillForge AI's frontend applications. It combines modern architectural patterns with proven technologies to deliver a scalable, maintainable, and performant solution that can grow with the business needs.