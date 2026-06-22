from django.db import models
from django.conf import settings
from core.models import SluggedModel

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