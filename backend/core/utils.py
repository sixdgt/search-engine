# core/utils.py
import pickle
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from django.core.cache import cache
from .models import Publication

logger = logging.getLogger(__name__)

TFIDF_CACHE_KEY = 'tfidf_data'
DOCUMENTS_CACHE_KEY = 'documents_data'

def ensure_nltk_resources():
    """Download NLTK resources if not already present."""
    try:
        nltk.data.find('corpora/stopwords')
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        logger.info("Downloading NLTK stopwords and punkt")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)

def build_tfidf_and_index():
    ensure_nltk_resources()

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))

    def pre_process(text):
        tokens = word_tokenize(text.lower())
        return [stemmer.stem(token) for token in tokens if token.isalnum() and token not in stop_words]

    publications = Publication.objects.all()
    documents = {pub.id: pub.abstract or pub.title for pub in publications}

    corpus = [' '.join(pre_process(text)) for text in documents.values()]
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf_matrix = None
    vectorizer = TfidfVectorizer()
    
    if corpus:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        try:
            cache.set(TFIDF_CACHE_KEY, pickle.dumps({
                'vectorizer': vectorizer,
                'tfidf_matrix': tfidf_matrix,
                'doc_ids': list(documents.keys())
            }), timeout=24*60*60)
            cache.set(DOCUMENTS_CACHE_KEY, documents, timeout=24*60*60)
        except Exception as e:
            logger.error(f"Failed to cache TF-IDF data: {e}")
            raise

    return documents, vectorizer, tfidf_matrix
