from rest_framework import serializers

from event.models import Event
from user.serializers import UserReadOnlySerializer
from event.serializers import EventSerializer
from user.models import CustomUser
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
        fields = ['id', 'participant', 'event', 'event_id']
        read_only_fields = ['participant', 'id']

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

class RegistrationReadOnlySerializer(serializers.ModelSerializer):
    participant = UserReadOnlySerializer()
    class Meta:
        model = Registration
        fields = ['participant', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True
    )
    class Meta:
        model = Feedback
        fields = ['participant', 'event', 'event_id', 'rating', 'comment']
        read_only_fields = ['participant']

    def validate(self, attrs):
        event = attrs.get('event')
        request = self.context.get('request')

        if event is None and self.instance:
            event = self.instance.event

        if event.status != 'FINISHED':
            raise serializers.ValidationError({
                'event': 'فقط برای رویدادهای پایان‌یافته می‌توانید بازخورد ثبت کنید'
            })
        
        registration = Registration.objects.filter(event=event, participant=request.user)
        if not registration.exists():
            raise serializers.ValidationError({
                'participant': 'برای ثبت نظر باید در دوره مورد نظر ثبت نام کنید'
            })
        
        feedback_qs = Feedback.objects.filter(event=event, participant=request.user)
        if self.instance:
            feedback_qs = feedback_qs.exclude(pk=self.instance.pk)

        if feedback_qs.exists():
            raise serializers.ValidationError({
                'participant': 'شما قبلا نظر خود را ثبت کرده اید'
            })
        
        return attrs

class ResultSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True
    )
    participant = UserReadOnlySerializer(read_only=True)
    participant_id = serializers.PrimaryKeyRelatedField(
        source='participant',
        queryset=CustomUser.objects.all(),
        write_only=True
    )
    class Meta:
        model = Result
        fields = ['event', 'event_id', 'participant', 'participant_id', 'achievement']
    
    def validate(self, attrs):
        event = attrs.get('event')
        participant = attrs.get('participant')
        request = self.context.get('request')

        if event is None and self.instance:
            event = self.instance.event

        if participant is None and self.instance:
            participant = self.instance.participant

        if request.user != event.organizer:
            raise serializers.ValidationError({
                'user': 'شما مالک این رویداد نیستید!'
            })
        if event.status != 'FINISHED':
            raise serializers.ValidationError({
                'event': 'فقط برای رویدادهای پایان‌یافته می‌توانید نتیجه ثبت کنید'
            })
        registration = Registration.objects.filter(participant=participant , event=event)
        if not registration.exists():
            raise serializers.ValidationError({
                'participant': 'این کاربر در این رویداد ثبت نام نکرده است.'
            })
        return attrs
        