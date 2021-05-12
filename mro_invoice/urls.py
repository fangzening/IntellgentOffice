from mro_invoice import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                path('invoice/<slug:po_num>', views.invoice_home, name='mro_invoice'),
                path('search_invoice', views.search_inv, name='search_invoice')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
