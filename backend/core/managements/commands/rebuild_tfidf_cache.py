from django.core.management.base import BaseCommand
from core.utils import build_tfidf_and_index, ensure_nltk_resources
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Rebuilds TF-IDF cache for search functionality'

    def handle(self, *args, **kwargs):
        logger.info("Starting TF-IDF cache rebuild")
        ensure_nltk_resources()
        documents, vectorizer, tfidf_matrix = build_tfidf_and_index()
        doc_count = len(documents)
        self.stdout.write(self.style.SUCCESS(f"TF-IDF cache rebuilt successfully: {doc_count} documents processed"))
