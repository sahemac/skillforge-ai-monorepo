# Cloud SQL Private IP Configuration Solution

## Problem Identified

Your Cloud SQL instance `skillforge-pg-instance-staging` is configured with:
- `ipv4_enabled = false` (no public IP)
- `private_network = "projects/skillforge-ai-mvp-25/global/networks/skillforge-vpc-staging"`

This means cloud-sql-proxy cannot connect using public IP mode, causing the error:
```
instance does not have IP of type "PUBLIC"
```

## Solution Options

### Option 1: Enable Public IP (Temporary - for Development)

**Quick Fix for Local Development:**

1. Edit terraform configuration:
```bash
# File: terraform/environments/staging/database.tf
# Change line 24 from:
ipv4_enabled = false
# To:
ipv4_enabled = true
```

2. Apply terraform changes:
```bash
cd terraform/environments/staging
terraform plan
terraform apply
```

3. Start cloud-sql-proxy (original command will work):
```bash
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging=tcp:5432
```

4. Test connection:
```bash
cd apps/backend/user-service
python test_simple_connectivity.py
```

### Option 2: Private IP Mode (Requires VPC Access)

**For Private Network Access:**

1. Use private IP mode:
```bash
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging=tcp:5432 -ip_address_types=PRIVATE
```

**Note:** This requires your local machine to have VPC network access, which is complex for local development.

### Option 3: Cloud-Based Development (Recommended)

**Deploy to Cloud Run with VPC Connector:**

The existing terraform already includes a VPC connector (`skillforge-vpc-connector-staging`). When you deploy to Cloud Run, it will automatically have private network access.

## Immediate Action Required

**For Local Development (Recommended):**

1. **Enable Public IP temporarily:**
```bash
cd terraform/environments/staging
```

2. **Edit database.tf:**
```diff
  ip_configuration {
-   ipv4_enabled    = false
+   ipv4_enabled    = true
    private_network = google_compute_network.vpc_main.id
  }
```

3. **Apply changes:**
```bash
terraform plan
terraform apply
```

4. **Restart cloud-sql-proxy:**
```bash
# Stop current proxy (Ctrl+C)
# Start with correct instance name:
.\cloud-sql-proxy.exe --port=5432 skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging
```

5. **Test validation:**
```bash
cd apps/backend/user-service
python test_simple_connectivity.py
python validate_service_simple.py
```

## Security Considerations

**Public IP Warning:**
- Enabling public IP temporarily is acceptable for development
- For production, keep `ipv4_enabled = false` and use private networking
- Consider adding authorized networks if public IP is needed

**Current Status:**
- ✅ Cloud SQL proxy installed and running
- ✅ Authentication working (using Application Default Credentials)  
- ❌ IP configuration mismatch (private instance, public connection attempt)

## Expected Results After Fix

```
DIAGNOSTIC RESULTS
Duration: 1.23s
Tests passed: 4/4

SUCCESS - All tests passed!
cloud-sql-proxy is working correctly
You can now run the full validation
```

## Files Updated

- `test_simple_connectivity.py` - Updated instance name to `skillforge-pg-instance-staging`
- `validate_service_simple.py` - Added comments about instance name
- This solution document created

## Next Steps

1. Apply the terraform change (Option 1)
2. Restart cloud-sql-proxy with correct command
3. Run diagnostic: `python test_simple_connectivity.py`
4. Run validation: `python validate_service_simple.py`
5. Once working, proceed with full validation: `python validate_service.py`