from django.urls import path
from . import views

urlpatterns = [
    path('login/<str:role>/', views.user_login, name='login'),
    path('register/<str:role>/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]