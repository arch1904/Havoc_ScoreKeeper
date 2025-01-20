from django.db import models

class Player(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('AAA', 'AAA'),
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    
    name = models.CharField(max_length=100)
    skill_level = models.CharField(max_length=3, choices=SKILL_LEVEL_CHOICES)

    def must_win_games(self):
        skill_games = {'AAA': 6, 'AA': 5, 'A': 4, 'B': 3, 'C': 2}
        return skill_games.get(self.skill_level, 0)

    def __str__(self):
        return f"{self.name} ({self.skill_level})"


class Match(models.Model):
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_matches')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_matches')
    
    eight_ball_player1_score = models.IntegerField(default=0)
    eight_ball_player2_score = models.IntegerField(default=0)
    nine_ball_player1_score = models.IntegerField(default=0)
    nine_ball_player2_score = models.IntegerField(default=0)
    ten_ball_player1_score = models.IntegerField(default=0)
    ten_ball_player2_score = models.IntegerField(default=0)
    
    def max_games(self):
        return self.player1.must_win_games() + self.player2.must_win_games() - 1