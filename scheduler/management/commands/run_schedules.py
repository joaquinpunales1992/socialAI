from django.core.management.base import BaseCommand
import requests
from django.utils import timezone
from scheduler.models import SocialSchedule  


PUBLISH_FACEBOOK_POST_ENDPOINT = "https://social-ai-s1kk.onrender.com/publish-facebook-post/"
DOMAIN = "http://127.0.0.1:8000"

class Command(BaseCommand):
    help = 'Run due scheduled social media posts using cron schedule.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        schedules = SocialSchedule.objects.all()

        for schedule in schedules:
            if not schedule.is_due(now):
                self.stdout.write(f"Skipping {schedule.id}: Not due yet.")
                continue

            social_media = schedule.social_media.lower()
            channel = schedule.social_media_channel.lower()

            self.stdout.write(f"Running: {social_media} - {channel}")

            try:
                if social_media == 'instagram' and channel == 'reel':
                    pass
                if social_media == 'instagram' and channel == 'post':
                    pass
                elif social_media == 'facebook' and channel == 'reel':
                    pass
                elif social_media == 'facebook' and channel == 'post':

                    media_content = schedule.source.media_contents.first()

                    content_data = media_content.content_data
                    schedule_api_token = schedule.api_key
                    schedule_social_media_id = schedule.social_media_id 
                    schedule_default_caption = schedule.default_caption

                    image_urls = [f"{DOMAIN}/{media_content.image.url}" for media_content in media_content.images.all()]
                    
                    image_urls = ["https://image2.homes.jp/smallimg/image.php?file=http://img.homes.jp/104867/sale/7139/2/1/vsee.jpg&width=600&height=600", "https://image3.homes.jp/smallimg/image.php?file=http%3A%2F%2Fimg.homes.jp%2F147319%2Fsale%2F1578%2F2%2F7%2Fufr8.jpg&width=600&height=600"]
                    hashtags = ["#japan", "#cheaphomes"]

                    json = {
                        "content_data": content_data,
                        "image_urls": image_urls,
                        "hashtags": hashtags,
                        "default_caption": schedule_default_caption,
                        "last_caption_generated": "string",
                        "facebook_page_id": schedule_social_media_id,
                        "meta_api_key": schedule_api_token,
                        "use_ai_caption": True,
                        "internet_images": True
                        }
                    response = requests.post(url=PUBLISH_FACEBOOK_POST_ENDPOINT, json=json)
                else:
                    self.stdout.write(self.style.WARNING(f"Unknown combo: {social_media} - {channel}"))
                    continue

                # Mark as run
                schedule.last_run = now
                schedule.save()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error on {schedule.id}: {str(e)}"))