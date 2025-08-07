import nested_admin
from django.contrib import admin
from scheduler.models import SocialSchedule, MediaContentSource,  MediaContent, MediaContentImage


class SocialScheduleAdmin(admin.ModelAdmin):
    list_display = ('social_media', 'social_media_channel', 'schedule', 'last_run')


class MediaContentImageInline(nested_admin.NestedTabularInline):
    model = MediaContentImage
    extra = 1


class MediaContentInline(nested_admin.NestedStackedInline):
    model = MediaContent
    inlines = [MediaContentImageInline]
    extra = 1


@admin.register(MediaContentSource)
class MediaContentSourceAdmin(nested_admin.NestedModelAdmin):
    inlines = [MediaContentInline]
    list_display = ('id', 'name')

admin.site.register(SocialSchedule, SocialScheduleAdmin)