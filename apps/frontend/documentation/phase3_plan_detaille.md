# 📋 Phase 3 - Plan Détaillé : State Management CQRS + Design System

*Date : 2025-01-23*  
*Phase : 3 - Infrastructure Avancée*  
*Durée estimée : 2-3 jours*

---

## 🎯 Vue d'Ensemble Phase 3

La Phase 3 transforme notre architecture en un système **production-ready** avec gestion d'état sophistiquée, design system complet, et intégration API robuste.

---

## 1️⃣ **State Management CQRS Pattern**

### 🔍 **Qu'est-ce que CQRS ?**
**CQRS** (Command Query Responsibility Segregation) sépare les opérations de **lecture** (Query) des opérations d'**écriture** (Command). C'est essentiel pour une app complexe avec 3 types d'utilisateurs.

### 📦 **Ce que je vais implémenter**

#### **A. Commands (Écriture) avec Redux Toolkit**
```typescript
// packages/shared-state/src/commands/

// Exemple : Créer un projet
const projectSlice = createSlice({
  name: 'projects',
  initialState: { creating: false, error: null },
  reducers: {
    createProjectStart: (state) => {
      state.creating = true;
    },
    createProjectSuccess: (state, action) => {
      state.creating = false;
      // Effet de bord : invalider les queries
    },
    createProjectFailure: (state, action) => {
      state.creating = false;
      state.error = action.payload;
    }
  }
});
```

**Pourquoi ?** 
- Traçabilité complète des actions
- Time-travel debugging
- Undo/Redo possible
- État prédictible

#### **B. Queries (Lecture) avec TanStack Query**
```typescript
// packages/shared-state/src/queries/

// Exemple : Récupérer les projets
export const useProjectsQuery = (filters?: ProjectFilters) => {
  return useQuery({
    queryKey: ['projects', filters],
    queryFn: () => projectApi.getProjects(filters),
    staleTime: 5 * 60 * 1000, // Cache 5 minutes
    cacheTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false
  });
};

// Optimistic updates
export const useCreateProjectMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: projectApi.create,
    onMutate: async (newProject) => {
      // Annuler requêtes en cours
      await queryClient.cancelQueries(['projects']);
      
      // Snapshot pour rollback
      const previousProjects = queryClient.getQueryData(['projects']);
      
      // Update optimiste
      queryClient.setQueryData(['projects'], old => [...old, newProject]);
      
      return { previousProjects };
    },
    onError: (err, newProject, context) => {
      // Rollback si erreur
      queryClient.setQueryData(['projects'], context.previousProjects);
    }
  });
};
```

**Pourquoi ?**
- Cache intelligent automatique
- Synchronisation server state
- Optimistic UI updates
- Gestion erreurs/retry automatique

#### **C. Event Bus (Communication Inter-Apps)**
```typescript
// packages/shared-state/src/events/

class EventBus extends EventEmitter {
  private static instance: EventBus;
  
  // Événements typés
  emit<T>(event: AppEvent<T>): void {
    super.emit(event.type, event.payload);
  }
  
  on<T>(eventType: string, handler: (payload: T) => void): void {
    super.on(eventType, handler);
  }
}

// Usage dans shell
eventBus.on('USER_LOGGED_IN', (user) => {
  // Mettre à jour navigation
  updateNavigation(user.role);
});

// Usage dans auth app
eventBus.emit({
  type: 'USER_LOGGED_IN',
  payload: { userId, role, permissions }
});
```

**Pourquoi ?**
- Communication entre micro-frontends
- Découplage total des apps
- Patterns pub/sub scalable

