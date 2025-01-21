from django.db import models

class Division(models.Model):
    """
    Represents a division (e.g., 'Division 1', 'Division 2', etc.).
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Team(models.Model):
    """
    Each team belongs to a particular division.
    Maximum roster size is 10 (enforced via logic, not by DB constraint).
    """
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (Division: {self.division.name})"

    @property
    def players(self):
        """
        Returns a list of all players associated with this team.
        """
        return self.player_set.all()
    
SKILL_RANK_CHOICES = [
    ('AAA', 'AAA'),  # must win 6
    ('AA', 'AA'),    # must win 5
    ('A', 'A'),      # must win 4
    ('B', 'B'),      # must win 3
    ('C', 'C'),      # must win 2
]

# Mapping of skill rank to number of games needed
SKILL_GAMES_NEEDED = {
    'AAA': 6,
    'AA': 5,
    'A': 4,
    'B': 3,
    'C': 2
}

class Player(models.Model):
    """
    Each player has a unique player number, belongs to a team, and has a skill rank.
    """
    player_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    skill_class = models.CharField(max_length=3, choices=SKILL_RANK_CHOICES)
    power_index = models.CharField(max_length=3)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (#{self.player_number}, {self.power_index}, {self.skill_class})"

GAME_TYPE_CHOICES = [
    ('8-Ball', '8-Ball'),
    ('9-Ball', '9-Ball'),
    ('10-Ball', '10-Ball'),
]

class Match(models.Model):
    """
    Represents a weekly encounter between two teams in a specific division.
    E.g., Team A vs Team B in a given division on a certain date.
    """
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    date = models.DateField()
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} on {self.date}"


class GameMatchup(models.Model):
    """
    Represents an individual matchup (e.g. 8-ball #1, 9-ball #2, etc.) 
    for the overall Match. 
    Each match has 6 GameMatchups total: 2 for 8-Ball, 2 for 9-Ball, 2 for 10-Ball.
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='matchups')
    game_type = models.CharField(max_length=10, choices=GAME_TYPE_CHOICES)
    # We'll capture the player references later, or possibly store them once assigned:
    lag_winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name='lag_winner_matchups')
    lag_loser = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name='lag_loser_matchups')
    # Additional fields: e.g. final scores or "boxes" to reflect how many games each player won
    # For simplicity, we’ll store them in a ManyToMany or direct integer fields, etc.

    def __str__(self):
        return f"{self.game_type} matchup for {self.match}"
    
