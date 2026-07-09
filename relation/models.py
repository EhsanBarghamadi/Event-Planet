from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import TimeStampedModel
from event.models import Event


class Registration(TimeStampedModel):

    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='شرکت‌کننده'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='رویداد'
    )

    class Meta:
        verbose_name = 'ثبت‌نام رویداد'
        verbose_name_plural = 'ثبت‌نام‌های رویداد'
        unique_together = ('participant', 'event')

    def __str__(self):
        return f"{self.participant.phone} -> {self.event.title}"


class Feedback(TimeStampedModel):

    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='نویسنده نظر'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='رویداد مربوطه'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز (از ۱ تا ۵)'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='متن نظر'
    )

    class Meta:
        verbose_name = 'بازخورد'
        verbose_name_plural = 'بازخوردها'
        unique_together = ('participant', 'event')

    def __str__(self):
        return f"{self.participant.phone} - Rating: {self.rating}"


class Result(TimeStampedModel):
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='رویداد'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='شرکت‌کننده'
    )
    achievement = models.CharField(
        max_length=255,
        verbose_name='دستاورد یا رتبه (مثلاً: رتبه اول، شایسته تقدیر)'
    )

    class Meta:
        verbose_name = 'نتیجه رویداد'
        verbose_name_plural = 'نتایج رویدادها'
        unique_together = ('event', 'participant')

    def __str__(self):
        return f"{self.event.title} - {self.participant.phone}: {self.achievement}"