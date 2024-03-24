from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from courses.models import Category, Course, Lesson, User, Comment, Like
from courses import serializers, paginators, permissions as perms


"""
GET /categories/
"""


class CategoryViewset(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


"""
GET /courses/
"""


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginators.CoursePaginator
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.action == "list":
            q = self.request.query_params.get("q")
            if q:
                self.queryset = self.queryset.filter(subject__icontains=q)

            cate_id = self.request.query_params.get("category_id")
            if cate_id:
                self.queryset = self.queryset.filter(category_id=cate_id)

        return self.queryset

    def get_permissions(self):
        if self.action == "lessons":
            if self.request.method == "POST":
                return [permissions.IsAuthenticated()]
        return super().get_permissions()

    """
    GET, POST /courses/<course_id>/lessons/
    """

    @action(methods=["get", "post"], url_path="lessons", detail=True)
    def lessons(self, request, pk):
        if request.method == "GET":
            return self.get_lessons(request)
        else:
            return self.post_lesson(request)

    def get_lessons(self, request):
        lessons = self.get_object().lesson_set.filter(active=True)

        q = request.query_params.get("q")
        if q:
            lessons = lessons.filter(subject__icontains=q)

        return Response(
            serializers.LessonSerializer(lessons, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post_lesson(self, request):
        lesson = Lesson.objects.create(
            subject=request.data.get("subject"),
            content=request.data.get("content"),
            course=self.get_object(),
            image=request.data.get("image"),
            tags=request.data.get("tags"),
        )
        return Response(
            serializers.LessonDetailsSerializer(lesson).data, status=status.HTTP_201_OK
        )


"""
GET /lessons/<lesson_id>/
"""


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.prefetch_related("tags").filter(active=True)
    serializer_class = serializers.LessonDetailsSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action == "comments":
            if self.request.method == "GET":
                return super().get_permissions()
            return [permissions.IsAuthenticated()]
        if self.action in ["like"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    """
    GET, POST /lessons/<lesson_id>/comments/
    """

    @action(methods=["get", "post"], url_path="comments", detail=True)
    def comments(self, request, pk):
        if request.method == "GET":
            return self.get_comments()
        else:
            return self.post_comment(request)

    def get_comments(self):
        comments = self.get_object().comment_set.select_related("user").all()

        return Response(
            serializers.CommentSerializer(comments, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post_comment(self, request):
        comment = Comment.objects.create(
            user=request.user,
            lesson=self.get_object(),
            content=request.data.get("content"),
        )

        return Response(
            serializers.CommentSerializer(comment).data, status=status.HTTP_201_CREATED
        )

    """
    POST /lessons/<lesson_id>/like/ 
    """

    @action(methods=["post"], detail=True, url_path="like")
    def like(self, request, pk):
        like, created = Like.objects.get_or_create(
            user=request.user, lesson=self.get_object()
        )
        if created:
            like.active = True
        else:
            if request.user != like.user:
                return Response(status=status.HTTP_403)
            like.active = not like.active
        like.save()

        return Response(
            serializers.LessonDetailsSerializer(
                self.get_object(), context={"request": request}
            ).data,
            status=status.HTTP_200_OK,
        )


"""
POST /users/
"""


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [
        parsers.MultiPartParser,
    ]

    def get_permissions(self):
        if self.action.__eq__("current_user"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    """
    GET /users/current-user/
    """

    @action(methods=["get"], url_path="current-user", detail=False)
    def current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)


"""
DELETE /comments/<comment_id>/
"""


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.AuthorOrReadOnly]
