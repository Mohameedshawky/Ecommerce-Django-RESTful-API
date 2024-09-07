from django.urls import path
from . import views 

urlpatterns = [
    path('register/',views.register),
    path('userinfo/', views.current_user), 
    path('userinfo/update/', views.update_user),
    path('forgot_password/', views.forgot_password), 
    path('reset_password/<str:token>/', views.reset_password), 
]
