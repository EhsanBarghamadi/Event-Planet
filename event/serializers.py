from rest_framework import serializers
from django.utils import timezone
from attribute.serializers import EventAttributeValueSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
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
        if value.date() < today:
            raise serializers.ValidationError('تاریخ شروع رویداد نمی‌تواند در گذشته باشد')
        return value
    
    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError('ظرفیت رویداد باید بزرگتر از صفر باشد.')
        return value
    
    def validate(self, attrs):
        if self.instance:
            start_date = attrs.get('start_date', self.instance.start_date)
            end_date = attrs.get('end_date', self.instance.end_date)
        else:
            start_date = attrs.get('start_date')
            end_date = attrs.get('end_date')
        new_status = attrs.get('status')

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    'end_date': 'تاریخ پایان رویداد نمیتواند قبل یا همزمان با تاریخ شروع آن باشد'
                })
            
        if not self.instance:
            if new_status is None:
                attrs['status'] = Event.Status.DRAFT
            elif new_status != Event.Status.DRAFT:
                raise serializers.ValidationError({
                    'status': 'وضعیت رویداد در زمان اجرا فقط میتواند "پیش نویس" باشد'
                })

        if self.instance:
            original_status = self.instance.status
            
            if new_status and original_status != new_status:
                if not Event.is_transition_allowed(original_status, new_status):
                    allowed_list = Event.get_allowed_transitions(original_status)
                    allowed_statuses = [status.value for status in allowed_list] if allowed_list else ['هیچکدام']
                    raise serializers.ValidationError({
                        'status': (
                            f'تغییر وضعیت از {original_status} به {new_status} مجاز نیست'
                            f'وضعیت مجاز {", ".join(allowed_statuses)}'
                        )
                    })
                
        return attrs
    
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
            
            if instance:

        return attrs