from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hackshop import views

urlpatterns = [
    path('', views.index),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('dashboard/', views.dashboard),
    path('shop/', views.shop),
    path('forum/', views.forum),
    path('admin-panel/', views.admin_panel),
    path('admin_clear_forum/', views.admin_clear_forum),
    path('backup/', views.backup),
    path('manage_bans/', views.manage_bans),
]

if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
