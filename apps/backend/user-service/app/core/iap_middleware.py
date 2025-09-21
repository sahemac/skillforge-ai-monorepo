"""
Google IAP (Identity-Aware Proxy) middleware for FastAPI
Handles IAP headers and authentication validation
"""

import logging
import json
import base64
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import httpx

logger = logging.getLogger(__name__)


class IAPMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Google IAP authentication headers."""
    
    def __init__(self, app, project_number: str, backend_service_id: str):
        super().__init__(app)
        self.project_number = project_number
        self.backend_service_id = backend_service_id
        self.expected_audience = f"/projects/{project_number}/global/backendServices/{backend_service_id}"
        self.public_keys = {}
        logger.info(f"IAP Middleware initialized for audience: {self.expected_audience}")
    
    async def dispatch(self, request: Request, call_next):
        """Process IAP headers if present."""
        
        # Skip IAP validation for health checks and metrics (common bypass endpoints)
        if request.url.path in ["/health", "/metrics", "/"]:
            logger.debug(f"Skipping IAP validation for health endpoint: {request.url.path}")
            return await call_next(request)
        
        # Get IAP headers
        iap_jwt = request.headers.get("x-goog-iap-jwt-assertion")
        
        if not iap_jwt:
            logger.warning("No IAP JWT header found - allowing request (Load Balancer should enforce IAP)")
            # For health checks and when IAP is properly configured at Load Balancer level
            return await call_next(request)
        
        try:
            # Validate IAP JWT
            user_info = await self.validate_iap_jwt(iap_jwt)
            if user_info:
                # Add user info to request state for use in endpoints
                request.state.iap_user = user_info
                logger.info(f"IAP authentication successful for user: {user_info.get('email', 'unknown')}")
            else:
                logger.error("IAP JWT validation failed")
                raise HTTPException(status_code=403, detail="IAP authentication failed")
                
        except Exception as e:
            logger.error(f"IAP validation error: {str(e)}")
            # In staging, log but allow - in production, reject
            if request.app.state.environment == "production":
                raise HTTPException(status_code=403, detail="Authentication required")
        
        return await call_next(request)
    
    async def validate_iap_jwt(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """Validate IAP JWT token."""
        try:
            # Decode header to get key ID
            header = jwt.get_unverified_header(jwt_token)
            key_id = header.get("kid")
            
            if not key_id:
                logger.error("No key ID found in JWT header")
                return None
            
            # Get public key for verification
            public_key = await self.get_public_key(key_id)
            if not public_key:
                logger.error(f"Could not retrieve public key for key ID: {key_id}")
                return None
            
            # Verify and decode JWT
            payload = jwt.decode(
                jwt_token,
                public_key,
                algorithms=["ES256"],
                audience=self.expected_audience,
                issuer="https://cloud.google.com/iap"
            )
            
            logger.info(f"IAP JWT validated successfully for user: {payload.get('email', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.error("IAP JWT token has expired")
            return None
        except jwt.InvalidAudienceError:
            logger.error(f"IAP JWT audience mismatch. Expected: {self.expected_audience}")
            return None
        except jwt.InvalidIssuerError:
            logger.error("IAP JWT issuer invalid")
            return None
        except Exception as e:
            logger.error(f"IAP JWT validation error: {str(e)}")
            return None
    
    async def get_public_key(self, key_id: str):
        """Fetch Google's public keys for IAP verification."""
        try:
            if key_id not in self.public_keys:
                # Fetch keys from Google
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://www.gstatic.com/iap/verify/public_key",
                        timeout=10.0
                    )
                    response.raise_for_status()
                    
                    keys_data = response.json()
                    
                    # Parse and store the key
                    if key_id in keys_data:
                        key_data = keys_data[key_id]
                        # Convert PEM to public key object
                        public_key = serialization.load_pem_public_key(
                            key_data.encode('utf-8')
                        )
                        self.public_keys[key_id] = public_key
                        logger.info(f"Retrieved and cached public key: {key_id}")
                    else:
                        logger.error(f"Key ID {key_id} not found in Google's public keys")
                        return None
            
            return self.public_keys.get(key_id)
            
        except Exception as e:
            logger.error(f"Error fetching public key {key_id}: {str(e)}")
            return None


def get_iap_user_info(request: Request) -> Optional[Dict[str, Any]]:
    """Helper function to get IAP user info from request."""
    return getattr(request.state, 'iap_user', None)


def get_user_email(request: Request) -> Optional[str]:
    """Helper function to get user email from IAP."""
    user_info = get_iap_user_info(request)
    return user_info.get('email') if user_info else None


def require_iap_auth(request: Request) -> Dict[str, Any]:
    """Helper function to require IAP authentication."""
    user_info = get_iap_user_info(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_info