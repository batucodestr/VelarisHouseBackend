from django.shortcuts import render
from .models import Room
from .serializers import RoomSerializer, KeyboxCodeSerializer, RoomDetailSerializer, AdminRoomSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all().order_by('room_number')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer
    permission_classes = [AllowAny]

class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = AdminRoomSerializer
    permission_classes = [IsAdminUser]

class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = AdminRoomSerializer
    permission_classes = [IsAdminUser]