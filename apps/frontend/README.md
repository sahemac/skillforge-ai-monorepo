# SkillForge AI Frontend

A modern React TypeScript application built with Vite for SkillForge AI platform.

## Features

- ⚡ **Vite** - Fast build tool and development server
- ⚛️ **React 19** - Latest React with TypeScript support
- 📏 **ESLint** - Code linting with TypeScript rules
- 💅 **Prettier** - Code formatting
- 🎯 **Path Aliases** - Clean imports with `@/` prefix
- 🏗️ **Modern Structure** - Organized folder structure for scalability

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Application pages/views
├── services/      # API calls and external services
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
├── types/         # TypeScript type definitions
├── styles/        # Global styles and CSS variables
├── App.tsx        # Main application component
├── main.tsx       # Application entry point
└── index.css      # Global CSS imports
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking

## Development Guidelines

### Code Style

- Use TypeScript for all new files
- Follow ESLint and Prettier configurations
- Use path aliases (`@/`) for imports
- Prefer functional components with hooks

### Import Structure

```typescript
// External libraries
import React from 'react'

// Internal modules with aliases
import { Button } from '@/components'
import { useAuth } from '@/hooks'
import { UserService } from '@/services'
import type { User } from '@/types'

// Relative imports (only for same directory)
import './Component.css'
```

### Component Structure

```typescript
// Component.tsx
interface ComponentProps {
  title: string
  optional?: boolean
}

export const Component: React.FC<ComponentProps> = ({ 
  title, 
  optional = false 
}) => {
  return (
    <div>
      <h1>{title}</h1>
    </div>
  )
}

export default Component
```

## Build and Deployment

```bash
# Build for production
npm run build

# The built files will be in the `dist` directory
```

## Configuration

### Path Aliases

The following path aliases are configured:

- `@/` → `src/`
- `@/components` → `src/components`
- `@/pages` → `src/pages`
- `@/services` → `src/services`
- `@/hooks` → `src/hooks`
- `@/utils` → `src/utils`
- `@/types` → `src/types`
- `@/styles` → `src/styles`

### Environment Variables

Create a `.env` file in the root directory for environment-specific configuration:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=SkillForge AI
```

## Contributing

1. Follow the existing code style and structure
2. Run `npm run lint` and `npm run format` before committing
3. Ensure `npm run build` passes without errors
4. Use semantic commit messages

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **CSS3** - Modern styling with custom properties
