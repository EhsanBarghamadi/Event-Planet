from django.contrib import admin
from .models import Attribute, EventAttributeValue


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_type']
    list_filter = ['data_type']
    search_fields = ['name']
    search_help_text = 'جست و جو بر اساس نام ویژگی'

@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['event', 'attribute', 'value']
    search_fields = ['event']
    search_help_text = 'جست و جو بر اساس رویداد'