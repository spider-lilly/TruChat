from django.urls import path

from .views import HistoryCounterView, HistoryListView

urlpatterns = [
    path("", HistoryListView.as_view(), name="history-list"),
    path("counter/", HistoryCounterView.as_view(), name="history-counter"),
]
