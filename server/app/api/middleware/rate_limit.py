import time
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from app.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = defaultdict(list)
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip] 
            if current_time - timestamp < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.request_counts[client_ip]) >= self.rate_limit:
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                media_type="text/plain"
            )
        
        # Add current request timestamp
        self.request_counts[client_ip].append(current_time)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        requests_remaining = self.rate_limit - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(requests_remaining)
        
        return response