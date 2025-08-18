from django.contrib import admin
from django.db import models
from django.forms import Textarea
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
    list_display = ("name", "base_url", )


@admin.register(SocialSchedule)
class SocialScheduleAdmin(admin.ModelAdmin):
    list_display = ("active", "social_media", "social_media_channel", "source")
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
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'class': 'vLargeTextField',  # Django's built-in large text field class
                'rows': 15,
                'style': 'font-family: Monaco, "Courier New", monospace; font-size: 12px;'})},
    }
    list_display = (
        "id",
        "connector",
    )
    list_filter = ("connector",)
    readonly_fields = [
        "connector",
    ]
