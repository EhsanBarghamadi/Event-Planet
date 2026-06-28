from rest_framework import serializers
from django.utils import timezone
from attribute.serializers import EventAttributeValueSerializer
from rest_framework.exceptions import PermissionDenied
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
            raise serializers.ValidationError('تاریخ شروع رویداد نمی‌تواند در گذشته باشد')
        return value

class EventStageSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True
    )
    class Meta:
        model = EventStage
        fields = ['id', 'event', 'event_id', 'title', 'description', 
                  'start_time', 'end_time', 'order']
        
    def validate_start_time(self, value):
        if value and self.instance and value < self.instance.event.start_date:
            raise serializers.ValidationError(
                 'زمان شروع باید بعد از شروع رویداد باشد',
                 code='invalid_start_time'
            )
        return value
    
    def validate_end_time(self, value):
        if value and self.instance and value > self.instance.event.end_date:
            raise serializers.ValidationError(
                'زمان پایان باید قبل از پایان رویداد باشد',
                code='invalid_end_time'
            )
        return value
    
    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        event = attrs.get('event')

        instance = self.instance 

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'start_time': 'زمان شروع باید قبل از زمان پایان باشد',
                'end_time': 'زمان پایان باید بعد از زمان شروع باشد'
            })
        
        if not instance:
            request = self.context.get('request')

            if not event:
                raise serializers.ValidationError({
                    'event_id': 'رویداد الزامی است!'
                })
            
            if event.organizer != request.user:
                raise PermissionDenied('شما مالک این رویداد نیستید.')
            
            if start_time < event.start_date:
                raise serializers.ValidationError({
                    'start_time': f'زمان شروع نباید قبل از {event.start_date} باشد'
                })
            
            if end_time > event.end_date:
                raise serializers.ValidationError({
                    'end_time': f'زمان پایان نباید بعد از {event.end_date} باشد'
                })
            

            overlapping = EventStage.objects.filter(
                event=event,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping.exists():
                raise serializers.ValidationError(
                    'این مرحله با مراحل دیگر تداخل زمانی دارد'
                )
        return attrs