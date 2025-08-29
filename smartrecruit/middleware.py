"""
Custom Security Middlewares for SmartRecruit
"""

import time
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Additional security headers
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
            
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware to prevent abuse
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Rate limiting for login attempts
        if request.path.startswith('/api-auth/login/') or request.path.startswith('/admin/login/'):
            return self.check_login_rate_limit(ip)
        
        # Rate limiting for API requests
        if request.path.startswith('/api/'):
            return self.check_api_rate_limit(ip)
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_login_rate_limit(self, ip):
        """Check rate limit for login attempts"""
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 5:  # Max 5 login attempts per hour
            logger.warning(f'Rate limit exceeded for login attempts from IP: {ip}')
            return HttpResponseForbidden('Too many login attempts. Please try again later.')
        
        # Increment counter
        cache.set(cache_key, attempts + 1, 3600)  # 1 hour timeout
        return None
    
    def check_api_rate_limit(self, ip):
        """Check rate limit for API requests"""
        cache_key = f'api_requests_{ip}'
        requests = cache.get(cache_key, 0)
        
        if requests >= 1000:  # Max 1000 API requests per hour
            logger.warning(f'Rate limit exceeded for API requests from IP: {ip}')
            return HttpResponseForbidden('API rate limit exceeded. Please try again later.')
        
        # Increment counter
        cache.set(cache_key, requests + 1, 3600)  # 1 hour timeout
        return None


class SecurityAuditMiddleware(MiddlewareMixin):
    """
    Middleware to log security-related events
    """
    
    def process_request(self, request):
        # Log suspicious patterns
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for common attack patterns
        suspicious_patterns = [
            'sqlmap', 'nikto', 'nessus', 'burp', 'nmap',
            'script', 'alert', 'onload', 'onerror'
        ]
        
        query_string = request.META.get('QUERY_STRING', '').lower()
        path = request.path.lower()
        
        for pattern in suspicious_patterns:
            if pattern in user_agent.lower() or pattern in query_string or pattern in path:
                logger.warning(
                    f'Suspicious request detected from {self.get_client_ip(request)}: '
                    f'Path: {request.path}, UA: {user_agent}, Query: {query_string}'
                )
                break
        
        # Log file upload attempts
        if request.FILES:
            logger.info(
                f'File upload from {self.get_client_ip(request)}: '
                f'Files: {list(request.FILES.keys())}'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests (> 2 seconds)
            if duration > 2.0:
                logger.warning(
                    f'Slow request detected: {request.method} {request.path} '
                    f'took {duration:.2f}s from {self.get_client_ip(request)}'
                )
            
            # Add performance header for debugging
            if settings.DEBUG:
                response['X-Response-Time'] = f'{duration:.3f}s'
        
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
