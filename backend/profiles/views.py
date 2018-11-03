from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile
from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR
)
import requests
import jwt
from backend.settings_secret import *

@api_view(["POST"])
def create_profile(request):
    #Requests
    jwt_token = request.data.get('jwt_token')
    name = request.data.get('name')
    photo_data = request.data.get('photo')

    try:
        user_json = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        username = user_json['username']
        user = User.objects.get(username = username)
    except:
        return Response({'error':'Usuário não identificado'}, status=HTTP_403_FORBIDDEN)

    try:
        profile = Profile.objects.get(user=user)
        return Response({'error':'Usuário já possui perfil'}, status=HTTP_400_BAD_REQUEST)

    except Profile.DoesNotExist:
        if(name and photo_data):
            photo = cloudinary.uploader.upload(photo_data)
            photo_url = photo['url']
            profile = Profile(user=user, name=name, photo=photo_url)
            profile.save()

        elif(name and not photo_data):
            photo_url = 'http://res.cloudinary.com/gustavolima00/image/upload/v1541203047/sd1gfqk6wqx5eo4hqn2a.png'
            profile = Profile(user=user, name=name, photo=photo_url)
            profile.save()

        else:
            return Response({'error':'Falha na requisição'}, status=HTTP_400_BAD_REQUEST)

        profile_name = profile.get_name()
        profile_photo = profile.get_photo()

        return Response(data={
            'username':username, 
            'name': profile_name, 
            'photo': profile_photo,
            },status=HTTP_200_OK)


@api_view(["POST"])
def update_profile(request):
    #Requests
    jwt_token = request.data.get('jwt_token')
    name = request.data.get('name')
    photo_data = request.data.get('photo')

    try:
        user_json = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        username = user_json['username']
        user = User.objects.get(username = username)
    except:
        return Response({'error':'Usuário não identificado'}, status=HTTP_403_FORBIDDEN)

    try:
        profile = Profile.objects.get(user=user)

    except Profile.DoesNotExist:
        return Response({'error':'Perfil não encontrado'}, status=HTTP_404_NOT_FOUND)

    if(name):
        profile.set_name(name)
    if(photo_data):
        photo = cloudinary.uploader.upload(photo_data)
        photo_url = photo['url']
        profile.set_photo(photo_url)

    profile_name = profile.get_name()
    profile_photo = profile.get_photo()

    return Response(data={
        'username':username, 
        'name': profile_name, 
        'photo': profile_photo,
        },status=HTTP_200_OK)

