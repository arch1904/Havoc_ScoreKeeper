from django.contrib import admin
from .models import Division, Team, Player, Match

# Register your models here.
admin.site.register(Division)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
