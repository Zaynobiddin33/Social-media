from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes
from django.contrib.auth import authenticate

from main import models
from . import serializers


class UserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        # way 1
        users = models.User.objects.all()
        if q:
            users.filter(
                Q(username__icontains=q)| 
                Q(first_name__iconatins=q)| 
                Q(last_name__iconatins=q)|
                Q(email__icontains=q)
                )
        # way 2
        # if q:
        #     users = models.User.objects.filter(
        #         Q(username__icontains=q)| 
        #         Q(first_name__iconatins=q)| 
        #         Q(last_name__iconatins=q)|
        #         Q(email__icontains=q)
        #     )
        # else:
        #     users = models.User.objects.all()

        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        try:
            models.User.objects.get(username = username)
            return Response({'error':'username is taken'})
        except:
            models.User.objects.create_user(
                username = username,
                password = password,
            )
        return Response({'success':'created'})
    
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def put(self, request, *args, **kwargs):
        try:
            user = request.user
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def delete(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username = username, password = password)
        if user == request.user:
            user.delete()
        return Response({'success':'user has been deleted'})
    
    
class UserRelationAPIView(APIView):

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def get(self, request, *args, **kwargs):
        user = request.user
        following = models.UserReletion.objects.filter(from_user=user)
        follower = models.UserReletion.objects.filter(to_user=user)
        following_ser = serializers.FollowingSerializer(following, many=True)
        follower_ser = serializers.FollowerSerializer(follower, many=True)
        data = {
            'following':following_ser.data,
            'follower':follower_ser.data,
        }
        return Response(data)


    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def post(self, request, code, *args, **kwargs):
            from_user = request.user
            data = models.UserReletion.objects.create(from_user=from_user, to_user=models.User.objects.get(code = code))
            data_ser = serializers.UserRealtionSerializer(data)
            return Response({'success':'created', 'relation': data_ser.data})


    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def delete(self, request, code, *args, **kwargs):
            to_user = models.User.objects.get(code=code)
            reletion = models.UserReletion.objects.get(
                from_user=request.user,
                to_user = to_user
                )
            reletion.delete()
            return Response({"success":'deleted relation'})
    
    
class ChatAPIView(APIView):
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def post(self, request, code, *args, **kwargs):
        user2 = models.User.objects.get(code = code)
        chat = models.Chat.objects.create()
        
        models.ChatUser.objects.create(
            chat = chat,
            user = user2
        )
        models.ChatUser.objects.create(
            chat = chat,
            user = request.user
        )
        return Response({'success':'chat created successfully'})
    
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def get(self, request, code=None, format=None):
        data = []
        chats = models.ChatUser.objects.filter(user = request.user)
        for chat_user in chats:
            user_chat = models.ChatUser.objects.exclude(user = request.user).get(chat = chat_user.chat).user.id
            user = models.User.objects.get(id = user_chat)
            ser_user = serializers.UserSerializer(user).data
            data.append(ser_user)
        return Response(data)
    
        # try:
        #     instance = models.Chat.objects.get(pk=pk)
        # except models.Chat.DoesNotExist:
        #     return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        # serializer = serializers.ChatSerializer(instance)
        # return Response(serializer.data)

    def delete(self, request, code, *args, **kwargs):
        try:
            chat = models.Chat.objects.get(code=code)
        except models.Chat.DoesNotExist:
            return Response({'fatal': 'no chat with that code'})
        data  = models.ChatUser.objects.filter(chat = chat)
        for i in data:
            i.delete()
        return Response({'succes':"chat has been deleted"})
    
    
