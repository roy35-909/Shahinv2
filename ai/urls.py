from django.urls import include, path

from .views import (
AIQuoteAPIView
)
urlpatterns = [

    path('generate_quote/', AIQuoteAPIView.as_view(), name="AI Quote API View"),

    
]