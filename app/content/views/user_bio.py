from django.shortcuts import render
from rest_framework import viewsets
from .models import UserBio
from .serializer import UserBioSerializer
# Create your views here.

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = UserBio.objects.all() #Queryset = all data som tilhører denne klassen (alle objekter i userbio)
    serializer_class = UserBioSerializer