#!/bin/bash
# Universal Alembic Migration Script for SkillForge AI Microservices
# Usage: ./scripts/migrate.sh SERVICE_NAME [ENVIRONMENT]
#
# Arguments:
#   SERVICE_NAME: Name of the microservice (e.g., user-service, company-service)
#   ENVIRONMENT: Target environment (staging, production) - defaults to staging
#
# Environment Variables Required:
#   DATABASE_URL: PostgreSQL connection string
#   GCP_PROJECT_ID: Google Cloud Project ID
#   SERVICE_ACCOUNT_KEY: Base64 encoded service account key (optional)

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly LOG_FILE="/tmp/migrate-${SERVICE_NAME:-unknown}-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${1}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Migration failed with exit code $exit_code"
        log_info "Log file: ${LOG_FILE}"
    fi
    exit $exit_code
}

# Rollback function
rollback_migration() {
    log_warn "Attempting to rollback migration..."
    
    if [[ -n "${BACKUP_REVISION:-}" ]]; then
        log_info "Rolling back to revision: ${BACKUP_REVISION}"
        cd "${SERVICE_DIR}"
        if alembic downgrade "${BACKUP_REVISION}" 2>&1 | tee -a "${LOG_FILE}"; then
            log_success "Rollback completed successfully"
        else
            log_error "Rollback failed! Manual intervention required"
            return 1
        fi
    else
        log_warn "No backup revision found. Cannot perform automatic rollback"
        return 1
    fi
}

