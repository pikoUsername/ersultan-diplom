from django.contrib import admin
from django import forms
from guardian.admin import GuardedModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Dealer, Car, CarLocation, TripTracking, Rental, Transaction, CarReview, Fine
)


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = '__all__'


@admin.register(Rental)
class RentalAdmin(GuardedModelAdmin):
    form = RentalForm
    list_display = ['user', 'car', 'start_time', 'end_time', 'is_paid']  # Убрали 'status'
    list_filter = ['is_paid']
    search_fields = ['user__username', 'car__brand']
    autocomplete_fields = ['user', 'car']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionForm
    list_display = ['user', 'amount', 'transaction_type', 'timestamp']  # Убрали 'status'
    list_filter = ['transaction_type']
    search_fields = ['user__username']
    readonly_fields = ['timestamp']  # 'created_at' нет в модели, но есть 'timestamp'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = CarReview
        fields = '__all__'


@admin.register(CarReview)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewForm
    list_display = ['user', 'car', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'car__brand']
    readonly_fields = ['created_at']


class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = '__all__'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    form = FineForm
    list_display = ['user', 'rental', 'amount', 'reason', 'issued_at']  # Убрали 'car'
    search_fields = ['user__username', 'rental__car__brand']
    readonly_fields = ['issued_at']  # Убрали 'created_at'


class DealerForm(forms.ModelForm):
    class Meta:
        model = Dealer
        widgets = {
            'name': forms.TextInput(attrs={'class': 'vTextField'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
        fields = '__all__'


@admin.register(Dealer)
class DealerAdmin(GuardedModelAdmin):
    form = DealerForm
    search_fields = ['name', 'address']
    list_display = ['name', 'address', 'latitude', 'longitude']
    list_filter = ['name']


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'vTextField'}),
            'model': forms.TextInput(attrs={'class': 'vTextField'}),
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2030}),
            'price_per_hour': forms.NumberInput(attrs={'step': 0.01}),
        }


@admin.register(Car)
class CarAdmin(GuardedModelAdmin):
    form = CarForm
    search_fields = ['brand', 'model']
    list_display = ['brand', 'model', 'year', 'price_per_hour', 'is_available', 'dealer']
    list_filter = ['year', 'dealer', 'is_available']
    list_editable = ['is_available', 'price_per_hour']
    autocomplete_fields = ['dealer']


class CarLocationForm(forms.ModelForm):
    class Meta:
        model = CarLocation
        fields = '__all__'


@admin.register(CarLocation)
class CarLocationAdmin(admin.ModelAdmin):
    form = CarLocationForm
    list_display = ['car', 'latitude', 'longitude', 'updated_at']
    search_fields = ['car__brand', 'car__model']
    readonly_fields = ['updated_at']


### 4. Форма для истории трекинга
class TripTrackingForm(forms.ModelForm):
    class Meta:
        model = TripTracking
        fields = '__all__'


@admin.register(TripTracking)
class TripTrackingAdmin(admin.ModelAdmin):
    form = TripTrackingForm
    list_display = ['rental', 'timestamp', 'latitude', 'longitude']
    search_fields = ['rental__id']
    readonly_fields = ['timestamp']