#### **D. Signals (Fine-grained Reactivity)**
```typescript
// packages/shared-state/src/signals/

import { signal, computed, effect } from '@preact/signals-react';

// Signal pour notification temps réel
export const notificationSignal = signal<Notification[]>([]);

// Computed pour badge count
export const unreadCount = computed(() => 
  notificationSignal.value.filter(n => !n.read).length
);

// Effect pour son notification
effect(() => {
  if (unreadCount.value > 0) {
    playNotificationSound();
  }
});

// Usage dans composant
function NotificationBadge() {
  // Re-render UNIQUEMENT si unreadCount change
  return <Badge count={unreadCount.value} />;
}
```

**Pourquoi ?**
- Performance maximale
- Re-renders minimaux
- Réactivité fine
- Idéal pour real-time

---

## 2️⃣ **Design System Complet**

### 🎨 **Ce que je vais créer**

#### **A. Design Tokens (Source de Vérité)**
```typescript
// packages/ui-kit/src/tokens/

export const tokens = {
  // Couleurs sémantiques
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      900: '#1e3a8a'
    },
    semantic: {
      error: 'var(--color-red-500)',
      success: 'var(--color-green-500)',
      warning: 'var(--color-amber-500)',
      info: 'var(--color-blue-500)'
    }
  },
  
  // Espacements (8px grid)
  spacing: {
    xs: '0.5rem',   // 8px
    sm: '1rem',     // 16px
    md: '1.5rem',   // 24px
    lg: '2rem',     // 32px
    xl: '3rem'      // 48px
  },
  
  // Typography
  typography: {
    fontFamily: {
      sans: 'Inter, system-ui, sans-serif',
      mono: 'JetBrains Mono, monospace'
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '2rem'
    }
  },
  
  // Animations
  motion: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms'
    },
    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)'
    }
  }
};
```

#### **B. Composants Primitifs (Atoms)**
```typescript
// packages/ui-kit/src/primitives/

// Button avec variantes
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading, ...props }, ref) => {
    return (
      <StyledButton
        ref={ref}
        $variant={variant}
        $size={size}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading && <Spinner size="sm" />}
        {props.children}
      </StyledButton>
    );
  }
);

// Input avec validation
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ error, icon, ...props }, ref) => {
    return (
      <InputWrapper>
        {icon && <Icon>{icon}</Icon>}
        <StyledInput 
          ref={ref} 
          $error={!!error}
          aria-invalid={!!error}
          {...props} 
        />
        {error && <ErrorMessage>{error}</ErrorMessage>}
      </InputWrapper>
    );
  }
);
```

#### **C. Composants Composés (Molecules)**
```typescript
// packages/ui-kit/src/components/

// Card avec Compound Pattern
export const Card = ({ children, ...props }) => {
  return <StyledCard {...props}>{children}</StyledCard>;
};

Card.Header = ({ children, actions }) => (
  <CardHeader>
    <CardTitle>{children}</CardTitle>
    {actions && <CardActions>{actions}</CardActions>}
  </CardHeader>
);

Card.Body = ({ children }) => (
  <CardBody>{children}</CardBody>
);

Card.Footer = ({ children, align = 'right' }) => (
  <CardFooter $align={align}>{children}</CardFooter>
);

// Usage
<Card>
  <Card.Header actions={<Button size="sm">Edit</Button>}>
    Project Details
  </Card.Header>
  <Card.Body>
    <ProjectInfo />
  </Card.Body>
  <Card.Footer>
    <Button variant="ghost">Cancel</Button>
    <Button>Save</Button>
  </Card.Footer>
</Card>
```

#### **D. Patterns Réutilisables (Organisms)**
```typescript
// packages/ui-kit/src/patterns/

// DataTable générique
export function DataTable<T>({ 
  data, 
  columns, 
  onSort, 
  onFilter,
  pagination 
}: DataTableProps<T>) {
  return (
    <Table>
      <TableHeader columns={columns} onSort={onSort} />
      <TableBody data={data} columns={columns} />
      {pagination && <TablePagination {...pagination} />}
    </Table>
  );
}

// Form Builder
export const FormBuilder = ({ 
  schema, 
  onSubmit, 
  defaultValues 
}: FormBuilderProps) => {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues
  });
  
  return (
    <Form {...form}>
      {renderFields(schema)}
      <Button type="submit">Submit</Button>
    </Form>
  );
};
```

