from rest_framework.serializers import ModelSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication


from main import models

class UserSerialezer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'email']

class UserRelationSerializer(ModelSerializer):
    class Meta:
        model = models.UserReletion
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    class Meta:
        model = models.Message
        fields = '__all__'

class ChatSerializer(ModelSerializer):
    messages = MessageSerializer(many = True, read_only = True)
    class Meta:
        model = models.Chat
        fields = ['users','messages']

class PostSerializer(ModelSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'

class PostFilesSerializer(ModelSerializer):
    class Meta:
        model = models.PostFiles
        fields = '__all__'

class UserRelationSerializer(ModelSerializer):
    class Meta:
        model = models.UserReletion
        fields = '__all__'

class CommentSerialzer(ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

class LikeSerialzer(ModelSerializer):
    class Meta:
        model = models.Like
        fields = '__all__'