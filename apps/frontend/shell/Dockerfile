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

# Configuration nginx pour SPA avec support des micro-frontends
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    
    # Configuration pour la sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # Configuration pour les micro-frontends
    add_header Cross-Origin-Embedder-Policy unsafe-none;
    add_header Cross-Origin-Opener-Policy same-origin-allow-popups;
    
    # Racine du site
    root /usr/share/nginx/html;
    index index.html;
    
    # Gestion des fichiers statiques avec cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin *;
    }
    
    # Gestion des fichiers de module federation
    location /assets/ {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
        expires 1h;
    }
    
    # Configuration pour SPA - toutes les routes pointent vers index.html
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma no-cache;
        add_header Expires 0;
    }
    
    # Health check endpoint pour Cloud Run
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Gestion des erreurs
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# Changement de propriétaire des fichiers
RUN chown -R nginx:nodejs /usr/share/nginx/html
RUN chown -R nginx:nodejs /var/cache/nginx
RUN chown -R nginx:nodejs /var/log/nginx

# Exposition du port 80 pour Cloud Run
EXPOSE 80

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"]

# Labels pour la traçabilité
LABEL maintainer="SkillForge AI Team"
LABEL description="SkillForge AI Shell App - Module Federation Host"
LABEL version="1.0.0"