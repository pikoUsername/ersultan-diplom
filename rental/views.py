from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, ListView

from .admin import RentalForm
from .models import Car, CarReview


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.filter(is_available=True)[:5]
        context["total_cars"] = Car.objects.count()
        context["total_brands"] = Car.objects.values("brand").distinct().count()
        context["total_reviews"] = CarReview.objects.count()
        return context


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

