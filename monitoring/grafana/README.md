# 📊 SkillForge AI - Configuration Grafana

**Date**: 2025-01-23  
**Auteur**: Kouemou Sah Jean Emac  
**Grafana Account**: sahemac.grafana.net  
**GitHub Integration**: ✅ Ready

---

## 🎯 CONFIGURATION GRAFANA CLOUD

### **Account Details**
```yaml
Grafana Cloud URL: https://sahemac.grafana.net
GitHub Integration: Configured
Project: SkillForge AI Monitoring
Environment: Staging + Production
```

### **Service Account Setup**

#### **1. Créer Service Account pour Google Cloud**
```bash
# Créer service account pour monitoring
gcloud iam service-accounts create grafana-monitoring \
  --display-name="Grafana Cloud Monitoring" \
  --project=skillforge-ai-mvp-25

# Assigner les rôles nécessaires
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
  --member="serviceAccount:grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
  --role="roles/monitoring.viewer"

gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
  --member="serviceAccount:grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
  --role="roles/logging.viewer"

gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
  --member="serviceAccount:grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

# Générer clé JSON
gcloud iam service-accounts keys create grafana-sa-key.json \
  --iam-account=grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

### **Data Sources Configuration**

#### **Google Cloud Monitoring**
```yaml
Type: Google Cloud Monitoring
Authentication: Service Account Key (JSON)
Project ID: skillforge-ai-mvp-25
Default Region: europe-west1

Metrics à surveiller:
  - Cloud Run metrics (CPU, Memory, Latency)
  - Load Balancer metrics (Request count, Error rate)
  - Database metrics (Connections, Query time)
  - Custom application metrics
```

#### **Google Cloud Logging**
```yaml
Type: Google Cloud Logging  
Authentication: Service Account Key (JSON)
Project ID: skillforge-ai-mvp-25

Logs à surveiller:
  - Cloud Run application logs
  - Load Balancer access logs
  - Database audit logs
  - IAP authentication logs
```

---

## 📈 DASHBOARDS CONFIGURATION

### **1. Infrastructure Dashboard**

#### **Cloud Run Performance**
```yaml
Panels:
  - CPU Utilization (user-service-staging)
  - Memory Usage (user-service-staging)  
  - Request Count per minute
  - Response Time (P50, P95, P99)
  - Error Rate percentage
  - Instance Count (min/max/current)

Alerts:
  - CPU > 80% for 5 minutes
  - Memory > 85% for 5 minutes
  - Error rate > 5% for 2 minutes
  - Response time P95 > 500ms for 3 minutes
```

#### **Load Balancer Metrics**
```yaml
Panels:
  - Request Count by domain (api.emacsah.com, skillforge-ai.emacsah.com)
  - Backend Health Status
  - SSL Certificate Status
  - Geographic Request Distribution
  - Cache Hit Ratio (if CDN enabled)

Alerts:
  - Backend health check failures
  - SSL certificate expiring in 30 days
  - Request volume spike (>200% normal)
```

### **2. Application Dashboard**

#### **Business Metrics**
```yaml
Panels:
  - API Endpoint Performance (/health, /api/v1/*)
  - Database Connection Pool Status
  - Authentication Success/Failure Rate
  - User Activity Metrics
  - Feature Usage Statistics

Custom Metrics (à implémenter):
  - User registrations per hour
  - Project submissions per day
  - Evaluation completions per hour
  - AI agent invocations per minute
```

#### **Database Performance**
```yaml
Panels:
  - PostgreSQL Connection Count
  - Query Execution Time
  - Active/Idle Connections
  - Database Size Growth
  - Slow Query Detection

Alerts:
  - Connection pool exhaustion
  - Query time > 1 second
  - Database size growth > 1GB/day
```

### **3. Security Dashboard**

#### **IAP Monitoring**
```yaml
Panels:
  - Authentication Attempts (Success/Failure)
  - User Sessions Duration
  - Geographic Access Patterns
  - Suspicious Activity Detection

Alerts:
  - Failed authentication > 10 attempts/minute
  - New geographic location access
  - Session duration anomalies
```

---

## 🚨 ALERTING CONFIGURATION

### **Alert Channels**
```yaml
Email: sah@emacsah.com
Slack: #skillforge-alerts (if configured)
PagerDuty: Critical alerts only
```

### **Alert Rules**

#### **Critical Alerts (P0)**
```yaml
- Service Down (Cloud Run not responding)
  Condition: Health check failures for 2 minutes
  
- Database Connection Loss
  Condition: No successful DB connections for 1 minute
  
- SSL Certificate Expired
  Condition: Certificate expired or expiring in 24h
  
- High Error Rate
  Condition: >10% error rate for 3 minutes
```

#### **Warning Alerts (P1)**
```yaml
- High Response Time
  Condition: P95 latency > 1 second for 5 minutes
  
- High Resource Usage
  Condition: CPU > 80% or Memory > 85% for 10 minutes
  
- Authentication Issues
  Condition: IAP failures > 5% for 5 minutes
```

#### **Info Alerts (P2)**
```yaml
- Deployment Events
  Condition: New Cloud Run revision deployed
  
- Configuration Changes
  Condition: Load Balancer or IAP settings modified
  
- Resource Scaling
  Condition: Instance count changes
```

---

## 🔧 IMPLEMENTATION STEPS

### **Phase 1: Service Account Setup (15 min)**
1. Créer service account `grafana-monitoring`
2. Assigner les rôles monitoring/logging
3. Générer et télécharger la clé JSON
4. Configurer dans Grafana Cloud

### **Phase 2: Data Sources (20 min)**
1. Ajouter Google Cloud Monitoring data source
2. Ajouter Google Cloud Logging data source
3. Tester la connectivité
4. Configurer les refresh intervals

### **Phase 3: Dashboards Import (30 min)**
1. Importer dashboards GCP standard
2. Personnaliser pour SkillForge AI
3. Ajouter custom panels
4. Configurer variables et templating

### **Phase 4: Alerting Setup (25 min)**
1. Configurer notification channels
2. Créer alert rules
3. Tester alerting workflow
4. Documenter escalation procedures

---

## 🎯 MONITORING STRATEGY

### **SLIs (Service Level Indicators)**
```yaml
Availability: 99.9% uptime
Latency: P95 < 200ms for API calls
Error Rate: < 1% of requests
Throughput: Handle 1000 RPS peak load
```

### **SLOs (Service Level Objectives)**
```yaml
Monthly Uptime: 99.9%
API Response Time: 95% of requests < 200ms
Error Budget: 0.1% (43.2 minutes/month)
Recovery Time: < 5 minutes for P0 incidents
```

### **Monitoring Coverage**
```yaml
Infrastructure: 100% (Cloud Run, Load Balancer, DB)
Application: 90% (API endpoints, business logic)
Security: 100% (IAP, authentication, access logs)
Business: 80% (user metrics, feature usage)
```

---

## 📊 DASHBOARD URLS

```yaml
Main Infrastructure: https://sahemac.grafana.net/d/skillforge-infra
Application Performance: https://sahemac.grafana.net/d/skillforge-app
Security Monitoring: https://sahemac.grafana.net/d/skillforge-security
Business Metrics: https://sahemac.grafana.net/d/skillforge-business
```

---

**Auteur**: Kouemou Sah Jean Emac  
**Date**: 2025-01-23  
**Version**: 1.0 - Configuration Grafana Complete  
**Status**: Ready for Implementation