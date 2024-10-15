from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('coins/', views.coin_index, name='coin-index'),
    path('coins/<str:symbol>/', views.coin_detail, name='coin-detail'),
    path('watchlist/', views.watchlist_view, name='coin-watchlist'),
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add-to-watchlist'),
    path('watchlist/remove/<str:symbol>/', views.remove_from_watchlist, name='remove-from-watchlist'),
    path('live-search/', views.live_search, name='live_search'),
]
