from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes

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
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, *args, **kwargs):
        try:
            user = request.user
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class UserRelationAPIView(APIView):

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


    def post(self, request, *args, **kwargs):
        try:
            from_user = request.user
            to_user = request.data['to_user']
            models.UserReletion.objects.create(from_user=from_user, to_user=to_user)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            to_user = models.User.objects.get(pk=pk)
            reletion = models.UserReletion.objects.get(
                from_user=request.user,
                to_user = to_user
                )
            reletion.delete()
            return Response(status=status.HTTP_200_OK)
        except models.UserReletion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    
class ChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        user = request.user
        chats = models.Chat.objects.filter(users=user)
        chats_ser = serializers.ChatListSerializer(chats)
        return Response(chats_ser.data)
        # try:
        #     instance = models.Chat.objects.get(pk=pk)
        # except models.Chat.DoesNotExist:
        #     return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        # serializer = serializers.ChatSerializer(instance)
        # return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        try:
            chat = models.Chat.objects.get(pk=pk)
        except models.Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class MassageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.MassageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        try:
            massage = models.Message.objects.get(pk=pk)
            assert massage.author == request.user
        except models.Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.MassageSerializer(massage, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            massage = models.Message.objects.get(pk=pk)
            assert massage.author == request.user
        except models.Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        massage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view
def following(request, pk):
    user = models.User.objects.get(pk=pk)
    user_reletion = models.UserReletion.objects.filter(from_user=user)
    serializer_data = serializers.FollowingSerializer(user_reletion, many=True)
    return serializer_data.data

@api_view
def follower(request, pk):
    user = models.User.objects.get(pk=pk)
    user_reletion = models.UserReletion.objects.filter(to_user=user)
    serializer_data = serializers.FollowerSerializer(user_reletion, many=True)
    return serializer_data.data



class PostView(APIView):
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
    
    def put(self, request, id, *args, **kwargs):
        post = models.Post.objects.filter(author = request.user).get(id = id)
        if request.data['title']:
            post.title = request.data['title']
        if request.data['body']:
            post.title = request.data['body']
        post.save()
        post_ser = serializers.PostSerializer(post)
        return Response(post_ser.data)
    
    def delete(self, request, id, *args, **kwargs):
        post = models.Post.objects.filter(author = request.user).get(id = id)
        post.delete()
        return Response({'success':'post has been deleted'})
    

#filtering posts
@api_view(['GET'])
def filter_post(request):
    search = request.data['search']
    posts = models.Post.objects.filter(Q(title__icontains = search) | Q(body__icontains = search))
    posts_ser = serializers.PostSerializer(posts, many = True)
    return Response (posts_ser.data)



class CommentView(APIView):
    def get(self, request, id, *args, **kwargs): #id => post_id
        post = models.Post.objects.get(id = id)
        comments = models.Comment.objects.filter(post = post).order_by('-date')
        comments_ser = serializers.CommentSerializer(comments, many = True)
        return Response(comments_ser.data)
    
    def post(self, request, id, *args, **kwargs): #id => post_id
        post = models.Post.objects.get(id = id)
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
    
    def put(self, request, id, *args, **kwargs): # id => comment_id
        try:
            comment = models.Comment.objects.filter(author = request.user).get(id = id)
            comment.text = request.data['text']
            comment.save()
            comment_ser = serializers.CommentSerializer(comment)
            return Response({'succes': 'change has been saved', 'comment': comment_ser.data})
        except:
            return Response({'fatal': f'no comment with id {id}'})
    
    def delete(self, request, id, *args, **kwargs):
        comment = models.Comment.objects.filter(author = request.user).get(id = id)
        comment.delete()
        return Response({'success':'comment has been deleted'})


class LikeView(APIView):
    def get(self, request, *args, **kwargs):
        reactions = models.Like.objects.filter(author = request.user).order_by('status')
        reactions_ser = serializers.LikeSerializer(reactions, many = True)
        return Response({'all reactions you gave' : reactions_ser.data})
    
    def post(self, request, id, *args, **kwargs):
        try:
            post = models.Post.objects.get(id = id)
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
            return Response({'fatal': f'no post with id {id}'})
    
    def put(self, request, id, *args, **kwargs):
        try:
            post = models.Post.objects.get(id = id)
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
            return Response({'fatal': f'no post with id {id}'})
    
    def delete(self, request, id, *args, **kwargs):
        try:
            post = models.Post.objects.get(id = id)
            emotion = models.Like.objects.filter(author = request.user).get(post = post)
            emotion.delete()
            return Response({'success':'emotion has been deleted'})
        except:
            return Response({'fatal': f'no post with id {id}'})