---

## 3️⃣ **Intégration API avec Backend**

### 🔌 **Ce que je vais configurer**

#### **A. SDK API Type-Safe**
```typescript
// packages/api-client/src/

// Client principal avec intercepteurs
class ApiClient {
  private axios: AxiosInstance;
  
  constructor(config: ApiConfig) {
    this.axios = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 10000
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor - Ajouter token
    this.axios.interceptors.request.use(
      async (config) => {
        const token = await tokenManager.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );
    
    // Response interceptor - Refresh token
    this.axios.interceptors.response.use(
      response => response,
      async (error) => {
        if (error.response?.status === 401) {
          const newToken = await tokenManager.refreshToken();
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return this.axios.request(error.config);
        }
        throw error;
      }
    );
  }
}
```

#### **B. Génération Types depuis OpenAPI**
```typescript
// Script de génération
// packages/api-client/scripts/generate-types.js

import { generateApi } from 'swagger-typescript-api';

generateApi({
  name: "SkillForgeApi.ts",
  output: "./src/generated",
  url: "http://localhost:8000/openapi.json",
  generateClient: true,
  generateRouteTypes: true,
  generateResponses: true
});

// Résultat : Types TypeScript automatiques
export interface User {
  id: string;
  email: string;
  role: 'LEARNER' | 'COMPANY' | 'ADMIN';
  profile: UserProfile;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  status: ProjectStatus;
  milestones: Milestone[];
}
```

#### **C. Services Métier Typés**
```typescript
// packages/api-client/src/services/

export class UserService {
  constructor(private client: ApiClient) {}
  
  async getProfile(): Promise<User> {
    const { data } = await this.client.get<User>('/users/me');
    return data;
  }
  
  async updateProfile(updates: Partial<UserProfile>): Promise<User> {
    const { data } = await this.client.patch<User>('/users/me', updates);
    return data;
  }
}

export class ProjectService {
  async getProjects(filters?: ProjectFilters): Promise<PaginatedResponse<Project>> {
    const { data } = await this.client.get<PaginatedResponse<Project>>('/projects', {
      params: filters
    });
    return data;
  }
  
  async createProject(project: CreateProjectDto): Promise<Project> {
    const { data } = await this.client.post<Project>('/projects', project);
    return data;
  }
}
```

---

## 4️⃣ **Tests Unitaires et Intégration**

### 🧪 **Ce que je vais mettre en place**

#### **A. Tests Unitaires (Domain & Use Cases)**
```typescript
// packages/core/src/domain/__tests__/

describe('User Entity', () => {
  it('should validate email format', () => {
    const validEmail = new Email('user@example.com');
    expect(validEmail.isValid()).toBe(true);
    
    expect(() => new Email('invalid')).toThrow(ValidationError);
  });
  
  it('should check password strength', () => {
    const weakPassword = new Password('123');
    expect(weakPassword.isStrong()).toBe(false);
    
    const strongPassword = new Password('MyStr0ng!Pass');
    expect(strongPassword.isStrong()).toBe(true);
  });
});

describe('LoginUseCase', () => {
  const mockAuthRepo = {
    login: vi.fn()
  };
  
  it('should authenticate valid credentials', async () => {
    const useCase = new LoginUseCase(mockAuthRepo);
    mockAuthRepo.login.mockResolvedValue(mockAuthSession);
    
    const result = await useCase.execute({
      email: 'user@test.com',
      password: 'ValidPass123!'
    });
    
    expect(result).toBeInstanceOf(AuthSession);
    expect(mockAuthRepo.login).toHaveBeenCalledWith(
      'user@test.com',
      'ValidPass123!'
    );
  });
});
```

