from django.urls import path
from .views import dashboard_view  # We will map your real view function next

app_name = 'shopping'

urlpatterns = [
    # Maps the app root path to your functional, role-based dashboard view logic
    path('', dashboard_view, name='dashboard'),
]
