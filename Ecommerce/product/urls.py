from django.urls import path
from . import views 

urlpatterns = [
    path('products/',views.listing_Products),
    path('products/<int:pk>/',views.get_product_by_id),
    path('products/add/',views.adding_new_product),
    path('products/update/<int:pk>/',views.update_product),
    path('products/delete/<int:pk>/',views.delete_product),

    path('<int:pk>/reviews/', views.create_review),
    path('<int:pk>/reviews/delete/', views.delete_review),
]
