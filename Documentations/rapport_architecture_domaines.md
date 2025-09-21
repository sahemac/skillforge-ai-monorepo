# 🌐 Rapport Architecture Domaines - SkillForge AI SaaS

*Date : 2025-01-23*  
*Sujet : Configuration DNS et Architecture Multi-Services*  
*IP Statique : 34.149.174.205 (skillforge-global-ip)*

---

## 🎯 Analyse de Votre Configuration Actuelle

### 📍 **Configuration DNS Existante**
```
IP Statique: 34.149.174.205 (skillforge-global-ip)
└── api.emacsah.com → Backend API (user-service)
└── skillforge-ai.emacsah.com → [À CONFIGURER]
```

### 🏗️ **Architecture Recommandée SaaS**

Voici comment organiser vos domaines pour une application SaaS professionnelle :

```
📱 Application Frontend (Micro-frontends)
└── skillforge-ai.emacsah.com → Shell App (Page principale)

🔌 API Backend
└── api.emacsah.com → Services backend (user-service, etc.)

📊 Services Additionnels (Future)
├── admin.emacsah.com → Interface admin dédiée
├── docs.emacsah.com → Documentation API
└── status.emacsah.com → Status page monitoring
```

---

## 🎯 **Domaine Principal : skillforge-ai.emacsah.com**

### ✅ **OUI, c'est PARFAIT pour votre SaaS !**

**skillforge-ai.emacsah.com** est idéal comme domaine principal car :

1. **🎨 Branding** : Identité claire "SkillForge AI"
2. **🔒 Professionnalisme** : Sous-domaine dédié à l'application
3. **📈 Scalabilité** : Permet d'ajouter d'autres services sur emacsah.com
4. **🌐 SEO** : URL mémorable et descriptive

---

## 🏗️ **Architecture Technique Recommandée**

### **1. Load Balancer + Routing**

```yaml
# Configuration GCP Load Balancer
skillforge-global-ip (34.149.174.205)
├── skillforge-ai.emacsah.com/*
│   └── Frontend Shell App (Port 3000)
│       ├── /auth → Auth Micro-frontend
│       ├── /learner → Learner Micro-frontend
│       ├── /company → Company Micro-frontend
│       └── /admin → Admin Micro-frontend
│
└── api.emacsah.com/*
    └── Backend Services
        ├── /api/v1/auth → user-service (Port 8000)
        ├── /api/v1/users → user-service
        ├── /api/v1/projects → project-service (future)
        └── /api/v1/portfolios → portfolio-service (future)
```

### **2. DNS Configuration**

```bash
# Zone DNS emacsah.com
A    skillforge-ai.emacsah.com    34.149.174.205
A    api.emacsah.com              34.149.174.205

# Certificats SSL
- *.emacsah.com (Wildcard SSL)
- Ou certificats spécifiques par sous-domaine
```

### **3. Nginx/Envoy Routing**

```nginx
# Configuration Load Balancer
server {
    server_name skillforge-ai.emacsah.com;
    
    # Frontend Shell App
    location / {
        proxy_pass http://frontend-shell:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Assets micro-frontends
    location /remoteEntry.js {
        proxy_pass http://auth-microfrontend:3001;
    }
}

server {
    server_name api.emacsah.com;
    
    # Backend API
    location /api/v1/ {
        proxy_pass http://user-service:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Health checks
    location /health {
        proxy_pass http://user-service:8000/health;
    }
}
```

---

## 🔄 **Flux Utilisateur Complet**

### **1. Première Visite**
```
Utilisateur saisit: skillforge-ai.emacsah.com
└── DNS résout: 34.149.174.205
    └── Load Balancer route vers: Frontend Shell App
        └── Shell App charge: Page d'accueil/landing
            └── CTA "Se connecter" → Modal auth ou /auth
```

### **2. Authentification**
```
Clic "Se connecter"
└── Modal Auth Micro-frontend OU Redirect /auth
    └── API Call: api.emacsah.com/api/v1/auth/login
        └── JWT Token reçu
            └── Redirect basé sur rôle:
                ├── /learner/dashboard
                ├── /company/dashboard
                └── /admin/dashboard
```

