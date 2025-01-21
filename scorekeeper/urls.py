from django.urls import path
from .views import login_view, scoresheet_view, view_matchups, view_teams

urlpatterns = [
    path('login/', login_view, name='login'),
    path('teams/', view_teams, name='view_teams'),
    path('teams/<int:team_id>/matchups/', view_matchups, name='view_matchups'),
    path('scoresheet/', scoresheet_view, name='scoresheet'),
    # ... You can add more routes as needed
]