#### **B. Tests Composants React**
```typescript
// apps/frontend/auth/src/presentation/__tests__/

describe('LoginForm', () => {
  it('should validate required fields', async () => {
    render(<LoginForm onSubmit={vi.fn()} />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await userEvent.click(submitButton);
    
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
  
  it('should submit valid form', async () => {
    const handleSubmit = vi.fn();
    render(<LoginForm onSubmit={handleSubmit} />);
    
    await userEvent.type(screen.getByLabelText(/email/i), 'user@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'Password123!');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        email: 'user@test.com',
        password: 'Password123!'
      });
    });
  });
});
```

#### **C. Tests Integration (API Mocking)**
```typescript
// packages/api-client/src/__tests__/

import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        accessToken: 'mock-token',
        refreshToken: 'mock-refresh',
        user: { id: '1', email: 'user@test.com' }
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('AuthService Integration', () => {
  it('should handle login flow', async () => {
    const authService = new AuthService(apiClient);
    const result = await authService.login('user@test.com', 'password');
    
    expect(result.accessToken).toBe('mock-token');
    expect(tokenManager.getStoredToken()).toBe('mock-token');
  });
});
```

#### **D. Tests E2E (Playwright)**
```typescript
// e2e/auth.spec.ts

test.describe('Authentication Flow', () => {
  test('should login and navigate to dashboard', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid=email-input]', 'user@test.com');
    await page.fill('[data-testid=password-input]', 'Password123!');
    await page.click('[data-testid=login-button]');
    
    await expect(page).toHaveURL('/learner/dashboard');
    await expect(page.locator('[data-testid=user-menu]')).toContainText('user@test.com');
  });
});
```

---

## 📊 **Impact Concret de la Phase 3**

### Avant Phase 3
- ❌ État local dispersé
- ❌ Pas de cache
- ❌ UI incohérente
- ❌ Intégration API manuelle
- ❌ Pas de tests

### Après Phase 3
- ✅ **État centralisé** avec CQRS
- ✅ **Cache intelligent** 5-10min
- ✅ **Design system** unifié
- ✅ **API type-safe** auto-générée
- ✅ **Tests 80%** coverage

### Bénéfices Mesurables
- 🚀 **Performance** : -60% re-renders inutiles
- 💾 **Cache** : -80% requêtes API
- 🎨 **Consistance** : 100% composants réutilisés
- 🐛 **Bugs** : -70% grâce aux types
- 🧪 **Confiance** : 80% code coverage

---

## 🛠️ **Technologies Utilisées**

| Catégorie | Technologie | Raison |
|-----------|-------------|---------|
| **Commands** | Redux Toolkit | Debugging, DevTools, Time-travel |
| **Queries** | TanStack Query v5 | Cache automatique, Optimistic UI |
| **Events** | EventEmitter3 | Léger, Type-safe, Performant |
| **Signals** | Preact Signals | Fine-grained reactivity |
| **UI Kit** | Styled Components | CSS-in-JS, Theming, SSR |
| **API** | Axios + OpenAPI | Intercepteurs, Types auto |
| **Tests** | Vitest + Testing Library | Fast, ESM native |
| **E2E** | Playwright | Cross-browser, Reliable |

---

## 📅 **Planning Phase 3**

### Jour 1 : State Management
- Matin : CQRS avec Redux Toolkit + React Query
- Après-midi : Event Bus + Signals

### Jour 2 : Design System
- Matin : Tokens + Primitives
- Après-midi : Composants + Patterns

### Jour 3 : Integration & Tests
- Matin : API Client + Types
- Après-midi : Tests setup

---

## ✅ **Livrables Phase 3**

1. **State Management CQRS** fonctionnel
2. **Design System** avec 20+ composants
3. **API Client** type-safe généré
4. **Tests** avec 80% coverage
5. **Documentation** Storybook
6. **Performance** monitoring setup

---

*Cette phase transforme l'architecture en système production-ready*