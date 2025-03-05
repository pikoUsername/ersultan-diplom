from django.urls import path
from .views import (
    HomePageView, CarTypeListView, CarDetailView,
    CarRentalView, AboutUsView, ContactUsView
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("cars/type/<str:type>/", CarTypeListView.as_view(), name="car_type_list"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/rent/", CarRentalView.as_view(), name="car_rent"),
    path("about/", AboutUsView.as_view(), name="about"),
    path("contact/", ContactUsView.as_view(), name="contact"),
]
