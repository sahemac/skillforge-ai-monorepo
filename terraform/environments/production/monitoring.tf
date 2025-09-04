# terraform/environments/staging/monitoring.tf

# Canal de notification par email
resource "google_monitoring_notification_channel" "email_alerts" {
  count        = var.enable_monitoring_alerts && var.monitoring_notification_email != "" ? 1 : 0
  display_name = "DevOps Email Alerts - ${title(var.environment)}"
  type         = "email"
  
  labels = {
    email_address = var.monitoring_notification_email
  }
}

# Crée un tableau de bord de base pour SkillForge
resource "google_monitoring_dashboard" "skillforge_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    "displayName" : "SkillForge AI - ${title(var.environment)} Dashboard",
    "mosaicLayout" : {
      "columns" : "2",
      "tiles" : [
        {
          "yPos" : 0,
          "xPos" : 0,
          "width" : 2,
          "height" : 2,  # ✅ CORRIGÉ : Changé de 1 à 2 (minimum requis)
          "widget" : {
            "title" : "Cloud Run - Request Count (per service)",
            "xyChart" : {
              "dataSets" : [
                {
                  "timeSeriesQuery" : {
                    "timeSeriesFilter" : {
                      "filter" : "metric.type = \"run.googleapis.com/request_count\" resource.type = \"cloud_run_revision\"",
                      "aggregation" : {
                        "perSeriesAligner" : "ALIGN_RATE"
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      ]
    }
  })
}

# Crée une politique d'alerte pour le taux d'erreur 5xx sur Cloud Run
resource "google_monitoring_alert_policy" "high_error_rate" {
  count        = var.enable_monitoring_alerts ? 1 : 0
  project      = var.project_id
  display_name = "High 5xx Error Rate - ${title(var.environment)}"
  combiner     = "OR"
  
  notification_channels = var.monitoring_notification_email != "" ? [google_monitoring_notification_channel.email_alerts[0].name] : []
  
  alert_strategy {
    auto_close = "1800s"  # Auto-close after 30 minutes
  }

  conditions {
    display_name = "Error rate over 5% for 5 minutes"
    condition_threshold {
      filter          = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" metric.label.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      # ✅ AJOUTÉ : Agrégation requise pour les métriques DELTA
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields     = ["resource.label.service_name"]
      }
      
      trigger {
        percent = 100
      }

      # Calcule le ratio par rapport à toutes les requêtes
      denominator_filter = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\""
      
      # ✅ AJOUTÉ : Agrégation pour le dénominateur aussi
      denominator_aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields     = ["resource.label.service_name"]
      }
    }
  }
}