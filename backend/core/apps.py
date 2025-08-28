from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Avoid circular imports by importing inside ready()
        from django.core.cache import cache
        from django.db.models.signals import post_save, post_delete
        from .models import Publication
        from .utils import build_tfidf_and_index

        # Signal to rebuild TF-IDF cache on Publication changes
        def update_tfidf_cache(sender, instance, **kwargs):
            logger.info("Updating TF-IDF cache due to Publication change")
            build_tfidf_and_index()

        post_save.connect(update_tfidf_cache, sender=Publication)
        post_delete.connect(update_tfidf_cache, sender=Publication)

        # Initialize cache if empty (non-blocking)
        if not cache.get('tfidf_data'):
            try:
                logger.info("Initializing TF-IDF cache at startup")
                build_tfidf_and_index()
                logger.info("TF-IDF cache initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize TF-IDF cache at startup: {e}")
