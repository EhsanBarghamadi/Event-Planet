from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def _create_user(self, phone, password, **extra_field):
        if not phone:
            raise ValueError('The number cannot empty!')
        user = self.model(phone=phone, **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, phone, password=None, **extra_field):
        extra_field.setdefault('is_active', True)
        extra_field.setdefault('is_staff', False)
        return self._create_user(phone, password, **extra_field)
    
    def create_superuser(self, phone, password=None, **extra_field):
        extra_field.setdefault('is_active', True)         
        extra_field.setdefault('is_staff', True)      
        extra_field.setdefault('is_superuser', True)              

        if extra_field.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_field.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_field)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ORGANIZER = 'ORGANIZER', 'Organizer'
        PARTICIPANT = 'PARTICIPANT', 'Participant'

    role = models.CharField(
        verbose_name=' نقش',
        max_length=15,
        choices=Roles.choices,
        default=Roles.PARTICIPANT
    )

    phone = models.CharField(
        verbose_name='شماره',
        max_length=20,
        unique=True,
        help_text='شماره باید منحصر به فرد باشد.'
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name='نام'
    )
    last_name = models.CharField(
        max_length=30,
        verbose_name='نام خانوادگی'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='مشخص میکند آیا کاربر فعال است یا نه'
    )

    is_staff = models.BooleanField(
        default=False,
        help_text='مشخص میکند آیا این کاربر میتواند وارد پنل ادمین شود یا نه'
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone