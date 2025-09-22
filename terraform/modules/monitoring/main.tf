# Monitoring Module for SkillForge AI
# Creates dashboards and alerts for backend services

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Dashboard for User Service
resource "google_monitoring_dashboard" "user_service_dashboard" {
  dashboard_json = jsonencode({
    displayName = "SkillForge AI - User Service Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "HTTP Request Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_http_requests_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.method", "metric.label.status_code"]
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Requests per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "HTTP Request Duration (95th percentile)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_http_request_duration_seconds/histogram\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_DELTA"
                      crossSeriesReducer = "REDUCE_PERCENTILE_95"
                      groupByFields = ["metric.label.method", "metric.label.endpoint"]
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Duration (seconds)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          yPos   = 4
          widget = {
            title = "Error Rate by Endpoint"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_errors_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.endpoint", "metric.label.error_type"]
                    }
                  }
                }
                plotType = "STACKED_BAR"
              }]
              yAxis = {
                label = "Errors per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 4
          widget = {
            title = "Database Operations"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_db_operations_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.operation", "metric.label.status"]
                    }
                  }
                }
                plotType = "STACKED_AREA"
              }]
              yAxis = {
                label = "Operations per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 4
          height = 4
          yPos   = 8
          widget = {
            title = "Active Users"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"prometheus.googleapis.com/skillforge_users_total/gauge\" resource.type=\"k8s_container\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields = ["metric.label.status"]
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
            }
          }
        },
        {
          width  = 4
          height = 4
          xPos   = 4
          yPos   = 8
          widget = {
            title = "Cache Hit Ratio"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"prometheus.googleapis.com/skillforge_cache_hit_ratio/gauge\" resource.type=\"k8s_container\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              gaugeView = {
                lowerBound = 0.0
                upperBound = 1.0
              }
            }
          }
        },
        {
          width  = 4
          height = 4
          xPos   = 8
          yPos   = 8
          widget = {
            title = "Authentication Events"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_auth_attempts_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.type", "metric.label.status"]
                    }
                  }
                }
                plotType = "STACKED_BAR"
              }]
              yAxis = {
                label = "Auth attempts per second"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
}

# Dashboard for Company Service
resource "google_monitoring_dashboard" "company_service_dashboard" {
  dashboard_json = jsonencode({
    displayName = "SkillForge AI - Company Service Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Company Service - HTTP Requests"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_company_http_requests_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.method", "metric.label.status_code"]
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Requests per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "API Gateway Integration"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_company_api_gateway_requests_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.gateway_endpoint"]
                    }
                  }
                }
                plotType = "STACKED_AREA"
              }]
              yAxis = {
                label = "Gateway requests per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          yPos   = 4
          widget = {
            title = "Company Registrations"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"prometheus.googleapis.com/skillforge_company_registrations_total/counter\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod  = "300s"
                      perSeriesAligner = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields = ["metric.label.size", "metric.label.industry"]
                    }
                  }
                }
                plotType = "STACKED_BAR"
              }]
              yAxis = {
                label = "Registrations per 5min"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 4
          widget = {
            title = "Companies by Size and Status"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"prometheus.googleapis.com/skillforge_companies_total/gauge\" resource.type=\"k8s_container\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields = ["metric.label.size", "metric.label.status"]
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_BAR"
              }
            }
          }
        }
      ]
    }
  })
}

# Alert Policy - High Error Rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "SkillForge AI - High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "High HTTP Error Rate"
    
    condition_threshold {
      filter          = "metric.type=\"prometheus.googleapis.com/skillforge_http_requests_total/counter\" AND metric.label.status_code>=\"400\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 10
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = ["resource.label.container_name"]
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy - High Response Time
resource "google_monitoring_alert_policy" "high_response_time" {
  display_name = "SkillForge AI - High Response Time"
  combiner     = "OR"
  
  conditions {
    display_name = "High HTTP Response Time (95th percentile)"
    
    condition_threshold {
      filter          = "metric.type=\"prometheus.googleapis.com/skillforge_http_request_duration_seconds/histogram\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 2.0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
        group_by_fields = ["resource.label.container_name"]
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy - Service Down
resource "google_monitoring_alert_policy" "service_down" {
  display_name = "SkillForge AI - Service Down"
  combiner     = "OR"
  
  conditions {
    display_name = "Service Health Check Failed"
    
    condition_absent {
      filter   = "metric.type=\"prometheus.googleapis.com/up\" AND metric.label.job=~\"(user-service|company-service)\""
      duration = "180s"
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_COUNT"
        group_by_fields = ["metric.label.job"]
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "300s"
  }
}

# Alert Policy - Database Issues
resource "google_monitoring_alert_policy" "database_issues" {
  display_name = "SkillForge AI - Database Issues"
  combiner     = "OR"
  
  conditions {
    display_name = "High Database Error Rate"
    
    condition_threshold {
      filter          = "metric.type=\"prometheus.googleapis.com/skillforge_db_operations_total/counter\" AND metric.label.status=\"error\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 5
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = ["resource.label.container_name"]
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy - Cache Issues
resource "google_monitoring_alert_policy" "cache_issues" {
  display_name = "SkillForge AI - Cache Performance"
  combiner     = "OR"
  
  conditions {
    display_name = "Low Cache Hit Ratio"
    
    condition_threshold {
      filter          = "metric.type=\"prometheus.googleapis.com/skillforge_cache_hit_ratio/gauge\""
      duration        = "600s"
      comparison      = "COMPARISON_LESS_THAN"
      threshold_value = 0.7
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy - Authentication Issues
resource "google_monitoring_alert_policy" "auth_issues" {
  display_name = "SkillForge AI - Authentication Issues"
  combiner     = "OR"
  
  conditions {
    display_name = "High Authentication Failure Rate"
    
    condition_threshold {
      filter          = "metric.type=\"prometheus.googleapis.com/skillforge_auth_attempts_total/counter\" AND metric.label.status=\"failure\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 20
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# SLO for API Availability
resource "google_monitoring_slo" "api_availability" {
  count        = var.enable_slos ? 1 : 0
  service      = var.service_id
  display_name = "API Availability SLO"
  goal         = 0.99
  
  request_based_sli {
    good_total_ratio {
      total_service_filter = "metric.type=\"prometheus.googleapis.com/skillforge_http_requests_total/counter\""
      good_service_filter  = "metric.type=\"prometheus.googleapis.com/skillforge_http_requests_total/counter\" AND metric.label.status_code<\"400\""
    }
  }
  
  rolling_period_days = 30
}

# SLO for API Latency
resource "google_monitoring_slo" "api_latency" {
  count        = var.enable_slos ? 1 : 0
  service      = var.service_id
  display_name = "API Latency SLO"
  goal         = 0.95
  
  request_based_sli {
    distribution_cut {
      distribution_filter = "metric.type=\"prometheus.googleapis.com/skillforge_http_request_duration_seconds/histogram\""
      range {
        max = 1.0
      }
    }
  }
  
  rolling_period_days = 30
}