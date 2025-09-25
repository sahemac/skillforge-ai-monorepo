# Dockerfile pour SkillForge AI Shell App
# Build multi-stage optimisé pour Cloud Run

# Stage 1: Build
FROM node:20-alpine AS builder

# Installation des dépendances système nécessaires
RUN apk add --no-cache git python3 make g++

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration du workspace depuis la racine
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./

# Installation de pnpm globalement
RUN npm install -g pnpm@latest

# Copie des packages partagés nécessaires au build
COPY packages ./packages

# Copie du code source de l'application shell
COPY apps/frontend/shell ./apps/frontend/shell

# Installation des dépendances depuis la racine
RUN pnpm install --frozen-lockfile

# Build de l'application pour la production
RUN cd apps/frontend/shell && pnpm build

# Stage 2: Production
FROM nginx:alpine AS production

# Installation des dépendances de sécurité
RUN apk add --no-cache ca-certificates tzdata

# Création d'un utilisateur non-root pour nginx
RUN addgroup -g 1001 -S nodejs && adduser -S nginx -u 1001 -G nodejs

# Copie des fichiers buildés depuis le stage builder
COPY --from=builder /app/apps/frontend/shell/dist /usr/share/nginx/html

# Installation de gettext pour envsubst
RUN apk add --no-cache gettext

# Copie de la configuration nginx template et du script de démarrage
COPY apps/frontend/shell/nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY apps/frontend/shell/start.sh /start.sh

# Rendre le script exécutable
RUN chmod +x /start.sh

# Changement de propriétaire des fichiers
RUN chown -R nginx:nodejs /usr/share/nginx/html
RUN chown -R nginx:nodejs /var/cache/nginx
RUN chown -R nginx:nodejs /var/log/nginx

# Exposition du port dynamique pour Cloud Run
EXPOSE $PORT

# Commande de démarrage avec script dynamique
CMD ["/start.sh"]

# Labels pour la traçabilité
LABEL maintainer="SkillForge AI Team"
LABEL description="SkillForge AI Shell App - Module Federation Host"
LABEL version="1.0.0"