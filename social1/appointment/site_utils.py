"""
Site management utilities for automatic domain handling
"""
from django.contrib.sites.models import Site
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Domain to Site ID mapping
DOMAIN_SITE_MAPPING = {
    'frizerskisalonhasko.com': 8,
    'www.frizerskisalonhasko.com': 10,
    'evoluci4n.online': 9,
    'www.evoluci4n.online': 11,
    'localhost': 8,  # Development fallback
    '127.0.0.1': 8,  # Development fallback
    'testserver': 8,  # Testing fallback
}

SITE_CONFIGS = {
    8: {
        'domain': 'frizerskisalonhasko.com',
        'name': 'Frizerski salon Hasko - Primary'
    },
    9: {
        'domain': 'evoluci4n.online', 
        'name': 'Frizerski salon Hasko - Alternative'
    },
    10: {
        'domain': 'www.frizerskisalonhasko.com',
        'name': 'Frizerski salon Hasko - WWW'
    },
    11: {
        'domain': 'www.evoluci4n.online',
        'name': 'Frizerski salon Hasko - WWW Alt'
    }
}


def get_site_id_for_domain(domain):
    """
    Get the appropriate site ID for a given domain
    """
    # Remove port if present
    domain = domain.split(':')[0] if ':' in domain else domain
    return DOMAIN_SITE_MAPPING.get(domain, 8)  # Default to primary site


def ensure_site_exists(site_id, create_if_missing=True):
    """
    Ensure a site exists with the given ID, create if missing
    """
    try:
        site = Site.objects.get(id=site_id)
        return site
    except Site.DoesNotExist:
        if not create_if_missing:
            return None
            
        if site_id in SITE_CONFIGS:
            config = SITE_CONFIGS[site_id]
            try:
                site = Site.objects.create(
                    id=site_id,
                    domain=config['domain'],
                    name=config['name']
                )
                logger.info(f"Created Site ID {site_id}: {config['domain']}")
                return site
            except Exception as e:
                logger.error(f"Failed to create Site ID {site_id}: {e}")
                return None
        else:
            logger.warning(f"No configuration found for Site ID {site_id}")
            return None


def ensure_all_sites_exist():
    """
    Ensure all configured sites exist
    """
    for site_id, config in SITE_CONFIGS.items():
        ensure_site_exists(site_id, create_if_missing=True)


def get_current_site_from_request(request):
    """
    Get the current site based on the request's HTTP_HOST
    """
    if request and hasattr(request, 'META'):
        host = request.META.get('HTTP_HOST', '')
        if host:
            site_id = get_site_id_for_domain(host)
            return ensure_site_exists(site_id)
    
    # Fallback to settings.SITE_ID
    return ensure_site_exists(getattr(settings, 'SITE_ID', 8))


def get_site_url(request=None, site_id=None):
    """
    Get the full URL for a site (with protocol)
    """
    if site_id is None:
        if request:
            site = get_current_site_from_request(request)
        else:
            site = ensure_site_exists(getattr(settings, 'SITE_ID', 8))
        
        if site:
            site_id = site.id
        else:
            site_id = 8
    
    site = ensure_site_exists(site_id)
    if site:
        protocol = 'https'
        return f'{protocol}://{site.domain}'
    
    # Ultimate fallback
    return 'https://frizerskisalonhasko.com'