from django.urls import path
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    path('admin/', views.index, name='index'),
    path('profile/', views.profile),
    path('login/', login, {'template_name': 'accounts/login.html'}),
    path('register/', views.register, name= 'register'),
    path('home/', views.home, name='home'),
    path('logout/', logout, {'template_name': 'accounts/logout.html'}),
    path('list/', views.list),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.del_profile, name='del_profile')
]


