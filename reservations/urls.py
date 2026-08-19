from django.urls import path
from .views import (
    ReservationListView,
    ReservationCreateView,
    ReservationRetrieveDestroyView
    )

urlpatterns = [
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/create/', ReservationCreateView.as_view(), name='reservation-create'),
    path('reservations/<int:pk>/', ReservationRetrieveDestroyView.as_view(), name='reservation-detail'),
]