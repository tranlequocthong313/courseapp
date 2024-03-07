from django.contrib import admin
from django.apps import apps
from django.utils.html import mark_safe

from courses.models import *

# Register your models here.

class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'description']
    readonly_fields = ['preview_image']

    def preview_image(self, course):
        print(course.image.name)
        return mark_safe(f'<img width="200" src="/static/{course.image.name}" />')


class TagInline(admin.TabularInline):
    model = Lesson.tags.through


class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'created_date', 'course_id']
    list_filter = ['subject', 'created_date']
    search_fields = ['subject', 'course']
    inlines = [TagInline]


admin_sites = {
    'course': CourseAdmin,
    'lesson': LessonAdmin
}

course_app = apps.get_app_config('courses')

for model_name, model in course_app.models.items():
    admin.site.register(model, admin_sites.get(model_name, admin.ModelAdmin))
