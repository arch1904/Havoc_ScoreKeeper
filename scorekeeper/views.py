from django.shortcuts import render

# Create your views here.
import csv
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Division, Player, Team, Match, GameMatchup, SKILL_GAMES_NEEDED
from .forms import CustomLoginForm, GameMatchupForm
from django.db import models

def load_schedule_from_csv(csv_path='schedule.csv'):
    # This is just a demonstration. In production, you might run a custom mgmt command
    # or do a one-time import. 
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            match_date = datetime.datetime.strptime(row['date'], '%Y-%m-%d').date()
            division_id = int(row['division_id'])
            home_team_id = int(row['home_team_id'])
            away_team_id = int(row['away_team_id'])

            division = Division.objects.get(pk=division_id)
            home_team = Team.objects.get(pk=home_team_id)
            away_team = Team.objects.get(pk=away_team_id)

            # Create or get existing Match
            match_obj, created = Match.objects.get_or_create(
                division=division,
                date=match_date,
                home_team=home_team,
                away_team=away_team
            )

            if created:
                # Create 6 default GameMatchup entries for this match
                # 2 x 8-ball, 2 x 9-ball, 2 x 10-ball
                for i in range(2):
                    GameMatchup.objects.create(match=match_obj, game_type='8-Ball')
                    GameMatchup.objects.create(match=match_obj, game_type='9-Ball')
                    GameMatchup.objects.create(match=match_obj, game_type='10-Ball')

def login_view(request):
    if request.method == 'POST':
        division_id = request.POST.get('division_id')
        player_id = request.POST.get('player_id')

        try:
            # Validate the player and division
            division = Division.objects.get(pk=division_id)
            player = Player.objects.get(player_number=player_id, team__division=division)
        except Division.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid Division ID'})
        except Player.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid Player ID'})

        # If successful, log the user in (you can implement a custom user system here)
        request.session['player_id'] = player.id
        request.session['division_id'] = division.id

        return redirect('view_teams')  # Redirect to the "view all teams" page

    return render(request, 'login.html')

def view_teams(request):
    division_id = request.session.get('division_id')
    if not division_id:
        return redirect('login')  # If not logged in, redirect to login

    division = Division.objects.get(pk=division_id)
    teams = Team.objects.filter(division=division)

    return render(request, 'view_teams.html', {'division': division, 'teams': teams})

def view_matchups(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    division_id = request.session.get('division_id')
    if team.division_id != division_id:
        return redirect('view_teams')  # Prevent access to matchups outside logged-in division

    # Fetch matchups where this team is either the home or away team
    matchups = Match.objects.filter(division_id=division_id).filter(
        models.Q(home_team=team) | models.Q(away_team=team)
    )

    # Add opponent info to matchups
    for matchup in matchups:
        if matchup.home_team == team:
            matchup.opponent = matchup.away_team
        else:
            matchup.opponent = matchup.home_team

    return render(request, 'view_matchups.html', {'team': team, 'matchups': matchups})

def scoresheet_view(request, matchup_id):
    # Fetch the selected matchup
    matchup = get_object_or_404(Match, pk=matchup_id)

    # Get the players from both teams
    home_players = Player.objects.filter(team=matchup.home_team)
    away_players = Player.objects.filter(team=matchup.away_team)

    # Handle form submission (if POST)
    if request.method == 'POST':
        # Process form data here (e.g., save scores)
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        
        # After processing, redirect to the matchups page or a success page
        return redirect('view_matchups', team_id=matchup.home_team.id)

    # Render the scoresheet for the selected matchup
    return render(request, 'scoresheet.html', {
        'matchup': matchup,
        'home_players': home_players,
        'away_players': away_players,
        'range_2': range(2),  # Add range(2) to the context
        'range_13': range(1, 14),  # Add range(1, 14) to the context
    })