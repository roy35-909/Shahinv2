
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from . import settings
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_schema', get_schema_view(title="API Schema",description="Guide for the Rest API"),name='api_schema'),
    path('', TemplateView.as_view(
        template_name = 'docs.html',
        extra_context = {'schema_url':'api_schema'}
    ),name = 'swagger-ui'),
    path('auth/', include('authentication.urls')),
    path('quote/', include('quote.urls')),
    path('users/', include('users.urls')),
    path('friends/', include('friends.urls')),
    path('payment/', include('payment.urls')),
    path('dashboard/', include('dashboard.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