class MassageAPIView(APIView):
    def get(self, request, code, *args, **kwargs):
        chat = models.Chat.objects.get(code = code)
        try:
            models.ChatUser.objects.get(chat = chat, user = request.user)
            messages  = models.Message.objects.filter(chat = chat).order_by('-date')
            message_ser = serializers.MassageSerializer(messages, many = True)
            return Response(message_ser.data)
        except:
            return Response({'fatal': 'chat does not exist or you cannot access this chat'})
            
    def post(self, request, code,  *args, **kwargs):
        file = request.FILES.get('file')
        body = request.data['body']
        chat = models.Chat.objects.get(code = code)
        models.ChatUser.objects.get(chat = chat, user = request.user)
        message = models.Message.objects.create(
            author = request.user,
            body = body,
            file = file,
            chat = chat
        )
        message_ser = serializers.MassageSerializer(message)
        return Response({'success':'created message', 'message': message_ser.data})

    def put(self, request, code, *args, **kwargs):
        body = request.data['body']
        try:
            message = models.Message.objects.get(code = code, author = request.user)
            message.body = body
            message.save()
            message_ser = serializers.MassageSerializer(message)
            return Response({'success':'changed', 'message' : message_ser.data})
        except:
            return Response({'fatal':'message not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, code, *args, **kwargs):
        try:
            message = models.Message.objects.get(code = code, author = request.user)
            message.delete()
            return Response({'success':'deleted'})
        except:
            return Response({'fatal':'message not found or you are not authenticated'}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def following(request, code):
    user = models.User.objects.get(code=code)
    user_reletion = models.UserReletion.objects.filter(from_user=user)
    serializer_data = serializers.FollowingSerializer(user_reletion, many=True)
    return Response (serializer_data.data)

@api_view(["GET"])
def follower(request, code):
    user = models.User.objects.get(code=code)
    user_reletion = models.UserReletion.objects.filter(to_user=user)
    serializer_data = serializers.FollowerSerializer(user_reletion, many=True)
    return Response (serializer_data.data)


#HOMEWORK

class PostView(APIView):
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def get(self, request, *args, **kwarg):
        posts = models.Post.objects.filter(author = request.user)
        posts_ser = serializers.PostSerializer(posts, many = True)
        return Response(posts_ser.data)
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def post(self, request, *args, **kwargs):
        """creates post first, and after that Postfiles are created.
          Postfiles can be created up to 10 files for 1 post"""
        author = request.user
        title = request.data['title']
        body = request.data['body']
        files = []
        for i in range(1,11):
            data = f'file{i}'
            if data in request.FILES:
                files.append(request.FILES[data])
        post = models.Post.objects.create(
            author = author,
            title = title,
            body = body,
        )
        for i in files:
                models.PostFiles.objects.create(
                    post = post,
                    file = i
                )
        post_ser = serializers.PostSerializer(post)
        return Response(post_ser.data)
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def put(self, request, code, *args, **kwargs):
        post = models.Post.objects.filter(author = request.user).get(code = code)
        if request.data.get('title'):
            post.title = request.data.get('title')
        if request.data.get('body'):
            post.body = request.data.get('body')
        post.save()
        post_ser = serializers.PostSerializer(post)
        return Response(post_ser.data)
    

    def delete(self, request, code, *args, **kwargs):
        post = models.Post.objects.filter(author = request.user).get(code = code)
        post.delete()
        return Response({'success':'post has been deleted'})
    


#filtering posts
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def filter_post(request):
    search = request.data['search']
    posts = models.Post.objects.filter(author = request.user).filter(Q(title__icontains = search) | Q(body__icontains = search))
    posts_ser = serializers.PostSerializer(posts, many = True)
    return Response (posts_ser.data)



class CommentView(APIView):
    def get(self, request, code, *args, **kwargs): #code => post_code
        post = models.Post.objects.get(code = code)
        comments = models.Comment.objects.filter(post = post).order_by('-date')
        comments_ser = serializers.CommentSerializer(comments, many = True)
        return Response(comments_ser.data)
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def post(self, request, code, *args, **kwargs): #code => post_code
        post = models.Post.objects.get(code = code)
        text = request.data['text']
        if request.data.get('reply'):
            reply = models.Comment.objects.get(id = request['reply_id'])
            comment = models.Comment.objects.create(
                author = request.user,
                post = post,
                text = text,
                reply = reply
            )
        else:
            comment = models.Comment.objects.create(
                author = request.user,
                post = post,
                text = text,
            )
        comment_ser = serializers.CommentSerializer(comment)
        return Response({'success':'created', 'comment':comment_ser.data})
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def put(self, request, code, *args, **kwargs): # code => comment_code
        try:
            comment = models.Comment.objects.filter(author = request.user).get(code = code)
            comment.text = request.data['text']
            comment.save()
            comment_ser = serializers.CommentSerializer(comment)
            return Response({'succes': 'change has been saved', 'comment': comment_ser.data})
        except:
            return Response({'fatal': f'no comment with code {code}'})
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def delete(self, request, code, *args, **kwargs):
        comment = models.Comment.objects.filter(author = request.user).get(code = code)
        comment.delete()
        return Response({'success':'comment has been deleted'})



class LikeView(APIView):
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def get(self, request, *args, **kwargs):
        reactions = models.Like.objects.filter(author = request.user).order_by('status')
        reactions_ser = serializers.LikeSerializer(reactions, many = True)
        return Response({'all reactions you gave' : reactions_ser.data})
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def post(self, request, code, *args, **kwargs):
        try:
            post = models.Post.objects.get(code = code)
            status = request.data['status']
            if status.lower() == 'true':
                reaction = True
            elif status.lower() == 'false':
                reaction = False
            else: 
                return Response({"error": "you didn't give a boolean for the status"})
            data = models.Like.objects.create(
                author = request.user,
                post = post,
                status = reaction,
            )
            like_ser = serializers.LikeSerializer(data)
            return Response({'success': 'created emotion', 'emotion':like_ser.data})
        except:
            return Response({'fatal': f'no post with code {code}'})
    

    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def put(self, request, code, *args, **kwargs):
        try:
            post = models.Post.objects.get(code = code)
            emotion = models.Like.objects.filter(author = request.user).get(post = post)
            status = request.data['status']
            if status.lower() == 'true':
                reaction = True
            elif status.lower() == 'false':
                reaction = False
            emotion.status = reaction
            emotion.save()
            emotion_ser = serializers.LikeSerializer(emotion)
            return Response({'success':'change has been saved', 'updated_to': emotion_ser.data})
        except:
            return Response({'fatal': f'no post with code {code}'})
    
    
    @authentication_classes([SessionAuthentication, BasicAuthentication])
    def delete(self, request, code, *args, **kwargs):
        try:
            post = models.Post.objects.get(code = code)
            emotion = models.Like.objects.filter(author = request.user).get(post = post)
            emotion.delete()
            return Response({'success':'emotion has been deleted'})
        except:
            return Response({'fatal': f'no post with code {code}'})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def user_posts(request, code):
    user = models.User.objects.get(code=code)
    posts = models.Post.objects.filter(author=user).order_by('-date')
    serializer_data = serializers.PostSerializer(posts, many=True)
    return Response(serializer_data.data)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def following_posts(request):

    models.UserReletion.objects.filter(from_user=request.user)
    posts = []

    for user in  models.UserReletion.objects.filter(from_user=request.user):
        # posts.extend(models.Post.objects.filter(author=user.to_user))
        posts.append(models.Post.objects.filter(author=user.to_user).order_by('date').last())

    posts.sort(key= lambda x:x.date, reverse=True)
    serializer_data = serializers.PostSerializer(data=posts, many=True)
    serializer_data.is_valid()

    return Response(serializer_data.data)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def post_detail(request, code):
    post = models.Post.objects.get(code=code)
    comment = models.Comment.objects.filter(post=post)
    post_serializer = serializers.PostSerializer(post).data
    comment_serializer = serializers.CommentSerializer(comment, many=True).data
    return Response({'post':post_serializer, 'comment':comment_serializer})