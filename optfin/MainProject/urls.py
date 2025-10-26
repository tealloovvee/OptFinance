
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls')),
    path('', TemplateView.as_view(template_name='dist/index.html')),
]

if settings.DEBUG:
    urlpatterns += static('/assets/', document_root=settings.STATIC_ROOT + '/assets')