### **3. Navigation Applicative**
```
Utilisateur authentifié navigue:
├── skillforge-ai.emacsah.com/learner/* → Learner Micro-frontend
├── skillforge-ai.emacsah.com/company/* → Company Micro-frontend
└── skillforge-ai.emacsah.com/admin/* → Admin Micro-frontend

Toutes les API calls → api.emacsah.com/api/v1/*
```

---

## 🛡️ **Configuration Terraform Requise**

### **1. Mise à Jour DNS**

```hcl
# terraform/environments/staging/dns.tf
resource "google_dns_record_set" "skillforge_frontend" {
  name = "skillforge-ai.emacsah.com."
  type = "A"
  ttl  = 300
  
  managed_zone = var.dns_zone_name
  rrdatas = [data.google_compute_global_address.skillforge_ip.address]
}

# Garder l'existant
resource "google_dns_record_set" "skillforge_api" {
  name = "api.emacsah.com."
  type = "A"
  ttl  = 300
  
  managed_zone = var.dns_zone_name
  rrdatas = [data.google_compute_global_address.skillforge_ip.address]
}
```

### **2. Load Balancer avec Double Routing**

```hcl
# terraform/environments/staging/load_balancer.tf

# URL Map pour Frontend
resource "google_compute_url_map" "skillforge_frontend_urlmap" {
  name            = "skillforge-frontend-urlmap-${var.environment}"
  default_service = google_compute_backend_service.frontend_shell_backend.id

  host_rule {
    hosts        = ["skillforge-ai.emacsah.com"]
    path_matcher = "frontend-paths"
  }

  path_matcher {
    name            = "frontend-paths"
    default_service = google_compute_backend_service.frontend_shell_backend.id
    
    path_rule {
      paths   = ["/auth/*"]
      service = google_compute_backend_service.auth_microfrontend_backend.id
    }
    
    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.user_service_backend.id
    }
  }
}

# URL Map pour API (existant)
resource "google_compute_url_map" "skillforge_api_urlmap" {
  name            = "skillforge-api-urlmap-${var.environment}"
  default_service = google_compute_backend_service.user_service_backend.id

  host_rule {
    hosts        = ["api.emacsah.com"]
    path_matcher = "api-paths"
  }

  path_matcher {
    name            = "api-paths"
    default_service = google_compute_backend_service.user_service_backend.id
  }
}
```

### **3. Certificats SSL Multi-Domaines**

```hcl
resource "google_compute_managed_ssl_certificate" "skillforge_ssl" {
  name = "skillforge-ssl-${var.environment}"
  
  managed {
    domains = [
      "skillforge-ai.emacsah.com",
      "api.emacsah.com"
    ]
  }
}
```

---

## 📱 **Pages et Routing Frontend**

### **Structure de Pages**

```typescript
// Frontend Routing Structure
const routes = [
  // Pages publiques
  { path: '/', component: LandingPage },           // Page d'accueil
  { path: '/pricing', component: PricingPage },    // Tarification
  { path: '/about', component: AboutPage },        // À propos
  
  // Authentification
  { path: '/auth/login', component: LoginPage },
  { path: '/auth/register', component: RegisterPage },
  
  // Dashboards (protégés)
  { path: '/learner/*', component: LearnerApp },   // Micro-frontend learner
  { path: '/company/*', component: CompanyApp },   // Micro-frontend company
  { path: '/admin/*', component: AdminApp },       // Micro-frontend admin
  
  // Pages utilitaires
  { path: '/404', component: NotFoundPage },
  { path: '*', redirect: '/404' }
];
```

### **Landing Page (Page d'Accueil)**

```typescript
// skillforge-ai.emacsah.com/ → Landing Page
const LandingPage = () => (
  <div>
    <Hero>
      <h1>SkillForge AI - Forge Your Skills</h1>
      <p>Plateforme d'apprentissage et de gestion de talents</p>
      <CTAButtons>
        <Button href="/auth/register">Commencer Gratuitement</Button>
        <Button variant="ghost" href="/auth/login">Se Connecter</Button>
      </CTAButtons>
    </Hero>
    
    <Features />
    <Testimonials />
    <Pricing />
    <Footer />
  </div>
);
```

---

## 🎯 **Bénéfices de Cette Architecture**

