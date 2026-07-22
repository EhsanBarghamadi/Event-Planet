import uuid
from django.db import models, transaction, IntegrityError
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ به‌روزرسانی'
    )

    class Meta:
        abstract = True

class SluggedModel(TimeStampedModel):
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name='اسلاگ'
    )

    class Meta:
        abstract = True

    def get_slug_source_field(self):
        raise NotImplementedError("Subclasses must implement get_slug_source_field()")
    
    def save(self, *args, **kwargs):
            if not self.slug:
                source_field_name = self.get_slug_source_field()
                source_value = getattr(self, source_field_name, '')
                if source_value:
                    base_slug = slugify(source_value, allow_unicode=True)
                    if not base_slug:
                        base_slug = f"item-{uuid.uuid4().hex[:8]}"
                    base_slug = base_slug[:240]
                    slug = base_slug
                    counter = 1
                    model = self.__class__
                    while model.objects.filter(slug=slug).exists():
                        slug = f'{base_slug}-{counter}'
                        counter += 1
                    self.slug = slug
                    max_attempts = 5
                    for attempt in range(max_attempts):
                        try:
                            with transaction.atomic():
                                super().save(*args, **kwargs)
                            return
                        except IntegrityError:
                            if attempt == max_attempts - 1:
                                raise
                            self.slug = f'{base_slug}-{uuid.uuid4().hex[:6]}'
                    return
            super().save(*args, **kwargs)