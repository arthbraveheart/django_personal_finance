from django.contrib import admin
from .models import Family

# Register your models here.
@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("heritage", "first_name", "last_name")
    search_fields = ("heritage", "first_name", "last_name")
    list_filter = ("heritage",)