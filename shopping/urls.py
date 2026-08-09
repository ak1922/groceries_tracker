from django.urls import path
from . import views


app_name = 'shopping'


urlpatterns = [
    path('', views.dashboard.dashboard_view, name='dashboard'),
    path('trip/<int:pk>', views.trip_detail, name='trip_detail'),
    path('history/', views.trip_history, name='trip_history'),
    path('stores/', views.store_list, name='store_list'),
    path('store/<int:pk>/edit/', views.store_edit, name='store_edit'),
    path('store/<int:pk>/delete/', views.store_delete, name='store_delete'),
]
