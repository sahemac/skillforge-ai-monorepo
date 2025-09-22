# Outputs for monitoring module

output "user_service_dashboard_id" {
  description = "ID of the user service dashboard"
  value       = google_monitoring_dashboard.user_service_dashboard.id
}

output "company_service_dashboard_id" {
  description = "ID of the company service dashboard"
  value       = google_monitoring_dashboard.company_service_dashboard.id
}

output "alert_policy_ids" {
  description = "Map of alert policy names to their IDs"
  value = {
    high_error_rate  = google_monitoring_alert_policy.high_error_rate.id
    high_response_time = google_monitoring_alert_policy.high_response_time.id
    service_down     = google_monitoring_alert_policy.service_down.id
    database_issues  = google_monitoring_alert_policy.database_issues.id
    cache_issues     = google_monitoring_alert_policy.cache_issues.id
    auth_issues      = google_monitoring_alert_policy.auth_issues.id
  }
}

output "slo_ids" {
  description = "Map of SLO names to their IDs"
  value = var.enable_slos ? {
    api_availability = google_monitoring_slo.api_availability[0].id
    api_latency      = google_monitoring_slo.api_latency[0].id
  } : {}
}

output "dashboard_urls" {
  description = "URLs to access the monitoring dashboards"
  value = {
    user_service = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.user_service_dashboard.id}?project=${var.project_id}"
    company_service = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.company_service_dashboard.id}?project=${var.project_id}"
  }
}