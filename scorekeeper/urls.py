from django.urls import path
from .views import login_view, scoresheet_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('scoresheet/', scoresheet_view, name='scoresheet'),
    # ... You can add more routes as needed
]