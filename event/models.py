from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel, SluggedModel

class Event(SluggedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'پیش‌نویس'
        PUBLISHED = 'PUBLISHED', 'منتشر شده'
        ONGOING = 'ONGOING', 'در حال برگزاری'
        CLOSED = 'CLOSED', 'بسته شده'
        FINISHED = 'FINISHED', 'پایان یافته'
        CANCELLED = 'CANCELLED', 'لغو شده'

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='برگزارکننده'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='عنوان رویداد'
    )
    description = models.TextField(
        verbose_name='توضیحات رویداد',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='وضعیت'
    )
    capacity = models.PositiveIntegerField(
        verbose_name='ظرفیت'
    )
    start_date = models.DateTimeField(
        verbose_name='تاریخ شروع'
    )
    end_date = models.DateTimeField(
        verbose_name='تاریخ پایان'
    )

    class Meta:
        verbose_name = 'رویداد'
        verbose_name_plural = 'رویداد ها'
        ordering = ['start_date']
        
    def __str__(self):
        return self.title

    def get_slug_source_field(self):
        return 'title'
    
    def clean(self):
        super().clean()
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({
                    'end_date': 'تاریخ پایان رویداد نمی‌تواند قبل یا هم‌زمان با تاریخ شروع آن باشد.'
                })
        if self.pk:
             original_status = Event.objects.get(pk=self.pk).status
             if original_status != self.status:
                allowed_transitions = {
                    Event.Status.DRAFT: [Event.Status.PUBLISHED, Event.Status.CANCELLED],
                    Event.Status.PUBLISHED: [Event.Status.ONGOING, Event.Status.CLOSED, Event.Status.CANCELLED],
                    Event.Status.ONGOING: [Event.Status.FINISHED, Event.Status.CANCELLED],
                    Event.Status.CLOSED: [Event.Status.FINISHED, Event.Status.CANCELLED],
                    Event.Status.FINISHED: [],
                    Event.Status.CANCELLED: [],
                }
                if self.status not in allowed_transitions.get(original_status, []):
                     raise ValidationError({
                          'status': f'تغییر وضعیت غیرمجاز از {original_status} به {self.status}.'
                     })
class EventStage(TimeStampedModel):
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='رویداد مربوطه'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='عنوان مرحله'
    )
    description = models.TextField(
        verbose_name='توضیحات مرحله',
        blank=True,
        null=True
    )
    start_time = models.DateTimeField(
        verbose_name='زمان شروع مرحله'
    )
    end_time = models.DateTimeField(
        verbose_name='زمان پایان مرحله'
    )
    order = models.PositiveIntegerField(
         verbose_name='ترتیب'
    )

    class Meta:
        verbose_name = 'مرحله رویداد'
        verbose_name_plural = 'مراحل رویداد'
        ordering = ['order']

    def __str__(self):
        return f"{self.event.title} - {self.title}"
    
    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                            raise ValidationError({
                                'end_time': 'زمان پایان مرحله نمی‌تواند قبل از زمان شروع آن باشد.'
                            })
        if self.event:
            if self.start_time < self.event.start_date:
                raise ValidationError({
                    'start_time': 'زمان شروع این مرحله نمی‌تواند قبل از شروع کل رویداد باشد.'
                })
            if self.end_time > self.event.end_date:
                raise ValidationError({
                    'end_time': 'زمان پایان این مرحله نمی‌تواند بعد از پایان کل رویداد باشد.'
                })