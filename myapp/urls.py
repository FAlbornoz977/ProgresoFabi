from django.contrib import admin
from django.urls import path
from myapp import views 
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('empresa/', views.empresa,name='empresa'),
    path('trabajos/', views.trabajos,name='trabajos'),
    path('contacto/', views.contacto,name='contacto'),
    path('blog/', views.blog,name='blog'),
    path('blog/new/', views.create_post, name='create_post'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('blog/<int:post_id>/edit/', views.edit_post, name='edit_post'),
     path('blog/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    #user
    path('upload/', views.upload_comprobante, name='upload_comprobante'),
    path('list/', views.list_comprobantes, name='list_comprobantes'),
    path('download/<int:pk>/', views.download_comprobante, name='download_comprobante'),
    path('recordatorios/', views.lista_recordatorios, name='lista_recordatorios'),
    path('eliminar_recordatorio/<int:id>/', views.eliminar_recordatorio, name='eliminar_recordatorio'),



    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'myapp.views.page_not_found'
