from django.contrib import admin
from connectors.models import (
    ManualConnector,
    ManualConnectorImage,
    ScraperConnector,
    ScrappedItem,
    SocialPost,
)
from scheduler.models import SocialSchedule


class ManualConnectorImageAdmin(admin.StackedInline):
    model = ManualConnectorImage


@admin.register(ManualConnector)
class ManualConnectorAdmin(admin.ModelAdmin):
    inlines = [ManualConnectorImageAdmin]
    list_display = ("name",)


@admin.register(ScraperConnector)
class ScraperConnectorAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(SocialSchedule)
class SocialScheduleAdmin(admin.ModelAdmin):
    list_display = ("social_media", "social_media_channel", "source")
    list_filter = ("social_media",)
    readonly_fields = [
        "last_run",
    ]


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "scrapped_item",
        "datetime",
    )
    list_filter = ("scrapped_item", "datetime")


@admin.register(ScrappedItem)
class ScrappedItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "connector",
    )
    list_filter = ("connector",)
    readonly_fields = [
        "connector",
    ]
