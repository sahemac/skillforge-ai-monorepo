# apps/backend/user-service/Dockerfile

# --- Étape 1: Le "Builder"
# Installe les dépendances dans une première étape pour optimiser le cache de layers
FROM python:3.11-slim as builder

WORKDIR /app

# Copie les fichiers de dépendances
COPY requirements.txt requirements-dev.txt ./

# Installe uniquement les dépendances de production
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 2: Le "Runtime"
# L'image finale est basée sur la même image slim
FROM python:3.11-slim

WORKDIR /app

# Crée un utilisateur non-root pour des raisons de sécurité
RUN useradd --no-create-home appuser
USER appuser

# Copie les dépendances installées depuis l'étape "builder"
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copie le code source de l'application (qui n'existe pas encore, c'est normal)
# COPY ./app /app/app

# Commande pour lancer le serveur (sera remplacée par le vrai code plus tard)
# Pour l'instant, on met une commande qui tourne en boucle pour que le conteneur ne crash pas
CMD ["tail", "-f", "/dev/null"]
