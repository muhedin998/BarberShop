"""
Middleware for automatic site management
"""
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .site_utils import get_site_id_for_domain, ensure_site_exists
import logging

logger = logging.getLogger(__name__)


class DynamicSiteMiddleware:
    """
    Middleware that automatically sets the current site based on the request domain
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the domain from the request
        host = request.META.get('HTTP_HOST', '')
        if host:
            # Remove port if present
            domain = host.split(':')[0]
            
            # Get the appropriate site ID for this domain
            site_id = get_site_id_for_domain(domain)
            
            # Ensure the site exists
            site = ensure_site_exists(site_id)
            
            if site:
                # Set the site for this request
                request._current_site_cache = site
                logger.debug(f"Set current site to {site.domain} (ID: {site.id}) for request to {host}")
            else:
                logger.warning(f"Could not ensure site exists for domain {domain}")

        response = self.get_response(request)
        return response


class EnsureSitesExistMiddleware:
    """
    Middleware that ensures all required sites exist on startup
    This runs once when the server starts
    """
    _sites_checked = False
    
    def __init__(self, get_response):
        self.get_response = get_response
        if not EnsureSitesExistMiddleware._sites_checked:
            self._ensure_sites_exist()
            EnsureSitesExistMiddleware._sites_checked = True

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def _ensure_sites_exist(self):
        """
        Ensure all required sites exist in the database
        """
        from .site_utils import ensure_all_sites_exist
        try:
            ensure_all_sites_exist()
            logger.info("Site existence check completed")
        except Exception as e:
            logger.error(f"Failed to ensure sites exist: {e}")

class SiteDebugMiddleware:
    """
    Debug middleware to log site information
    Only use in development
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            try:
                current_site = get_current_site(request)
                logger.debug(f"Current site: {current_site.domain} (ID: {current_site.id})")
            except Exception as e:
                logger.debug(f"Could not get current site: {e}")
        
        response = self.get_response(request)
        return response