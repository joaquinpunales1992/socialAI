from django.db import models
from django.utils import timezone
from croniter import croniter
from datetime import datetime


class MediaContentSource(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class MediaContent(models.Model):
    content_data = models.TextField()
    source = models.ForeignKey(MediaContentSource, related_name='media_contents', on_delete=models.CASCADE, default="")

    def __str__(self):
        return f"Post {self.pk}"

class MediaContentImage(models.Model):
    media_content_id = models.ForeignKey(MediaContent, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media_content_images/')

    def __str__(self):
        return f"Image for Media Content {self.media_content_id}"

class SocialSchedule(models.Model):
    class SocialMedia(models.TextChoices):
        INSTAGRAM = 'instagram', 'Instagram'
        FACEBOOK = 'facebook', 'Facebook'

    class SocialMediaChannel(models.TextChoices):
        REEL = 'reel', 'Reel'
        POST = 'post', 'Post'
        
    social_media = models.CharField(max_length=100, choices=SocialMedia.choices)
    social_media_channel = models.CharField(max_length=100, choices=SocialMediaChannel.choices)
    api_key = models.CharField(max_length=300)
    social_media_id = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100, default="*/15 * * * *")
    source = models.ForeignKey(MediaContentSource, on_delete=models.SET_NULL, null=True, blank=True, default="")
    default_caption = models.CharField(max_length=300, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def is_due(self, now=None):
        return True
        if not now:
            now = timezone.now()

        if not self.schedule:
            return False

        base_time = self.last_run or (now - timezone.timedelta(days=1))
        import pdb;pdb.set_trace()
        try:
            itr = croniter(self.schedule, base_time)
            next_run = itr.get_next(datetime)

            return now >= timezone.make_aware(next_run)
        except Exception as e:
            print(f"Invalid cron expression for schedule ID {self.id}: {self.schedule}")
            return False
        
