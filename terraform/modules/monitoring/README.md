# SkillForge AI Monitoring Module

This Terraform module creates comprehensive monitoring for the SkillForge AI backend services using Google Cloud Monitoring and Prometheus metrics.

## Features

### Dashboards
- **User Service Dashboard**: HTTP metrics, database operations, authentication events, cache performance
- **Company Service Dashboard**: API Gateway integration, company registrations, business metrics

### Alert Policies
- High error rate alerts (>10 errors/sec by default)
- High response time alerts (>2s for 95th percentile)
- Service availability monitoring
- Database error rate monitoring
- Cache performance alerts (hit ratio <70%)
- Authentication failure rate alerts

### SLOs (Service Level Objectives)
- API Availability: 99% uptime target
- API Latency: 95% of requests under 1 second

## Usage

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  project_id     = var.project_id
  environment    = var.environment
  service_id     = "your-service-id"
  
  notification_channels = [
    "projects/your-project/notificationChannels/channel-id"
  ]
  
  # Optional: Customize thresholds
  error_rate_threshold     = 15
  response_time_threshold  = 3.0
  cache_hit_ratio_threshold = 0.8
}
```

## Prerequisites

1. **Prometheus Metrics**: Services must expose Prometheus metrics on `/metrics` endpoint
2. **Google Cloud Monitoring API**: Must be enabled in your project
3. **Notification Channels**: Create notification channels for alerts (email, Slack, PagerDuty, etc.)

## Metrics Expected

The module expects the following Prometheus metrics from your services:

### User Service Metrics
- `skillforge_http_requests_total` - HTTP request counter
- `skillforge_http_request_duration_seconds` - HTTP request duration histogram
- `skillforge_errors_total` - Error counter
- `skillforge_db_operations_total` - Database operation counter
- `skillforge_auth_attempts_total` - Authentication attempt counter
- `skillforge_users_total` - User count gauge
- `skillforge_cache_hit_ratio` - Cache hit ratio gauge

### Company Service Metrics
- `skillforge_company_http_requests_total` - HTTP request counter
- `skillforge_company_api_gateway_requests_total` - API Gateway request counter
- `skillforge_company_registrations_total` - Company registration counter
- `skillforge_companies_total` - Company count gauge

## Alert Thresholds

Default alert thresholds can be customized via variables:

| Alert | Default Threshold | Variable |
|-------|------------------|----------|
| Error Rate | 10 errors/sec | `error_rate_threshold` |
| Response Time | 2.0 seconds | `response_time_threshold` |
| Cache Hit Ratio | 70% | `cache_hit_ratio_threshold` |
| Auth Failures | 20 failures/sec | `auth_failure_threshold` |
| DB Errors | 5 errors/sec | `db_error_threshold` |

## Outputs

- `user_service_dashboard_id` - Dashboard ID for User Service
- `company_service_dashboard_id` - Dashboard ID for Company Service
- `alert_policy_ids` - Map of alert policy names to IDs
- `slo_ids` - Map of SLO names to IDs
- `dashboard_urls` - Direct URLs to access dashboards

## Implementation Guide

1. **Deploy the module**:
   ```bash
   terraform apply
   ```

2. **Verify metrics collection**:
   - Check that your services expose metrics at `/metrics`
   - Verify Prometheus is scraping your services
   - Confirm metrics appear in Google Cloud Monitoring

3. **Test alerts**:
   - Generate test traffic to trigger thresholds
   - Verify notifications are sent to configured channels

4. **Customize dashboards**:
   - Use the Google Cloud Console to modify dashboard layouts
   - Add additional metrics as needed

## Troubleshooting

### Metrics Not Appearing
- Verify `/metrics` endpoint is accessible
- Check Prometheus configuration for service discovery
- Ensure Google Cloud Monitoring API is enabled

### Alerts Not Firing
- Check alert policy conditions match your metric labels
- Verify notification channels are correctly configured
- Review alert history in Google Cloud Console

### Dashboard Issues
- Confirm metric names match between services and dashboard queries
- Check time range and aggregation settings
- Verify resource labels are consistent

## Cost Considerations

- Dashboard storage: Minimal cost
- Alert policies: First 5 policies free, then $0.50/policy/month
- SLOs: Included with Google Cloud Operations suite
- Metric ingestion: Based on volume, typically low for application metrics

## Security

- Dashboards are private to your Google Cloud project
- Alert policies respect IAM permissions
- Metrics are transmitted over HTTPS
- No sensitive data should be included in metric labels