from django.contrib import admin
#Poner  nota de documentacion
from .models import PoI

@admin.register(PoI)
class PoIAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'external_id', 'category', 'avg_rating')
    search_fields = ('id', 'external_id')
    list_filter = ('category',)
    ordering = ('id',)