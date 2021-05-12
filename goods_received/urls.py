from goods_received import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                path('create_gr', views.create_gr, name='create_gr'),
                path('coming_soon', views.gr_soon, name='coming_soon'),
                path('gr_dashboard', views.gr_dashboard, name='gr_dashboard'),
                path('view_my_gr', views.view_gr, name='view_my_gr'),
                path('approve_gr', views.approve_gr, name='approve_gr'),
                # vv This one MUST ALWAYS be last vv
                path('<slug:formID>', views.gr_home, name='goods_received')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
