from rest_framework import serializers
from django.utils import timezone
from attribute.serializers import EventAttributeValueSerializer
from .models import Event, EventStage

class EventSerializer(serializers.ModelSerializer):
    attribute_values = EventAttributeValueSerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'title', 'description', 
                  'status', 'capacity', 'start_date',
                    'end_date', 'attribute_values']
        read_only_fields = ['attribute_values', 'organizer']

    def validate_start_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError('تاریخ شروع رویداد نمی‌تواند در گذشته باشد.')
        return value
