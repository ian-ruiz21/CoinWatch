from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/signup/', views.signup, name='signup'),

]
