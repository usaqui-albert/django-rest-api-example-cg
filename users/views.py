# -*- encoding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from rest_framework import parsers, renderers, status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .models import User
from .serializers import CreateUserSerializer, UserSerializer
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
        queryset = User.objects.all()
        return queryset


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
