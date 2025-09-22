"""
IAP middleware for AI Orchestrator Service
"""

from starlette.middleware.base import BaseHTTPMiddleware

class IAPMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, project_number: str, backend_service_id: str):
        super().__init__(app)
        self.project_number = project_number
        self.backend_service_id = backend_service_id
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response