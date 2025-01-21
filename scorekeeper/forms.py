from django import forms

class CustomLoginForm(forms.Form):
    division_id = forms.IntegerField(label="Division ID")
    player_id = forms.CharField(label="Player Number")

    # If you want, add cleaning/validation here

class GameMatchupForm(forms.Form):
    """
    Dynamically sets the list of possible players for lag_winner and lag_loser.
    Also dynamically handles the number of checkboxes or fields for each player's
    possible game wins.
    """
    def __init__(self, *args, possible_players=None, skill_data=None, **kwargs):
        """
        :param possible_players: A QuerySet or list of players from both teams
        :param skill_data: (skill_1, skill_2) for dynamic generation of fields
        """
        super().__init__(*args, **kwargs)

        # Create choices for players
        player_choices = [(p.id, f"{p.name} (#{p.player_number}, {p.skill_rank})") 
                          for p in possible_players] if possible_players else []

        self.fields['lag_winner'] = forms.ChoiceField(choices=player_choices, required=False)
        self.fields['lag_loser'] = forms.ChoiceField(choices=player_choices, required=False)

        # Suppose we want checkboxes for each "game" up to skill_needed_sum - 1
        if skill_data:
            skill_winner_needed, skill_loser_needed = skill_data
            total_games = (skill_winner_needed + skill_loser_needed) - 1
            # We'll generate two sets of checkboxes or integer fields:
            for i in range(total_games):
                # Mark checkboxes for lag_winner
                self.fields[f'lag_winner_game_{i}'] = forms.BooleanField(required=False)
                # Mark checkboxes for lag_loser
                self.fields[f'lag_loser_game_{i}'] = forms.BooleanField(required=False)