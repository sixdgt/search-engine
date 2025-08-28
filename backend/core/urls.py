from django.urls import path
from .views import SearchArticleView, StartScrapeView, ScrapeStatusView

urlpatterns = [
    path('search/', SearchArticleView.as_view(), name='search'),
    path('scrape/', StartScrapeView.as_view(), name='start-scrape'),
    path('scrape/status/<str:task_id>/', ScrapeStatusView.as_view(), name='scrape-status'),
]
