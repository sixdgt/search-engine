from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Publication, Author
from .utils import build_tfidf_and_index
from rest_framework import status
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from .tasks import run_full_scrape
from celery.result import AsyncResult

class StartScrapeView(APIView):
    def get(self, request, *args, **kwargs):
        task = run_full_scrape.delay(max_pages=50, workers=12, delay=0.35)  # start Celery task
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

class ScrapeStatusView(APIView):
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        return Response({
            'task_id': task.id,
            'status': task.status,
            'result': task.result if task.status == 'SUCCESS' else None
        })
class SearchArticleView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def pre_process(self, text):
        tokens = word_tokenize(text.lower())
        return [self.stemmer.stem(token) for token in tokens if token.isalnum() and token not in self.stop_words]

    def get(self, request):
        query = request.GET.get('query', '').strip()
        if not query:
            return Response({'results': []})

        # Lazy cache rebuild
        tfidf_data = cache.get('tfidf_data')
        documents = cache.get('documents_data')

        if not tfidf_data or not documents:
            documents, vectorizer, tfidf_matrix = build_tfidf_and_index()
        else:
            tfidf_data = pickle.loads(tfidf_data)
            vectorizer = tfidf_data['vectorizer']
            tfidf_matrix = tfidf_data['tfidf_matrix']
            doc_ids = tfidf_data['doc_ids']

        if not documents or tfidf_matrix is None:
            return Response({'results': []})

        # Query vector
        processed_query = ' '.join(self.pre_process(query))
        query_vector = vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

        # Top results
        ranked_docs = sorted(zip(doc_ids, similarities), key=lambda x: x[1], reverse=True)[:50]
        results = []
        for doc_id, score in ranked_docs:
            if score > 0:
                pub = Publication.objects.get(id=doc_id)
                authors = list(pub.authors.values('name', 'profile_url'))
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'title': pub.title,
                    'link': pub.link,
                    'published_date': pub.published_date,
                    'abstract': pub.abstract,
                    'authors': authors
                })

        return Response({'results': results})
