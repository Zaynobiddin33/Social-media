from django.urls import path
from . import views


urlpatterns = [
    path('user/', views.UserAPIView.as_view()),
    path('user-relation/', views.UserRelationAPIView.as_view(), name = 'list'),
    path('user-relation/<str:code>', views.UserRelationAPIView.as_view(), name = 'delete-post'),
    path('chat/', views.ChatAPIView.as_view(), name = 'list-delete-put'),
    path('chat/<str:code>', views.ChatAPIView.as_view(), name = 'post'),
    path('message/<str:code>', views.MassageAPIView.as_view()),
    path('following/<str:code>/', views.following),
    path('follower/<str:code>/', views.follower),
    #post
    path('post', views.PostView.as_view(), name = 'post-list-create'),
    path('post/<str:code>', views.PostView.as_view(), name = 'update-delete'),
    #post-filter
    path('search', views.filter_post),
    #comment
    path('comment/<str:code>', views.CommentView.as_view()),
    #like
    path('like', views.LikeView.as_view(), name = 'list'),
    path('like/<str:code>', views.LikeView.as_view(), name = 'post-delete-put'),
    path('user-posts/<str:code>', views.user_posts),
    path('following-posts', views.following_posts),
    path('post-detail/<str:code>', views.post_detail),
    
    path('following/<str:code>', views.following),
    path('follower/<str:code>', views.follower),

]