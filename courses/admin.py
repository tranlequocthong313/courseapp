from django.contrib import admin
from django.apps import apps
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from cloudinary.forms import CloudinaryFileField

from courses.models import *


class MyModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ['css/style.css']
        }


class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    image = CloudinaryFileField()

    class Meta:
        model = Course
        fields = '__all__'


class CourseAdmin(MyModelAdmin):
    list_display = ['id', 'subject', 'description']
    readonly_fields = ['preview_image']
    form = CourseForm

    def preview_image(self, course):
        return mark_safe(f'<img width="200" src="{course.image.url}" />')


class TagInline(admin.TabularInline):
    model = Lesson.tags.through


class LessonForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)
    image = CloudinaryFileField()

    class Meta:
        model = Lesson
        fields = '__all__'


class LessonAdmin(MyModelAdmin):
    list_display = ['id', 'subject', 'created_date', 'course_id']
    list_filter = ['subject', 'created_date']
    search_fields = ['subject', 'course']
    inlines = [TagInline]
    form = LessonForm


admin_sites = {
    'course': CourseAdmin,
    'lesson': LessonAdmin
}

course_app = apps.get_app_config('courses')

for model_name, model in course_app.models.items():
    admin.site.register(model, admin_sites.get(model_name, MyModelAdmin))
