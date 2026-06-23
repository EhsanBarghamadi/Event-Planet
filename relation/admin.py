from django.contrib import admin
from .models import Registration, Feedback, Result

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['participant', 'event']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['participant', 'event', 'rating']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['event', 'participant', 'achievement']