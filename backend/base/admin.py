from django.contrib import admin

from .models import (
    Restaurant,
    Employee,
    Session
)


admin.site.register(Restaurant)
admin.site.register(Employee)
admin.site.register(Session)
