
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls')),
    path('', TemplateView.as_view(template_name='dist/index.html')),
]
