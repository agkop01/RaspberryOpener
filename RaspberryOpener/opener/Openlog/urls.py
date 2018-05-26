from django.urls import path
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    path('admin/', views.index, name='index'),
    path('profile/', views.profile),
    path('login/', login, {'template_name': 'accounts/login.html'}),
    path('register/', views.register, name= 'register')
    
]


