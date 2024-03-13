from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication , SessionAuthentication
from main import models
from django.db.models import Q
from . import serializers


from django.contrib.auth import login, authenticate 

# class MyModelView(ModelViewSet):
#     queryset = models.MyModel.objects.all() 
#     serializer_class = serializers.MyModelSerializer


#     def get_queryset(self):
#         queryset = models.MyModel.objects.all()
#         return queryset
 


@api_view(['POST'])
def create_user(request):
    username = request.data["username"]
    password = request.data["password"]
    email = request.data['email']
    first_name = request.data["first_name"]
    new_user = models.User.objects.create_user(
        username = username,
        password = password,
        email = email,
        first_name = first_name,
    )
    new_user_ser = serializers.UserSerialezer(new_user)
    return Response({'detail': 'user has been created', 'user': new_user_ser.data})
    

@api_view(['POST'])
def update_user(request):
    #for checking
    username = request.data.get('username')
    password = request.data.get('password')
    #for changing
    change_username = request.data.get('change_username')
    change_password = request.data.get('change_password')
    change_email = request.data.get('change_email')
    change_first_name = request.data.get('change_first_name')
    if authenticate(username = username, password = password) is not None:
        user = models.User.objects.get(username = username)
        if change_username:
            user.username = username
        if change_password:
            user.set_password(change_password)
        if change_first_name:
            user.first_name = change_first_name
        if change_email:
            user.email = change_email
        user.save()
        user_ser = serializers.UserSerialezer(user)
        return Response({'detail':'user has been changed', 'user': user_ser.data})


@api_view(['POST'])
def delete_user(request):
    username = request.data['username']
    password = request.data['password']
    if authenticate(username = username, password = password) is not None:
        user = models.User.objects.get(username = username)
        user.delete()
        return Response({'detail': f'user {username} has been deleted'})
    

@api_view(['GET'])
def list_users(request):
    """gets list of usernames that starts with given string for example ali->[ alisher, alijon, alimardon]"""
    username = request.data['username']
    filtered = models.User.objects.filter(username__startswith = username)
    if not filtered.exists():
        return Response({'detail':'not found'}, status=404)
    user_ser = serializers.UserSerialezer(filtered, many = True)
    return Response(user_ser.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_relation(request, id):
    user = models.User.objects.get(id = id)
    if request.user != user:
        if models.User.objects.filter(username = user).first():
            to_username = models.User.objects.get(username = user)
            if not models.UserReletion.objects.filter(from_user = request.user, to_user = to_username).first():
                relation = models.UserReletion.objects.create(
                    from_user = request.user,
                    to_user = to_username
                )
                relation_ser = serializers.UserRelationSerializer(relation)
                return Response({'detail': 'relation has been created', 'relation' : relation_ser.data})
            else:
                return Response({'detail': 'already created relation'})
        else:
            return Response({'detail': 'username does not exist'})
    

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_relation(request, id):
    to_user = models.User.objects.get(id = id)
    if models.UserReletion.objects.filter(from_user = request.user, to_user = to_user).first():
        models.UserReletion.objects.get(from_user = request.user, to_user = to_user).delete()
        return Response({'detail': 'relation has been deleted'})
    else:
        return Response({'detail': f'You dont have relation with "{to_user.username}"'})
    

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_chat(request, id):
    user = models.User.objects.get(id = id)
    if not models.Chat.objects.filter(users=request.user).filter(users=user).first():
        chat = models.Chat.objects.create(
        )
        chat.users.add(request.user, user)
        chat.save()
        return Response({'success':'chat has been created'})
    else:
        return Response({'detail': 'chat was created before'})
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_chat(request, id):
    try:
        chat = models.Chat.objects.filter(users = request.user).filter(id = id)
        chat.delete()
        return Response({'success':'chat has been deleted'})
    except:
        return Response({'detail':'chat does not exist'})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def chat_detail(request, id):
    chat = models.Chat.objects.get(id = id, users = request.user)
    chat_ser = serializers.ChatSerializer(chat)
    return Response(chat_ser.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_message(request, id):
    chat = models.Chat.objects.get(id = id, users = request.user)
    body = request.data['body']
    file = request.FILES.get('file')
    if not file:
        message = models.Message.objects.create(
            author = request.user,
            chat = chat,
            body = body,
        )
    else:
        message = models.Message.objects.create(
            author = request.user,
            chat = chat,
            body = body,
            file = file
        )
    message_ser = serializers.MessageSerializer(message)
    return Response(message_ser.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def update_message(request, id):
    body = request.data['body']
    file = request.FILES.get('file')
    message = models.Message.objects.get(id = id, author = request.user)
    if not file:
        message.body = body
        message.save()
    else:
        message.body = body
        message.file = file
        message.save()
    message_ser = serializers.MessageSerializer(message)
    return Response({'success': 'update has been saved', 'message':message_ser.data})


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_message(request, id):
    message = models.Message.objects.get(id = id, author = request.user)
    message.delete()
    return Response({'detail': 'message has been deleted'})