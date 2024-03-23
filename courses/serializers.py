from courses.models import Category, Course, Lesson, Tag, Comment, User, Like
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = instance.image.url

        return rep


class CourseSerializer(ItemSerializer):
    class Meta:
        model = Course
        fields = ["id", "subject", "image", "created_date"]


class LessonSerializer(ItemSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "subject", "image", "created_date"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "avatar",
        ]
        extra_kwargs = {"password": {"write_only": "true"}}


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    lesson = LessonSerializer()

    class Meta:
        model = Like
        fields = ["id", "user", "lesson", "active"]


class LessonDetailsSerializer(LessonSerializer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, lesson):
        request = self.context.get("request")
        if request.user.is_authenticated:
            return lesson.like_set.filter(active=True, user=request.user).exists()

    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ["liked"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ["id", "content", "created_date", "user"]
