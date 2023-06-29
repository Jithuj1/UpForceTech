from django.urls import path
from .views import *
from rest_framework_simplejwt.views import(TokenRefreshView)


urlpatterns = [
    path('users', UserDetails),
    path('users/<int:id>', CrudUser),
    path('api/token/', MytokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('post', NewPost),
    path('post/<int:id>', GetPost),
    path('update_post/<int:id>', CrudPost),
    path('like', NewLike),
    path('like/<int:id>', CrudLike),
]
