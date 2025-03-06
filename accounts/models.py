from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class UserModel(AbstractUser):
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    avatar = models.ImageField(null=True, blank=True, upload_to='-/users', verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Баланс")

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # ✅ Уникальное имя
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # ✅ Уникальное имя
        blank=True,
    )

    def get_avatar(self, default=None):
        if self.avatar:
            return '%s%s' % (settings.MEDIA_URL, self.avatar)
        return default

    def __str__(self):
        return self.username
