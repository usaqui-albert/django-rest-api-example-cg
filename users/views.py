# -*- encoding: utf-8 -*-
import logging

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from rest_framework import parsers, status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .models import User
from .serializers import CreateUserSerializer, UserSerializer, UpdateUserSerializer
from .tasks import post_create_user
from benevity_library import benevity
from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from events.helpers import get_message_error


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
            context = {'without_payment': True, 'without_plan': True}
            queryset = self.get_queryset()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserSerializer(page, many=True, context=context)
                return self.get_paginated_response(serializer.data)

            serializer = UserSerializer(queryset, many=True, context=context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response('Permission denied, you are not an administrator',
                        status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = User.objects.all().select_related('country', 'province')
        return queryset


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Service to get the detail of a user or update if the user requesting is the owner
    or is an admin

    :accepted methods:
        PATH
        PUT
        GET
        DELETE
    """
    def __init__(self, *args, **kwargs):
        super(UserDetail, self).__init__(*args, **kwargs)
        benevity.api_key = BENEVITY_API_KEY
        benevity.company_id = BENEVITY_COMPANY_ID
        self.logger = logging.getLogger(__name__)

    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, **kwargs):
        """Method to get the data of a user if the user requesting is the owner or is an admin

        :param request: data to update, user requesting instance and request method PUT or PATCH
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
                obj = self.perform_update(serializer)
                return Response(UserSerializer(obj).data)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response("You are not the owner or an administrator",
                        status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, **kwargs):
        """Method to get the data of a user if the user requesting is the owner or is an admin

        :param request: user requesting instance and request method GET
        :param kwargs: pk of the user
        :return: Http 200 if the getting data was success
        :except: Http 404 if the user does not exists, Http 403 if the user requesting is
        not the owner or is not an admin
        """
        if self.is_admin_or_own_user():
            instance = self.get_object()
            if instance.exists():
                context = dict()
                if request.user.is_staff:
                    context['without_payment'] = True
                    context['without_plan'] = True
                serializer = UserSerializer(instance.get(), context=context)
                return Response(serializer.data)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response("You are not the owner or an administrator",
                        status=status.HTTP_403_FORBIDDEN)

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            raw_password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(raw_password)
        obj = serializer.save()
        dic_to_update = {
            'user': str(obj.benevity_id),
            'firstname': str(obj.company) if obj.is_corporate_account() else str(obj.first_name),
            'lastname': '-' if obj.is_corporate_account() else str(obj.last_name),
            'address-postcode': str(obj.zip_code),
        }
        updated_user = benevity.update_user(**dic_to_update)
        if updated_user['attrib']['status'] == 'FAILED':
            message = 'There was a benevity error updating the user'
            self.logger.error(message + ', ' + get_message_error(updated_user))
        return obj

    def destroy(self, request, **kwargs):
        """Method to delete a user only if the user requesting is an admin

        :param request: user requesting instance and request method DELETE
        :param kwargs: pk of the user
        :return: Http 200 if the user was successfully deleted
        :except: Http 404 if the user does not exists, Http 403 if the user requesting is
        not an admin
        """
        if request.user.is_staff:
            instance = self.get_object()
            if instance.exists():
                self.perform_destroy(instance.get())
                return Response("The user was successfully deleted",
                                status=status.HTTP_200_OK)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response('Permission denied, you are not an administrator',
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

            if admin_mode:
                return_serializer = UserSerializer(user,
                                                   context={
                                                       'without_payment': True,
                                                       'without_plan': True
                                                   })
            else:
                return_serializer = UserSerializer(user)

            data = {'token': str(token),
                    'user': return_serializer.data}
            return Response(data, status=status.HTTP_200_OK)
