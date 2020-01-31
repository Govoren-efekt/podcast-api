from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.email_post, name='login'),
    path('login/<str:token>/', views.token_post, name='login-token'),
    path('logout/', views.logout, name='logout'),
]