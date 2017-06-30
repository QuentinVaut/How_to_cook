from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.RecetteView.as_view(), name='home'),
    url(r'^login/',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^register/$', views.add_userView, name='register'),
    url(r'^user/recettes/$', views.recettes_userView, name='user_recettes'),
    url(r'^ajout_recette/$', views.add_recetteView, name='recette_add'),
    url(r'^error/$', views.error, name='error'),
    url(r'^(?P<recette_slug>[-\w]+)/$', views.detail_recetteView, name='recette_detail'),
    url(r'^(?P<recette_slug>[-\w]+)/edit/$', views.edit_recetteView, name='recette_edit'),
    url(r'^(?P<recette_slug>[-\w]+)/remove/$', views.remove_recetteView, name='recette_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


