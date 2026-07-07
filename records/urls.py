from django.urls import path
from .views import Records_View

urlpatterns = [
    path('', Records_View.as_view(), name='records'),
]
