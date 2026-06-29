from rest_framework import serializers
from event.models import Event
from event.serializers import EventSerializer
from .models import Registration, Feedback, Result

class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset = Event.objects.all(),
        write_only = True
    )
    class Meta:
        model = Registration
        fields = ['participant', 'event', 'event_id']
        read_only_fields = ['participant']

    def validate(self, attrs):
        event = attrs.get('event')
        required = self.context.get('request')

        if event.status != 'PUBLISHED':
            raise serializers.ValidationError({
                'event':'ثبت نام فقط روی رویداد های منتشر شده انجام می شود'
            })
        num_participant = Registration.objects.filter(event=event).count()
        if num_participant >= event.capacity:
            raise serializers.ValidationError({
                'event': 'ظرفیت این دوره تکمیل شده است'
            })
        check_registration = Registration.objects.filter(event=event, participant=required.user)
        if check_registration.exists():
            raise serializers.ValidationError({
                'participant':'شما قبلا ثبت نام کرده اید'
            })
        return attrs