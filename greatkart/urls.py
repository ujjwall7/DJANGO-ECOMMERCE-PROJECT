from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('secure/admin/panel/', admin.site.urls),
    path('', views.home),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('orders/',include('orders.urls')),
    path('accounts/',include('accounts.urls')),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
]


if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()


