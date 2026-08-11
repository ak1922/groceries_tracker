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
    path('trip/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    path('trip/<int:pk>/toggle/', views.trip_toggle_complete, name='trip_toggle'),
    path('trip/<int:pk>/delete/', views.delete_trip, name='delete_trip'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),
]
