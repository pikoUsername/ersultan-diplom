from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now

from accounts.models import UserModel


# 1. Дилерский центр (точка получения машины)
class Dealer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")

    def __str__(self):
        return self.name


class Car(models.Model):
    class CarType(models.TextChoices):
        SEDAN = 'Sedan', 'Седан'
        SUV = 'SUV', 'Внедорожник'
        HATCHBACK = 'Hatchback', 'Хэтчбек'
        CABRIOLET = 'Cabriolet', 'Кабриолет'
        COUPE = 'Coupe', 'Купе'
        MINIVAN = 'Minivan', 'Минивэн'
        PICKUP = 'Pickup', 'Пикап'

    class TransmissionTypes(models.TextChoices):
        MANUAL = 'Manual', 'Механика'
        AUTOMATIC = 'Automatic', 'Автоматическая'

    class FuelTypes(models.TextChoices):
        PB95 = "PB95", "PB95"
        PB98 = "PB98", "PB98"

    brand = models.CharField(max_length=100, verbose_name="Марка")
    model = models.CharField(max_length=100, verbose_name="Модель")
    type = models.CharField(
        max_length=20,
        choices=CarType.choices,
        default=CarType.SEDAN,
        verbose_name="Тип"
    )
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за час (тг)")
    is_available = models.BooleanField(default=True, verbose_name="Доступна")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    dealer = models.ForeignKey("Dealer", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Дилер")
    image = models.ImageField(upload_to='cars/', null=True, blank=True, verbose_name="Фото")
    transmission = models.CharField(
        max_length=20,
        choices=TransmissionTypes.choices,
        verbose_name="Трансмиссия",
        default=TransmissionTypes.MANUAL
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelTypes.choices,
        verbose_name="Тип топлива",
        default=FuelTypes.PB95,
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    class Meta:
        verbose_name = "Машина"
        verbose_name_plural = "Машины"


# 3. Отзывы пользователей на машины
class CarReview(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользватель")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автомобиль")
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)], verbose_name="Оценка")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    def __str__(self):
        return f"Отзыв {self.user.username} на {self.car} ({self.rating})"


class Rental(models.Model):
    PAYMENT_METHODS = (
        ("CARD", "Банковская карта"),
        ("PAYPAL", "PayPal"),
        ("BITCOIN", "Bitcoin"),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")

    start_time = models.DateTimeField(default=now, verbose_name="Начало аренды")
    end_time = models.DateTimeField(verbose_name="Окончание аренды")

    # Личные данные
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес")
    city = models.CharField(max_length=100, verbose_name="Город")

    # Локация аренды
    pickup_location = models.CharField(max_length=255, verbose_name="Место получения")
    pickup_date = models.DateField(verbose_name="Дата получения")
    pickup_time = models.TimeField(verbose_name="Время получения")

    # Локация возврата
    dropoff_location = models.CharField(max_length=255, verbose_name="Место возврата")
    dropoff_date = models.DateField(verbose_name="Дата возврата")
    dropoff_time = models.TimeField(verbose_name="Время возврата")

    # Оплата
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Метод оплаты"
    )
    card_number = models.CharField(max_length=16, blank=True, null=True, verbose_name="Номер карты")
    expiration_date = models.CharField(max_length=7, blank=True, null=True, verbose_name="Срок действия карты (MM/YY)")
    card_holder = models.CharField(max_length=255, blank=True, null=True, verbose_name="Владелец карты")
    cvc = models.CharField(max_length=3, blank=True, null=True, verbose_name="CVC")

    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Итоговая цена")

    def save(self, *args, **kwargs):
        """Автоматический расчет стоимости аренды"""
        if self.pickup_date and self.dropoff_date:
            days = (self.dropoff_date - self.pickup_date).days
            self.total_price = days * self.car.price_per_hour * 24  # Цена за сутки

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Аренда {self.car} пользователем {self.user.username}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("TOP_UP", "Пополнение баланса"),
        ("RENTAL", "Оплата аренды"),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Тип")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"Транзакция {self.user.username}: {self.transaction_type} {self.amount}"


# 3. Текущее местоположение машины
class CarLocation(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name="location", verbose_name="Автомобиль")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return f"Местоположение {self.car} ({self.latitude}, {self.longitude})"

    @staticmethod
    def get_last_position(car_id):
        """Получает последнюю зафиксированную позицию машины"""
        try:
            return CarLocation.objects.get(car_id=car_id)
        except CarLocation.DoesNotExist:
            return None


# 4. История перемещений (лог трекинга)
class TripTracking(models.Model):
    rental = models.ForeignKey("Rental", on_delete=models.CASCADE, related_name="tracking", verbose_name="Аренда")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время фиксации")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")

    def __str__(self):
        return f"Трек аренды {self.rental.id} ({self.latitude}, {self.longitude})"


# 6. Штрафы
class Fine(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, verbose_name="Аренда")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма штрафа")
    reason = models.TextField(verbose_name="Причина")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"Штраф {self.user.username} ({self.amount} руб.)"
