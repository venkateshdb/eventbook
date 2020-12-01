from django.contrib import admin

from event.models import User, Event, Location, Images


admin.site.register(User)
admin.site.register(Event)
admin.site.register(Location)
admin.site.register(Images)
