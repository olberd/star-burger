from django.contrib import admin
from .models import Place


@admin.register(Place)
class LocationAdmin(admin.ModelAdmin):
    pass
