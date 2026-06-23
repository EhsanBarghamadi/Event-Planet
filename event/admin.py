from django.contrib import admin
from .models import Event, EventStage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['organizer', 'title', 'status', 'start_date', 'end_date']
    search_fields = ['title',]
    search_help_text = 'بر اساس عنوان رویداد جست و جو کنید'
    list_filter = ['status',]

@admin.register(EventStage)
class EventStageAdmin(admin.ModelAdmin):
    list_display = ['event', 'title', 'start_time', 'end_time']
    search_fields = ['event']
    search_help_text = 'جست و جو بر اساس رویداد'