from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(BaseModel):
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='courses/%Y/%m')


    def __str__(self):
        return self.subject


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Lesson(BaseModel):
    subject = models.CharField(max_length=255)
    content = models.TextField
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='courses/%Y/%m')
    tags = models.ManyToManyField(Tag)


    def __str__(self):
        return self.subject


class Comment(BaseModel):
    content = models.TextField
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Rating(BaseModel):
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)


    def __str__(self):
        return self.rating
