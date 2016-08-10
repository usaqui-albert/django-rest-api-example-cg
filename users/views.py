# -*- encoding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from rest_framework import parsers, renderers, status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .models import User
from .serializers import CreateUserSerializer, UserSerializer, UpdateUserSerializer
from .tasks import post_create_user

class UserView(generics.ListCreateAPIView):
    """Service to create a new user and get all users(temporary)

    :accepted methods:
        POST
        GET
    """
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        if isinstance(obj, User):
            transaction.on_commit(lambda: post_create_user.delay(obj.id))
            token = Token.objects.create(user=obj)
            data = {'token': str(token),
                    'user': UserSerializer(obj).data}
            return Response(data, status=status.HTTP_201_CREATED)
        if not obj:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            return Response({'stripe_error': [str(obj)]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = self.get_queryset()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserSerializer(page, many=True, context={'without_payment': True})
                return self.get_paginated_response(serializer.data)

            serializer = UserSerializer(queryset, many=True, context={'without_payment': True})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response('Permission denied, you are not an administrator',
                        status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = User.objects.all().select_related('country', 'province')
        return queryset


class UserDetail(generics.RetrieveUpdateAPIView):
    """Service to get the detail of a user or update if the user requesting is the owner
    or is an admin

    :accepted methods:
        PATH
        PUT
        GET
    """
    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.AllowAny,)

    def update(self, request, **kwargs):
        """Method to get the data of a user if the user requesting is the owner or is an admin

        :param request: data to update, user instance and request method PUT or PATCH
        :param kwargs: pk of the user and the partial boolean value
        :return: Http 200 with the updated data if it was successfully updated
        :except: Http 404 if the user does not exists, Http 403 if the user requesting is
        not the owner or is not an admin
        """
        if self.is_admin_or_own_user():
            instance = self.get_object()
            if instance.exists():
                if not request.user.is_staff and 'is_active' in request.data:
                    del request.data['is_active']
                partial = kwargs.pop('partial', True)
                serializer = self.get_serializer(instance.get(),
                                                 data=request.data,
                                                 partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response("You are not the owner or an administrator",
                        status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, **kwargs):
        """Method to get the data of a user if the user requesting is the owner or is an admin

        :param request: user instance and request method GET
        :param kwargs: pk of the user
        :return: Http 200 if the getting data was success
        :except: Http 404 if the user does not exists, Http 403 if the user requesting is
        not the owner or is not an admin
        """
        if self.is_admin_or_own_user():
            instance = self.get_object()
            if instance.exists():
                serializer = UserSerializer(instance.get(), context={'without_payment': True})
                return Response(serializer.data)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response("You are not the owner or an administrator",
                        status=status.HTTP_403_FORBIDDEN)

    def get_object(self):
        """Method to filter user by pk and prefetch the country instance related to
        the user

        :return: queryset with the user in it
        """
        obj = User.objects.filter(pk=self.kwargs['pk']).select_related('country', 'province')
        return obj

    def is_admin_or_own_user(self):
        """Method to verify if the user that is requesting is the owner or is an admin

        :return: True if is the own user or an admin, otherwise False
        """
        user, pk = (self.request.user, self.kwargs['pk'])
        return True if user.is_staff or user.pk == int(pk) else False


class LoginView(generics.GenericAPIView):
    """Service to get a token authentication

    :accepted methods:
        POST username(email) and password.
    """
    throttle_classes = ()
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        """Method for the authentication of a user

        :param request: introduced data, 'email' and 'password'
        :return: authentication token
        :except: validation error message if the username and password don't match
        """
        if 'admin_mode' in request.data:
            admin_mode = False if str(request.data['admin_mode']) == 'False' else True
        else:
            admin_mode = False

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if admin_mode and not user.is_staff:
            return Response('Permission denied, you are not an administrator',
                            status=status.HTTP_403_FORBIDDEN)
        else:
            user.last_login = timezone.now()
            user.save()
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            data = {'token': str(token),
                    'user': UserSerializer(user).data}
            return Response(data, status=status.HTTP_200_OK)
