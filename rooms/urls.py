from django.urls import path
from .views import RoomListView, RoomDetailView, RoomCreateView, RoomRetrieveUpdateDestroyView

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('rooms/create/', RoomCreateView.as_view(), name='room-create'),
    path('rooms/<int:pk>/update/', RoomRetrieveUpdateDestroyView.as_view(), name='room-update'),
    path('rooms/<int:pk>/destroy/', RoomRetrieveUpdateDestroyView.as_view(), name='room-destroy'),
]