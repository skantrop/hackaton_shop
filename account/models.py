from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    activation_code = models.CharField(max_length=8, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.email}'

    def create_activation_code(self):
        from django.utils.crypto import get_random_string
        code = get_random_string(8, '0123456789')
        self.activation_code = code
        self.save()

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    @staticmethod
    def send_activation_mail(email, activation_code):
        message = f"Thank you for registration. Activation code for your account: {activation_code}"
        send_mail("Account activation",
                  message,
                  'test@gmail.com',
                  [email, ]
                  )
