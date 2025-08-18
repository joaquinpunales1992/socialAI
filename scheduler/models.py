from django.db import models
from django.utils import timezone
from croniter import croniter
from datetime import datetime
from connectors.models import Connector


class MediaContentSource(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MediaContent(models.Model):
    content_data = models.TextField()
    source = models.ForeignKey(
        MediaContentSource,
        related_name="media_contents",
        on_delete=models.CASCADE,
        default="",
    )

    def __str__(self):
        return f"Post {self.pk}"


class MediaContentImage(models.Model):
    media_content_id = models.ForeignKey(
        MediaContent, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="media_content_images/")

    def __str__(self):
        return f"Image for Media Content {self.media_content_id}"

from taggit.managers import TaggableManager


class SocialSchedule(models.Model):
    class SocialMedia(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"

    class SocialMediaChannel(models.TextChoices):
        REEL = "reel", "Reel"
        POST = "post", "Post"

    social_media = models.CharField(max_length=100, choices=SocialMedia.choices, help_text="Social Media Platform")
    social_media_channel = models.CharField(
        max_length=100, choices=SocialMediaChannel.choices, help_text="Channel for the social media. Example: Post, Reel, etc."
    )
    api_key = models.CharField(max_length=300, help_text="API Key for the social media platform")
    social_media_id = models.CharField(max_length=100, help_text="Social Media ID for the account")
    schedule = models.CharField(max_length=100, default="*/15 * * * *", help_text="Cron schedule expression")
    source = models.ForeignKey(
        Connector, on_delete=models.SET_NULL, null=True, blank=True, default="", help_text="Source of the content"
    )

    default_caption = models.CharField(max_length=300, blank=True, help_text="Default caption for the post.")
    use_ai_caption = models.BooleanField(default=True, verbose_name="Use AI Caption", help_text="Use AI to generate caption for the post.")
    hashtags = TaggableManager(blank=True, help_text="List of hashtags to be used in the post.")
    last_run = models.DateTimeField(null=True, blank=True, help_text="Last time the schedule was run.")
    active = models.BooleanField(default=True, help_text="Is the schedule active?")

    def __str__(self):
        return f"{self.social_media} - {self.social_media_channel} - {self.source}"

    def get_hashtags(self):
        return [hashtag for hashtag in self.hashtags.names()]
    
    def is_due(self, now=None):
        if not now:
            now = timezone.now()

        if not self.schedule:
            return False

        base_time = self.last_run or (now - timezone.timedelta(days=1))
        
        try:
            itr = croniter(self.schedule, base_time)
            next_run = itr.get_next(datetime)

            # Check if next_run is timezone-aware
            if timezone.is_aware(next_run):
                return now >= next_run
            else:
                return now >= timezone.make_aware(next_run)
        except Exception as e:
            print(f"Invalid cron expression for schedule ID {self.id}: {self.schedule}")
            return False
