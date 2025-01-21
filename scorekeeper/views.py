from django.shortcuts import render

# Create your views here.
import csv
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Division, Player, Team, Match, GameMatchup, SKILL_GAMES_NEEDED
from .forms import CustomLoginForm, GameMatchupForm

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
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            division_id = form.cleaned_data['division_id']
            player_id = form.cleaned_data['player_id']

            # Attempt to find the Player in that Division
            try:
                # We'll do a quick filter
                division = Division.objects.get(pk=division_id)
                player = Player.objects.get(player_number=player_id, team__division=division)
            except (Division.DoesNotExist, Player.DoesNotExist):
                return render(request, 'login.html', {
                    'form': form,
                    'error': "Invalid division/player combination."
                })

            # Example: find a match for the player's team that is "today"
            # In a real scenario, you might show a list of all scheduled matches or 
            # the nearest upcoming match. For demonstration, assume "today's match."
            today = datetime.date.today()
            # e.g. get home or away match for player's team on today's date
            match = Match.objects.filter(
                division=division,
                date=today
            ).filter(
                home_team=player.team
            ).first() or Match.objects.filter(
                division=division,
                date=today
            ).filter(
                away_team=player.team
            ).first()

            if not match:
                # If no match found, return an error or handle gracefully
                return render(request, 'scorekeeper/templates/login.html', {
                    'form': form,
                    'error': "No scheduled match found for your team today!"
                })

            # Store something in session for demonstration
            request.session['player_id'] = player.id
            request.session['division_id'] = division.id
            request.session['match_id'] = match.id

            # Redirect to the scoresheet page
            return redirect(reverse('scoresheet'))
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

def scoresheet_view(request):
    match_id = request.session.get('match_id')
    player_id = request.session.get('player_id')

    if not match_id or not player_id:
        # If there's no session data, go back to login
        return redirect('login')  # name of your login url

    match = get_object_or_404(Match, pk=match_id)
    current_player = get_object_or_404(Player, pk=player_id)

    # Potential players for the dropdown: all players from both teams
    possible_players = Player.objects.filter(team__in=[match.home_team, match.away_team])

    # We’ll gather matchup forms
    matchup_forms = []
    if request.method == 'POST':
        # If user submitted the forms, we can process them (not fully implemented).
        # For each matchup, gather the posted form data and handle saving.
        for i, matchup in enumerate(match.matchups.all()):
            form_prefix = f'matchup_{matchup.id}'
            form = GameMatchupForm(
                request.POST,
                possible_players=possible_players,
                skill_data=None,  # We'll set dynamically below
                prefix=form_prefix
            )
            if form.is_valid():
                lag_winner_id = form.cleaned_data['lag_winner']
                lag_loser_id = form.cleaned_data['lag_loser']
                if lag_winner_id and lag_loser_id:
                    matchup.lag_winner_id = lag_winner_id
                    matchup.lag_loser_id = lag_loser_id
                    matchup.save()

            matchup_forms.append(form)
        # After processing all forms, maybe redirect or show success message
        return HttpResponse("Scores saved!")  # or redirect to scoreboard
    else:
        # GET request, build blank forms
        for matchup in match.matchups.all():
            # If there's already a lag winner/loser on the matchup, we can pass them as initial data
            initial_data = {}
            if matchup.lag_winner:
                initial_data['lag_winner'] = matchup.lag_winner.id
            if matchup.lag_loser:
                initial_data['lag_loser'] = matchup.lag_loser.id

            # For demonstration, let’s figure out the skill data (if both players are known)
            # But since it’s a blank scoresheet, we might not have them yet, so pass None
            skill_data = None
            # Example: if we have two known players:
            # skill_data = (SKILL_GAMES_NEEDED[matchup.lag_winner.skill_rank],
            #               SKILL_GAMES_NEEDED[matchup.lag_loser.skill_rank])

            form = GameMatchupForm(
                possible_players=possible_players,
                skill_data=skill_data,
                initial=initial_data,
                prefix=f'matchup_{matchup.id}'
            )
            matchup_forms.append(form)

    return render(request, 'scorekeeper/templates/scoresheet.html', {
        'match': match,
        'matchup_forms': matchup_forms,
    })
