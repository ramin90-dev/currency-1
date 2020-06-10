from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from settings import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    path('rate/', include('rate.urls_rate')),

    path('account/', include('account.urls')),

]

handler404 = views.handler404
handler500 = views.handler500
