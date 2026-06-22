from django.db import models
from core.models import TimeStampedModel
from event.models import Event

class Attribute(TimeStampedModel):

    class DataType(models.TextChoices):
        TEXT = 'TEXT', 'متنی'
        INTEGER = 'INTEGER', 'عددی'
        BOOLEAN = 'BOOLEAN', 'بولین (بله/خیر)'

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام ویژگی'
    )
    data_type = models.CharField(
        max_length=15,
        choices=DataType.choices,
        verbose_name='نوع داده‌ای'
    )

    class Meta:
        verbose_name = 'ویژگی داینامیک'
        verbose_name_plural = 'ویژگی‌های داینامیک'

    def __str__(self):
        return f"{self.name} ({self.get_data_type_display()})"


class EventAttributeValue(TimeStampedModel):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name='رویداد'
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='event_values',
        verbose_name='ویژگی'
    )
    value_text = models.TextField(blank=True, null=True, verbose_name='مقدار متنی')
    value_int = models.IntegerField(blank=True, null=True, verbose_name='مقدار عددی')
    value_bool = models.BooleanField(blank=True, null=True, verbose_name='مقدار بولین')

    class Meta:
        verbose_name = 'مقدار ویژگی رویداد'
        verbose_name_plural = 'مقادیر ویژگی‌های رویداد'
        unique_together = ('event', 'attribute')

    def __str__(self):
        return f"{self.event.title} -> {self.attribute.name}"

    @property
    def value(self):
        if self.attribute.data_type == Attribute.DataType.TEXT:
            return self.value_text
        elif self.attribute.data_type == Attribute.DataType.INTEGER:
            return self.value_int
        elif self.attribute.data_type == Attribute.DataType.BOOLEAN:
            return self.value_bool
        return None