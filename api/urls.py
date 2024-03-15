from django.urls import path
from . import views


urlpatterns = [
    path('user/', views.UserAPIView.as_view()),
    path('user-relation/', views.UserRelationAPIView.as_view()),
    path('chat/', views.UserAPIView.as_view()),
    path('massage/', views.UserAPIView.as_view()),
    path('following/<int:pk>/', views.following),
    path('follower/<int:pk>/', views.follower),
    #post
    path('post', views.PostView.as_view(), name = 'post-list-create'),
    path('post/<int:id>', views.PostView.as_view(), name = 'update-delete'),
    #post-filter
    path('search', views.filter_post),
    #comment
    path('comment/<int:id>', views.CommentView.as_view()),
    #like
    path('like', views.LikeView.as_view(), name = 'list'),
    path('like/<int:id>', views.LikeView.as_view(), name = 'post-delete-put')
]