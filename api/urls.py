from django.urls import path, include
from rest_framework import routers
from . import views


# router = routers.DefaultRouter()
# router.register(r'my-model', views.MyModelView, basename='MyModel')


# urlpatterns = [
#     path('router/', include(router.urls)),
#     path('auth/', include('rest_framework.urls')),
#     path('', views.list_data)
# ]


urlpatterns = [
    #CRUD user
    path('create-user', views.create_user),
    path('update-user', views.update_user),
    path('delete-user', views.delete_user),
    path('list-user', views.list_users),

    #Relation
    path('create-relation/<int:id>', views.create_relation), #id -> user_id
    path('delete-relation/<int:id>', views.delete_relation), #id -> user_id

    #chat
    path('create-chat/<int:id>', views.create_chat), #id -> user_id
    path('delete-chat/<int:id>', views.delete_chat), #id -> chat_id
    path('chat-detail/<int:id>', views.chat_detail), #id -> chat_id

    #message
    path('create-message/<int:id>', views.create_message), #id -> chat_id
    path('update-message/<int:id>', views.update_message), #id -> message_id
    path('delete-message/<int:id>', views.delete_message), #id -> message_id

]