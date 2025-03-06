from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, ListView

from .admin import RentalForm
from .models import Car, CarReview, Rental, Transaction


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.filter(is_available=True)[:5]
        context["total_cars"] = Car.objects.count()
        context["total_brands"] = Car.objects.values("brand").distinct().count()
        context["total_reviews"] = CarReview.objects.count()
        return context


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        """Фильтруем машины по типу, если параметр передан"""
        car_type = self.kwargs.get('type')  # Получаем тип из URL
        if car_type:
            return Car.objects.filter(type=car_type, is_available=True)
        return Car.objects.filter(is_available=True)  # По умолчанию все доступные машины


class CarTypeListView(ListView):
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"

    def get_queryset(self):
        car_type = self.kwargs.get("type")
        return Car.objects.filter(type=car_type, is_available=True)


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"


class CarRentalView(FormView):
    template_name = "car_rental.html"
    form_class = RentalForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        car_id = self.kwargs.get("pk")
        car = Car.objects.get(id=car_id)
        rental = form.save(commit=False)
        rental.car = car
        rental.user = self.request.user
        rental.save()
        return super().form_valid(form)


class ContactUsView(TemplateView):
    template_name = "contact.html"


class AboutUsView(TemplateView):
    template_name = "about.html"


class RentalHistoryView(ListView):
    model = Rental
    template_name = 'rental_history.html'
    context_object_name = 'rentals'

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user).order_by('-end_date')


class TransactionHistoryView(ListView):
    model = Transaction
    template_name = 'payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')


class ActiveRentalsView(ListView):
    model = Rental
    template_name = 'cars/active_rentals.html'
    context_object_name = 'rentals'

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, is_active=True)

