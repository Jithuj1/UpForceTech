from .models import CustomUser
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q



@api_view(['GET','POST'])
def UserDetails(request):
    if request.method == "POST":
        email = request.data.get('email')
        email = email.lower()
        try:
            user = CustomUser.objects.get(email = email)
            if user:
                return Response({'message':"Email already taken "})
        except:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = CustomUser.objects.get(email=email)
                serializer = UserReadSerializer(user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'message':'wrong credentials'})
    else:
        user = CustomUser.objects.all()
        serializer = UserReadSerializer(user, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET', 'PUT', 'DELETE'])
def CrudUser(request, id):
    try:
        user = CustomUser.objects.get(id = id)
    except:
        data = {"message":"user not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":     
        serializer = UserReadSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        serializer = UserSerializer(user, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            updated_user = CustomUser.objects.get(id = id)
            serializer = UserReadSerializer(updated_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'invalid input'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        user.delete()
        return Response(status=status.HTTP_200_OK)
    
    
    

class TokenObtainPairViewExtend(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adding custom climes 
        token['id'] = user.id
        token['name'] = user.name
        token['is_admin'] = user.is_admin

        if token:
            return token
        else:
            return Response("False")
        

class MytokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairViewExtend


def extract_jwt_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if auth_header and auth_header.startswith('Bearer '):
        jwt_token = auth_header.split(' ')[1]
        if jwt_token:
            try:
                decoded_token = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                admin = decoded_token.get('is_admin')
                id = decoded_token.get('id')
                return {'id': id, 'admin': admin}
            except jwt.DecodeError:
                pass
    return None


class CustomPagination(PageNumberPagination):
    page_size = 10

@api_view(['GET','POST'])
@authentication_classes([JWTAuthentication])
def NewPost(request):
    print(request.data)
    paginator = CustomPagination()
    if request.method == "POST":
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            serializer = ReadPostSerializer(post)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            msg = {"message":"enter valid credentials"}
            return Response(msg, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        if request.user.is_authenticated:
            result = extract_jwt_token(request)
            user_id = result['id']
            posts = Post.objects.filter(Q(visibility='public') | Q(visibility='private', user_id=user_id))
        else:
            posts = Post.objects.filter(visibility = 'public')
        for post in posts:
            count = Like.objects.filter(post_id = post.id).count()
            post.like_count = count
        paginated_posts= paginator.paginate_queryset(posts, request)
        serializer = ReadPostSerializer(paginated_posts, many = True)
        return paginator.get_paginated_response(serializer.data)
    

@api_view(['GET'])
def GetPost(request, id):
    try:
        post = Post.objects.get(id = id)
    except:
        data = {"message":"post not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if post.visibility !='public':
        msg = {"message":"Post is protected from outsiders"}
        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
    count = Like.objects.filter(post_id = post.id).count()
    post.like_count = count
    serializer = ReadPostSerializer(post)
    return Response(serializer.data, status=status.HTTP_200_OK)
        


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def CrudPost(request, id):
    result = extract_jwt_token(request)
    try:
        post = Post.objects.get(id = id)
        if result['id'] != post.user_id:
            msg = {"message": "updation from outsiders is not acceptable"}
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "PUT":
            serializer = PostSerializer(post, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                updated_post = Post.objects.get(id = id)
                serializer = ReadPostSerializer(updated_post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                data = {'message':'invalid credentials'}
                return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif request.method == "DELETE":
            post.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except:
        data = {"message":"post not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def NewLike(request):
    user_id = request.data.get('user_id', None)
    post_id = request.data.get('post_id', None)
    result = extract_jwt_token(request)
    if result['id'] != user_id:
        msg = {"message": "Login required"}
        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
    serializer = LikeSerializer(data=request.data)
    if serializer.is_valid():
        try:
            like = Like.objects.get(user_id = user_id, post_id = post_id)
            like.delete()
            return Response(status=status.HTTP_200_OK)
        except:
            serializer.save()
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)



# this view is not necessary to work this project because we can perform every operations with the previous view NewLike
# I just created this view because of you have mentioned in the pdf
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def CrudLike(request, id):
    result = extract_jwt_token(request)
    try:
        like = Like.objects.get(id = id)
    except:
        data = {"message":"Not liked"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if result['id'] != like.user_id:
        msg = {"message": "updation from outsiders is not acceptable"}
        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.data.get('user_id', None)
    post_id = request.data.get('post_id', None)
    serializer = UserSerializer(like, data = request.data, partial = True)
    if request.method == "PUT":
        if serializer.is_valid():
            try:
                like = Like.objects.get(user_id = user_id, post_id = post_id)
                like.delete()
                return Response(status=status.HTTP_200_OK)
            except:
                serializer.save()
                return Response(status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            like = Like.objects.get(user_id = user_id, post_id = post_id)
            like.delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)