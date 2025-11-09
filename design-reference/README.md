# Design Reference

This directory contains HTML templates used as **visual and design references** for the SkillForge AI application.

## ⚠️ Important Note

These templates are **NOT meant to be used directly** in the React/Vite application. They use:
- Tailwind CSS via CDN (incompatible with our build process)
- Plain HTML structure (not React components)

## Purpose

Use these templates as:
- **Visual design reference** for layout and styling
- **UI/UX inspiration** for component design
- **Color scheme and branding** reference

## How to Use

When implementing features in the React app (`apps/frontend/shell/`):
1. Review the template's design and layout
2. Extract the Tailwind classes you need
3. Recreate the component in React using our UI kit (`packages/ui-kit/`)
4. Adapt the styling to work with our Vite + Tailwind setup

## Templates Included

- `index.html` - Landing page design
- `login.html` - Login page
- `register.html` - Registration page
- `verify-email.html` - Email verification page
- `refresh-token.html` - Token refresh page
- `logo_skillforge_AI.png.png` - Original logo file (Note: corrected version is in `apps/frontend/shared/assets/logos/`)