### **✅ Avantages Techniques**
1. **Séparation claire** : Frontend ≠ API
2. **Scalabilité** : Chaque service peut scale indépendamment
3. **Sécurité** : CORS configuré entre domaines
4. **Performance** : CDN possible sur frontend
5. **Maintenance** : Déploiements indépendants

### **✅ Avantages Business**
1. **SEO** : skillforge-ai.emacsah.com référençable
2. **Branding** : URL mémorable et professionnelle
3. **Marketing** : Landing page dédiée
4. **Analytics** : Tracking séparé frontend/API

### **✅ Avantages UX**
1. **URL claire** : skillforge-ai.emacsah.com/learner/dashboard
2. **Navigation fluide** : Single Page Application
3. **Bookmarks** : URLs spécifiques par fonctionnalité
4. **Partage** : Links directs vers fonctionnalités

---

## 🚀 **Plan d'Implémentation**

### **Phase 1 : Configuration DNS (1 jour)**
```bash
# 1. Ajouter DNS Record
gcloud dns record-sets transaction start --zone=emacsah-com-zone
gcloud dns record-sets transaction add 34.149.174.205 \
  --name=skillforge-ai.emacsah.com. --ttl=300 --type=A \
  --zone=emacsah-com-zone
gcloud dns record-sets transaction execute --zone=emacsah-com-zone

# 2. Tester résolution
nslookup skillforge-ai.emacsah.com
```

### **Phase 2 : Certificat SSL (1 jour)**
```bash
# Mise à jour certificat pour inclure nouveau domaine
gcloud compute ssl-certificates create skillforge-multi-ssl \
  --domains=skillforge-ai.emacsah.com,api.emacsah.com \
  --global
```

### **Phase 3 : Load Balancer (2 jours)**
```bash
# Mise à jour Terraform avec double routing
terraform plan -var-file=environments/staging/terraform.tfvars
terraform apply
```

### **Phase 4 : Déploiement Frontend (3 jours)**
```bash
# Build et déploiement micro-frontends
npm run build:all
docker build -t skillforge-frontend-shell .
gcloud run deploy skillforge-frontend-shell \
  --image=gcr.io/skillforge-ai-mvp-25/skillforge-frontend-shell \
  --region=europe-west1
```

---

## ⚠️ **Points d'Attention**

### **1. CORS Configuration**
```typescript
// Backend CORS pour nouveau domaine
const corsOptions = {
  origin: [
    'https://skillforge-ai.emacsah.com',
    'https://api.emacsah.com',
    'http://localhost:3000'  // Dev
  ],
  credentials: true
};
```

### **2. Cookies/JWT**
```typescript
// Configuration cookies cross-domain
const jwtConfig = {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  domain: '.emacsah.com'  // Permet partage entre sous-domaines
};
```

### **3. Monitoring/Logging**
```yaml
# Séparation logs par service
logs:
  frontend:
    - skillforge-ai.emacsah.com/*
  api:
    - api.emacsah.com/*
```

---

## 📊 **Métriques à Surveiller**

### **Frontend (skillforge-ai.emacsah.com)**
- Page load time
- Bounce rate
- Conversion rate (landing → signup)
- User journey analytics

### **API (api.emacsah.com)**  
- Response time
- Error rate
- Throughput
- Uptime

---

## 🎯 **Conclusion & Recommandation**

### ✅ **RECOMMANDATION FORTE**

**OUI, utilisez skillforge-ai.emacsah.com comme domaine principal !**

Cette configuration vous donne :
- 🎨 **Branding professionnel** avec identité claire
- 🏗️ **Architecture scalable** frontend/backend séparés  
- 🔒 **Sécurité optimale** avec isolation des services
- 📈 **SEO-friendly** pour référencement naturel
- 🚀 **Évolutivité** pour futurs services

### **Timeline**
- **Semaine 1** : Configuration DNS + SSL
- **Semaine 2** : Mise à jour Load Balancer  
- **Semaine 3** : Déploiement Frontend
- **Semaine 4** : Tests & optimisations

Votre architecture sera alors **production-ready** avec une séparation claire des responsabilités et une excellente expérience utilisateur !

---

*Rapport généré pour optimiser l'architecture domaines SkillForge AI*