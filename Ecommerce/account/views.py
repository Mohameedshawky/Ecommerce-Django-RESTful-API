from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .serializer import SingUpSerializer,UserSerializer


@api_view(['POST'])
def register(request):
    passedData = request.data

    serializedUser = SingUpSerializer(data = passedData)
    if serializedUser.is_valid() :
        if not User.objects.filter(username = passedData['email']).exists():
            serializedUser.save()
            return Response({'details':'Your account registered susccessfully!'}
                            ,status=status.HTTP_201_CREATED )
        else:
            return Response({'error':'This email already exists!' },
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializedUser.errors)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user, many=False)
    return Response({'user':user.data}
                    ,status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data

    # Validate email
    email_validator = EmailValidator()
    try:
        email_validator(data['email'])
    except ValidationError:
        return Response({'error': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=data['email']).exclude(id=user.id).exists():
        return Response({'error': 'This email is already in use'}, status=status.HTTP_400_BAD_REQUEST)

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.username = data.get('email', user.username)
    user.email = data.get('email', user.email)

    if data.get('password', '') != "":
        try:
            validate_password(data['password'], user)
            user.password = make_password(data['password'])
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    user.save()
    serializer = UserSerializer(user, many=False)

    return Response({'Updated Info.': serializer.data}, status=status.HTTP_200_OK)

def _get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)

@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User,email=data['email'])
    token = get_random_string(40)
    expire_date = timezone.now() + timedelta(minutes=30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    
    host = _get_current_host(request)

    link = f"http://{host}/api/reset_password/{token}"
    body = f"Your password reset link is : {link}"
    send_mail(
        "Paswword reset from Ecommerce",
        body,
        "Ecommerce@gmail.com",
        [data['email']]
    )
    return Response({'details': f"Password reset sent to {data['email']}"})

 


@api_view(['POST'])
def reset_password(request,token):
    data = request.data
    user = get_object_or_404(User,profile__reset_password_token = token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None 
    user.profile.save() 
    user.save()
    return Response({'details': 'Password reset done '})