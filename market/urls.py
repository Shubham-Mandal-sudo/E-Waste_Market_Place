from django.urls import path
from . import views

urlpatterns = [
    path('sell/', views.create_listing, name='create_listing'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
]