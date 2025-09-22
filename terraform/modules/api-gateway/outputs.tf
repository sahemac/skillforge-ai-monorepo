# Outputs for API Gateway Test Module

output "api_gateway_url" {
  description = "URL of the deployed API Gateway"
  value       = google_api_gateway_gateway.main.default_hostname
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = google_api_gateway_gateway.main.gateway_id
}

output "api_id" {
  description = "ID of the API"
  value       = google_api_gateway_api.main.api_id
}

output "api_config_id" {
  description = "ID of the API config"
  value       = google_api_gateway_api_config.main.api_config_id
}

output "service_account_email" {
  description = "Email of the API Gateway service account"
  value       = google_service_account.api_gateway.email
}

output "gateway_url_https" {
  description = "Full HTTPS URL of the API Gateway"
  value       = "https://${google_api_gateway_gateway.main.default_hostname}"
}

output "test_endpoints" {
  description = "Test endpoints to verify API Gateway functionality"
  value = {
    health_check     = "https://${google_api_gateway_gateway.main.default_hostname}/health"
    auth_health      = "https://${google_api_gateway_gateway.main.default_hostname}/api/v1/auth/health"
    users_endpoint   = "https://${google_api_gateway_gateway.main.default_hostname}/api/v1/users"
    login_endpoint   = "https://${google_api_gateway_gateway.main.default_hostname}/api/v1/auth/login"
  }
}