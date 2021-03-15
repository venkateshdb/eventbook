from django.contrib import admin

from event.models import User, Event, Images, order_ticket


admin.site.register(User)
admin.site.register(Event)
admin.site.register(Images)
admin.site.register(order_ticket)
