from django.contrib import admin
from .models import User, Board, Cell, Board_Participation, Room

# Register your models here.
admin.site.register(User)
admin.site.register(Board)
admin.site.register(Cell)
admin.site.register(Board_Participation)
admin.site.register(Room)