# Health check function
health_check() {
    local service_url="${1}"
    local max_attempts=30
    local attempt=1

    log_info "Performing health check on: ${service_url}"

    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "${service_url}/health" >/dev/null 2>&1; then
            log_success "Health check passed (attempt $attempt)"
            return 0
        else
            log_warn "Health check failed (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        fi
    done

    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Validate database connection
validate_database_connection() {
    log_info "Validating database connection..."
    
    if [[ -z "${DATABASE_URL:-}" ]]; then
        log_error "DATABASE_URL environment variable is required"
        return 1
    fi

    # Test database connection using Python
    python3 -c "
import sys
import asyncio
import asyncpg
from urllib.parse import urlparse

async def test_connection():
    try:
        url = '${DATABASE_URL}'
        parsed = urlparse(url)
        
        # Extract connection parameters
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path[1:]  # Remove leading /
        username = parsed.username
        password = parsed.password
        
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        
        # Test query
        result = await conn.fetchval('SELECT version();')
        print(f'Database connection successful: {result[:50]}...')
        
        await conn.close()
        return True
    except Exception as e:
        print(f'Database connection failed: {e}', file=sys.stderr)
        return False

if not asyncio.run(test_connection()):
    sys.exit(1)
" 2>&1 | tee -a "${LOG_FILE}"

    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log_success "Database connection validated"
        return 0
    else
        log_error "Database connection validation failed"
        return 1
    fi
}

# Get current database revision
get_current_revision() {
    cd "${SERVICE_DIR}"
    local current_revision
    current_revision=$(alembic current --verbose 2>/dev/null | grep -E '^[a-f0-9]+' | head -1 | cut -d' ' -f1)
    echo "${current_revision}"
}

# Run Alembic migration
run_migration() {
    log_info "Starting migration for ${SERVICE_NAME}..."
    
    cd "${SERVICE_DIR}"
    
    # Get current revision for potential rollback
    BACKUP_REVISION=$(get_current_revision)
    log_info "Current database revision: ${BACKUP_REVISION:-'(empty)'}"
    
    # Show pending migrations
    log_info "Checking for pending migrations..."
    if ! alembic show head 2>&1 | tee -a "${LOG_FILE}"; then
        log_warn "Could not retrieve migration info"
    fi
    
    # Run the migration
    log_info "Running alembic upgrade head..."
    if alembic upgrade head 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "Migration completed successfully"
        
        # Get new revision
        local new_revision
        new_revision=$(get_current_revision)
        log_info "New database revision: ${new_revision:-'(empty)'}"
        
        return 0
    else
        log_error "Migration failed"
        return 1
    fi
}

# Post-migration validation
post_migration_validation() {
    log_info "Running post-migration validation..."
    
    cd "${SERVICE_DIR}"
    
    # Check if we can connect to database and run basic queries
    python3 -c "
import sys
import asyncio
import asyncpg
from urllib.parse import urlparse

async def validate_migration():
    try:
        url = '${DATABASE_URL}'
        parsed = urlparse(url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        # Check if alembic_version table exists and has data
        result = await conn.fetchval('''
            SELECT version_num FROM alembic_version LIMIT 1
        ''')
        
        if result:
            print(f'Migration validation successful. Current version: {result}')
        else:
            print('Warning: No version found in alembic_version table')
            
        await conn.close()
        return True
    except Exception as e:
        print(f'Post-migration validation failed: {e}', file=sys.stderr)
        return False

if not asyncio.run(validate_migration()):
    sys.exit(1)
" 2>&1 | tee -a "${LOG_FILE}"

    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log_success "Post-migration validation passed"
        return 0
    else
        log_error "Post-migration validation failed"
        return 1
    fi
}

# Main function
main() {
    trap cleanup EXIT
    
    # Parse arguments
    if [[ $# -lt 1 ]]; then
        log_error "Usage: $0 SERVICE_NAME [ENVIRONMENT]"
        log_error "Example: $0 user-service staging"
        exit 1
    fi
    
    readonly SERVICE_NAME="$1"
    readonly ENVIRONMENT="${2:-staging}"
    readonly SERVICE_DIR="${PROJECT_ROOT}/apps/backend/${SERVICE_NAME}"
    
    # Start logging
    log_info "===========================================" 
    log_info "SkillForge AI Migration Script"
    log_info "Service: ${SERVICE_NAME}"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Timestamp: $(date)"
    log_info "Log file: ${LOG_FILE}"
    log_info "==========================================="
    
    # Validate service directory
    if [[ ! -d "${SERVICE_DIR}" ]]; then
        log_error "Service directory not found: ${SERVICE_DIR}"
        exit 1
    fi
    
    # Check for Alembic configuration
    if [[ ! -f "${SERVICE_DIR}/alembic.ini" ]]; then
        log_error "Alembic configuration not found: ${SERVICE_DIR}/alembic.ini"
        exit 1
    fi
    
    # Validate required environment variables
    if [[ -z "${DATABASE_URL:-}" ]]; then
        log_error "DATABASE_URL environment variable is required"
        exit 1
    fi
    
    # Install required Python packages
    log_info "Installing required packages..."
    pip install --quiet alembic asyncpg 2>&1 | tee -a "${LOG_FILE}"
    
    # Step 1: Validate database connection
    if ! validate_database_connection; then
        log_error "Database validation failed"
        exit 1
    fi
    
    # Step 2: Run migration
    if ! run_migration; then
        log_error "Migration failed, attempting rollback..."
        if ! rollback_migration; then
            log_error "Rollback also failed. Manual intervention required!"
            exit 1
        fi
        exit 1
    fi
    
    # Step 3: Post-migration validation
    if ! post_migration_validation; then
        log_error "Post-migration validation failed, attempting rollback..."
        if ! rollback_migration; then
            log_error "Rollback failed after validation error. Manual intervention required!"
            exit 1
        fi
        exit 1
    fi
    
    # Step 4: Health check (if service URL provided)
    if [[ -n "${SERVICE_URL:-}" ]]; then
        if ! health_check "${SERVICE_URL}"; then
            log_warn "Health check failed, but migration completed successfully"
            log_warn "Service may need time to restart or there may be application issues"
        fi
    fi
    
    log_success "===========================================" 
    log_success "Migration completed successfully!"
    log_success "Service: ${SERVICE_NAME}"
    log_success "Environment: ${ENVIRONMENT}"
    log_success "Log file: ${LOG_FILE}"
    log_success "==========================================="
}

# Run main function with all arguments
main "$@"