# -*- encoding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import parsers, renderers, status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .models import *
from .serializers import *
from .tasks import post_create_user

class UserView(generics.ListCreateAPIView):
    """Service to create a new user

    :accepted methods:
        POST
        GET
    """
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """Re-write of perform_create method to send the email after the user is created"""
        with transaction.atomic():
            obj = serializer.save()
            transaction.on_commit(lambda: post_create_user.delay(obj.id))
        return self.serializer_class(obj)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset
