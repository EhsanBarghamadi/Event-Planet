from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SluggedModel

class Event(SluggedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'پیش‌نویس'
        PUBLISHED = 'PUBLISHED', 'منتشر شده'
        CLOSED = 'CLOSED', 'بسته شده'
        FINISHED = 'FINISHED', 'پایان یافته'

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

    def __str__(self):
        return self.title

    def get_slug_source_field(self):
        return 'title'
    
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

    class Meta:
        verbose_name = 'مرحله رویداد'
        verbose_name_plural = 'مراحل رویداد'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.event.title} - {self.title}"