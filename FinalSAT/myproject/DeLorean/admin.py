from django.contrib import admin

# Register your models here.

from models import Event
admin.site.register(Event)

from models import Intermediary
admin.site.register(Intermediary)

from models import User
admin.site.register(User)

from models import Update
admin.site.register(Update)
